import argparse
import calendar
import datetime
import os
import sys
import time
import traceback
from importlib import metadata
from pathlib import Path
from typing import List

from stack_overflow_watchman.clients.stack_overflow_wrapper import StackOverflowEnterpriseAPI
from stack_overflow_watchman.exceptions import MissingEnvVarError
from stack_overflow_watchman.loggers import JSONLogger, StdoutLogger, export_csv
from stack_overflow_watchman.models.signature import Signature, load_from_yaml
from stack_overflow_watchman.signature_updater import SignatureUpdater
from stack_overflow_watchman.stack_overflow_search import (
    query_stackoverflow_excerpts
)

SIGNATURES_PATH = (Path(__file__).parents[2] / 'watchman-signatures').resolve()
OutputLogger = JSONLogger


def init_logger(logging_type: str, debug: bool) -> JSONLogger or StdoutLogger:
    """ Create a logger object. Defaults to stdout if no option is given

    Args:
        logging_type: Type of logging to use
        debug: Whether to use debug level logging or not
    Returns:
        JSONLogger or StdoutLogger
    """

    if not logging_type or logging_type == 'stdout':
        return StdoutLogger(debug=debug)
    return JSONLogger(debug=debug)


def load_signatures() -> List[Signature]:
    """ Load signatures from YAML files
    Returns:
        List[Signature] -- List of signatures loaded from YAML files
    """

    loaded_signatures = []
    try:
        for root, dirs, files in os.walk(SIGNATURES_PATH):
            for sig_file in files:
                sig_path = (Path(root) / sig_file).resolve()
                if sig_path.name.endswith('.yaml'):
                    loaded_def = load_from_yaml(sig_path)
                    for sig in loaded_def:
                        if sig.status == 'enabled' and 'stack_overflow' in sig.watchman_apps:
                            loaded_signatures.append(sig)
        return loaded_signatures
    except Exception as e:
        raise e


def validate_variables() -> (str, str):
    """ Validate whether Stack Overflow Watchman environment variables have been set
        and return them

    Returns:
        (str, str) -- Tuple containing the Stack Overflow Watchman token and domain
    """

    try:
        return os.environ['STACK_OVERFLOW_WATCHMAN_TOKEN'], os.environ['STACK_OVERFLOW_WATCHMAN_DOMAIN']
    except KeyError:
        try:
            os.environ['STACK_OVERFLOW_WATCHMAN_TOKEN']
        except KeyError as exc:
            raise MissingEnvVarError('STACK_OVERFLOW_WATCHMAN_TOKEN') from exc
        try:
            os.environ['STACK_OVERFLOW_WATCHMAN_DOMAIN']
        except KeyError as exc:
            raise MissingEnvVarError('STACK_OVERFLOW_WATCHMAN_DOMAIN') from exc


def search(stack_overflow_client: StackOverflowEnterpriseAPI,
           sig: Signature,
           tf: int,
           logger: JSONLogger or StdoutLogger) -> None:
    """Search Stack Overflow for questions based on a signature

    Args:
        stack_overflow_client: StackOverflowEnterpriseAPI object
        sig: Signature object
        tf: Timeframe to search in seconds
        logger: Logger object
    """

    try:
        logger.log('INFO', f'Searching for: {sig.name}')
        results = query_stackoverflow_excerpts(stack_overflow_client, sig, tf, logger)

        if results:
            for log_data in results:
                if log_data.get('match_type') == 'answer':
                    logger.log(
                        'NOTIFY',
                        log_data,
                        scope='answer',
                        severity=sig.severity,
                        detect_type=sig.name,
                        notify_type='result')
                else:
                    logger.log(
                        'NOTIFY',
                        log_data,
                        scope='question',
                        severity=sig.severity,
                        detect_type=sig.name,
                        notify_type='result')
    except Exception as exc:
        raise exc


def main():
    global OutputLogger
    try:
        start_time = time.time()
        project_metadata = metadata.metadata('stack-overflow-watchman').json

        parser = argparse.ArgumentParser(description=project_metadata.get('summary'))
        parser.add_argument(
            '--timeframe',
            choices=['d', 'w', 'm', 'a'],
            dest='time',
            help='How far back to search: d = 24 hours w = 7 days, m = 30 days, a = all time. Defaults to all time')
        parser.add_argument(
            '--output', '-o',
            choices=['json', 'stdout'],
            dest='logging_type',
            help='Where to send results. Defaults to stdout')
        parser.add_argument(
            '--version', '-v',
            action='version',
            version=f'stack-overflow-watchman {project_metadata.get("version")}')
        parser.add_argument(
            '--debug', '-d',
            dest='debug',
            action='store_true',
            help='Turn on debug level logging')

        args = parser.parse_args()
        tm = args.time
        debug = args.debug
        logging_type = args.logging_type

        if tm == 'd':
            tf = calendar.timegm(time.gmtime()) - 86400
        elif tm == 'w':
            tf = calendar.timegm(time.gmtime()) - 604800
        elif tm == 'm':
            tf = calendar.timegm(time.gmtime()) - 2592000
        else:
            tf = calendar.timegm(time.gmtime()) - 1576800000

        OutputLogger = init_logger(logging_type, debug)

        token, domain = validate_variables()
        stack_overflow_client = StackOverflowEnterpriseAPI(token, domain)

        now = int(time.time())
        today = datetime.date.today().strftime('%Y-%m-%d')
        start_date = time.strftime('%Y-%m-%d', time.localtime(now - tf))

        OutputLogger.log('SUCCESS', 'Stack Overflow Watchman started execution')
        OutputLogger.log('INFO', f'Version: {project_metadata.get("version")}')
        OutputLogger.log('INFO', f'Created by: {project_metadata.get("author")} '
                                 f'<{project_metadata.get("author_email")}>')
        OutputLogger.log('INFO', f'Searching Stack Overflow for '
                                 f'Teams site https://{os.environ.get("STACK_OVERFLOW_WATCHMAN_DOMAIN")}'
                                 f'.stackenterprise.co')
        OutputLogger.log('INFO', f'Searching from {start_date} to {today}')

        OutputLogger.log('INFO', 'Downloading signature file updates')
        SignatureUpdater(OutputLogger).update_signatures()
        OutputLogger.log('INFO', 'Importing signatures...')
        signature_list = load_signatures()
        OutputLogger.log('SUCCESS', f'{len(signature_list)} signatures loaded')
        site_info = stack_overflow_client.get_site_info()
        site_stats = stack_overflow_client.get_site_stats()
        site_metadata = dict(site_info, **site_stats)
        OutputLogger.log('SITE', site_metadata, detect_type='Site', notify_type='site')

        OutputLogger.log('INFO', 'Getting everything...')
        for sig in signature_list:
            search(stack_overflow_client, sig, tf, OutputLogger)

        OutputLogger.log('SUCCESS', f'Stack Overflow Watchman finished execution - Execution time:'
                                    f' {str(datetime.timedelta(seconds=time.time() - start_time))}')

    except Exception as e:
        OutputLogger.log('CRITICAL', e)
        OutputLogger.log('DEBUG', traceback.format_exc())
        sys.exit(1)


if __name__ == '__main__':
    main()
