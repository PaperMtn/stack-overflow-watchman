import csv
import dataclasses
import json
import logging
import logging.handlers
import os
import re
import sys
import traceback
from logging import Logger
from typing import Any, Dict, List, ClassVar, Protocol

from colorama import Fore, Back, Style, init


class StdoutLogger:
    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug')
        self.print_header()
        init()

    def log(self,
            mes_type: str,
            message: Any,
            **kwargs) -> None:

        notify_type = kwargs.get('notify_type')
        scope = kwargs.get('scope')

        if not self.debug and mes_type == 'DEBUG':
            return

        if dataclasses.is_dataclass(message):
            message = dataclasses.asdict(message)

        if notify_type == "site":
            message = f'SITE: \n' \
                      f'    NAME: {message.get("name")}  \n' \
                      f'    URL: {message.get("site_url")}  \n' \
                      f'    AUDIENCE: {message.get("audience")}  \n' \
                      f'    USERS: {message.get("total_users")}  \n' \
                      f'    QUESTIONS: {message.get("total_questions")}  \n' \
                      f'    ANSWERS: {message.get("total_answers")}  \n' \
                      f'    ACCEPTED_ANSWERS: {message.get("total_accepted")}  \n' \
                      f'    API_REVISION: {message.get("api_revision")}'
            mes_type = 'SITE'
        if notify_type == "result":
            if scope == 'question':
                message = 'SCOPE: Question' \
                          f'    OWNER: {message.get("question").get("owner").get("display_name")} \n' \
                          f'    QUESTION_URL: {message.get("question").get("link")} \n' \
                          f'    QUESTION_TITLE: {message.get("question").get("title")} \n' \
                          f'    CREATED: {message.get("question").get("creation_date")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            elif scope == 'answer':
                message = 'SCOPE: Answer' \
                          f'    OWNER: {message.get("answer").get("owner").get("display_name")} \n' \
                          f'    ANSWER_URL: {message.get("answer").get("link")} \n' \
                          f'    CREATED: {message.get("answer").get("creation_date")} \n' \
                          f'    POTENTIAL_SECRET: {message.get("match_string")} \n' \
                          f'    -----'
            mes_type = 'RESULT'
        try:
            self.log_to_stdout(message, mes_type)
        except Exception as e:
            print(e)
            self.log_to_stdout(message, mes_type)

    def log_to_stdout(self,
                      message: Any,
                      mes_type: str) -> None:

        try:

            reset_all = Style.NORMAL + Fore.RESET + Back.RESET
            key_color = Fore.WHITE
            base_color = Fore.WHITE
            high_color = Fore.WHITE
            style = Style.NORMAL

            if mes_type == "NOTIFY":
                base_color = Fore.CYAN
                high_color = Fore.CYAN
                key_color = Fore.CYAN
                style = Style.NORMAL
            elif mes_type == 'INFO':
                base_color = Fore.WHITE
                high_color = Fore.WHITE
                key_color = Fore.WHITE
                style = Style.DIM
                mes_type = '-'
            elif mes_type == 'SITE':
                base_color = Fore.LIGHTBLUE_EX
                high_color = Fore.LIGHTBLUE_EX
                key_color = Fore.LIGHTBLUE_EX
                style = Style.NORMAL
                mes_type = '+'
            elif mes_type == 'USER':
                base_color = Fore.RED
                high_color = Fore.RED
                key_color = Fore.RED
                style = Style.NORMAL
                mes_type = '+'
            elif mes_type == 'WARNING':
                base_color = Fore.YELLOW
                high_color = Fore.YELLOW
                key_color = Fore.YELLOW
                style = Style.NORMAL
                mes_type = '!'
            elif mes_type == "SUCCESS":
                base_color = Fore.LIGHTGREEN_EX
                high_color = Fore.LIGHTGREEN_EX
                key_color = Fore.LIGHTGREEN_EX
                style = Style.NORMAL
                mes_type = '>>'
            elif mes_type == "DEBUG":
                base_color = Fore.WHITE
                high_color = Fore.WHITE
                key_color = Fore.WHITE
                style = Style.DIM
                mes_type = '#'
            elif mes_type == "ERROR":
                base_color = Fore.MAGENTA
                high_color = Fore.MAGENTA
                key_color = Fore.MAGENTA
                style = Style.NORMAL
            elif mes_type == "CRITICAL":
                base_color = Fore.RED
                high_color = Fore.RED
                key_color = Fore.RED
                style = Style.NORMAL
            elif mes_type == "RESULT":
                base_color = Fore.LIGHTGREEN_EX
                high_color = Fore.LIGHTGREEN_EX
                key_color = Fore.LIGHTGREEN_EX
                style = Style.NORMAL
                mes_type = '!'

            # Make log level word/symbol coloured
            type_colorer = re.compile(r'([A-Z]{3,})', re.VERBOSE)
            mes_type = type_colorer.sub(high_color + r'\1' + base_color, mes_type.lower())
            # Make header words coloured
            header_words = re.compile(r'([A-Z_0-9]{2,}:)\s', re.VERBOSE)
            message = header_words.sub(key_color + Style.BRIGHT + r'\1 ' + Fore.WHITE + Style.NORMAL, str(message))
            sys.stdout.write(
                f"{reset_all}{style}[{base_color}{mes_type}{Fore.WHITE}]{style} {message}{Fore.WHITE}{Style.NORMAL}\n")
        except Exception:
            if self.debug:
                traceback.print_exc()
                sys.exit(1)
            print('Formatting error')

    def print_header(self) -> None:
        print(" ".ljust(79) + Style.BRIGHT)

        print(Fore.YELLOW + Style.BRIGHT +
              """
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠾⠛⢉⣉⣉⣉⡉⠛⠷⣦⣄⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⠋⣠⣴⣿⣿⣿⣿⣿⡿⣿⣶⣌⠹⣷⡀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⠁⣴⣿⣿⣿⣿⣿⣿⣿⣿⣆⠉⠻⣧⠘⣷⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⠈⠀⢹⡇⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⢸⣿⠛⣿⣿⣿⣿⣿⣿⡿⠃⠀⠀⠀⠀⢸⡇⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⢿⡆⠈⠛⠻⠟⠛⠉⠀⠀⠀⠀⠀⠀⣾⠃⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣧⡀⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⠃⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢼⠿⣦⣄⠀⠀⠀⠀⠀⠀⠀⣀⣴⠟⠁⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⣠⣾⣿⣦⠀⠀⠈⠉⠛⠓⠲⠶⠖⠚⠋⠉⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⣠⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀ ⠈⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        """ + Style.RESET_ALL
              )
        print('   Stack Overflow Watchman     ')
        print(
            Style.DIM + '   Finding exposed secrets and personal data in Stack Overflow Enterprise      '
            + Style.RESET_ALL)
        print('  ')
        print(Style.BRIGHT + '   by PaperMtn - GNU General Public License')
        print(' '.ljust(79) + Fore.GREEN)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


class JSONLogger(Logger):
    def __init__(self, name: str = 'stack_overflow_watchman', **kwargs):
        super().__init__(name)
        self.notify_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "NOTIFY", "scope": "%(scope)s", "severity": '
            '"%(severity)s", "detection_type": "%(type)s", "detection_data": %(message)s}')
        self.info_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}')
        self.success_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "SUCCESS", "message": %(message)s}')
        self.site_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "SITE", "message": %(message)s}')
        self.user_format = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "USER", "message": %(message)s}')
        self.logger = logging.getLogger(self.name)
        self.handler = logging.StreamHandler(sys.stdout)
        self.logger.addHandler(self.handler)
        if kwargs.get('debug'):
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    def log(self,
            level: str,
            log_data: str or Dict,
            **kwargs):
        if level.upper() == 'NOTIFY':
            self.handler.setFormatter(self.notify_format)
            self.logger.info(
                json.dumps(
                    log_data,
                    cls=EnhancedJSONEncoder),
                extra={
                    'scope': kwargs.get('scope', ''),
                    'type': kwargs.get('detect_type', ''),
                    'severity': kwargs.get('severity', '')})
        elif level.upper() == 'INFO':
            self.handler.setFormatter(self.info_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'DEBUG':
            self.handler.setFormatter(self.info_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'SUCCESS':
            self.handler.setFormatter(self.success_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'SITE':
            self.handler.setFormatter(self.site_format)
            self.logger.info(json.dumps(log_data))
        elif level.upper() == 'USER':
            self.handler.setFormatter(self.user_format)
            self.logger.info(json.dumps(log_data))
        else:
            self.handler.setFormatter(self.info_format)
            self.logger.critical(log_data)


class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict]


def export_csv(csv_name: str, export_data: List[IsDataclass]) -> None:
    """ Export the data passed in a dataclass to CSV file

    Args:
        csv_name: Name of the CSV file to create
        export_data: Dataclass object to create CSV from
    """
    try:
        headers = dataclasses.asdict(export_data[0]).keys()
        with open(f'{os.path.join(os.getcwd(), csv_name)}.csv', 'w') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for item in export_data:
                writer.writerow(dataclasses.asdict(item))
        f.close()
    except Exception as e:
        print(e)
