import dataclasses
import json
import re
from datetime import datetime
from typing import List, Dict

from stack_overflow_watchman.clients.stack_overflow_wrapper import StackOverflowEnterpriseAPI
from stack_overflow_watchman.loggers import JSONLogger, StdoutLogger
from stack_overflow_watchman.models.models import (
    Owner,
    Question,
    Answer
)
from stack_overflow_watchman.models.signature import Signature


def _convert_time(timestamp: str or int) -> str or None:
    """Convert epoch timestamp to ISO 8601 string """

    pattern = '%Y-%m-%dT%H:%M:%S.%f%z'
    try:
        return datetime.strftime(datetime.fromtimestamp(timestamp), pattern)
    except:
        return None


def _deduplicate(input_list: List[Dict]) -> List[Dict]:
    """ Removes duplicates where results are returned by multiple queries
    Nested class handles JSON encoding for dataclass objects

    Args:
        input_list: List of dataclass objects
    Returns:
        List of JSON objects with duplicates removed
    """

    class EnhancedJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if dataclasses.is_dataclass(o):
                return dataclasses.asdict(o)
            return super().default(o)

    json_set = {json.dumps(dictionary, sort_keys=True, cls=EnhancedJSONEncoder)
                for dictionary in input_list}

    return [json.loads(t) for t in json_set]


def query_stackoverflow_excerpts(stack_overflow_client: StackOverflowEnterpriseAPI,
                                 sig: Signature,
                                 timeframe: int,
                                 log_handler: JSONLogger or StdoutLogger) -> List[Dict] or None:
    """ Search Stack Overflow for questions based on a signature

    Args:
        stack_overflow_client: StackOverflowEnterpriseAPI object
        sig: Signature object
        timeframe: Timeframe to search in seconds
        log_handler: Logger object
    Returns:
        List of questions
    """
    try:
        results = []
        for query in sig.search_strings:
            log_handler.log('INFO', f'Searching for: {query}')
            potential_matches = stack_overflow_client.search_excerpts(query, timeframe)
            if potential_matches:
                log_handler.log('INFO', f'{len(potential_matches)} potential matches found')

            for pattern in sig.patterns:
                compiled_pattern = re.compile(pattern)
                matches = [question for question in potential_matches if compiled_pattern.search(question['body'])]

                for match in matches:
                    match_string = compiled_pattern.search(match.get('body')).group(0)

                    if match.get('item_type') == 'answer':
                        answer = stack_overflow_client.get_answer(match.get('answer_id'))
                        user = Owner(**answer.get('owner'))
                        answer['owner'] = user
                        answer['creation_date'] = _convert_time(answer.get('creation_date'))
                        answer['last_activity_date'] = _convert_time(answer.get('last_activity_date'))
                        answer['community_owned_date'] = _convert_time(answer.get('community_owned_date'))
                        answer['locked_date'] = _convert_time(answer.get('locked_date'))
                        answer['last_edit_date'] = _convert_time(answer.get('last_edit_date'))
                        answer_obj = Answer(**answer)
                        results.append({
                            'match_string': match_string,
                            'match_type': match.get('item_type'),
                            'answer': answer_obj
                        })
                    else:
                        question = stack_overflow_client.get_question(match.get('question_id'))
                        user = Owner(**question.get('owner'))
                        question['owner'] = user
                        question['creation_date'] = _convert_time(question.get('creation_date'))
                        question['last_activity_date'] = _convert_time(question.get('last_activity_date'))
                        question['community_owned_date'] = _convert_time(question.get('community_owned_date'))
                        question['locked_date'] = _convert_time(question.get('locked_date'))
                        question['last_edit_date'] = _convert_time(question.get('last_edit_date'))
                        question['closed_date'] = _convert_time(question.get('closed_date'))
                        question['bounty_closes_date'] = _convert_time(question.get('bounty_closes_date'))
                        question['protected_date'] = _convert_time(question.get('protected_date'))
                        question_obj = Question(**question)
                        results.append({
                            'match_string': match_string,
                            'match_type': match.get('item_type'),
                            'question': question_obj
                        })
        if results:
            results = _deduplicate(results)
            log_handler.log('SUCCESS', f'{len(results)} total matches found after filtering')
            return results
        else:
            log_handler.log('INFO', 'No matches found after filtering')
            return None
    except Exception as exc:
        log_handler.log('ERROR', f'Error occurred: {exc}')
        raise exc
