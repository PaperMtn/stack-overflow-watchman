from typing import Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


class StackOverflowEnterpriseAPI:
    def __init__(self,
                 token: str,
                 team_domain: str):
        self.api_key = token
        self.base_url = f"https://{team_domain}.stackenterprise.co/api/2.3"
        self.session = requests.Session()
        self.session.mount(self.base_url,
                           HTTPAdapter(
                               max_retries=Retry(
                                   total=5,
                                   backoff_factor=0.3,
                                   status_forcelist=[500, 502, 503, 504])))
        self.session.headers = {'X-API-Key': self.api_key}
        self.filter_id = self._create_filter()

    def _create_filter(self) -> str:
        """ Create a filter for API requests. This is used to for getting additional
            fields in the API requests

        Returns:
            Filter ID string
        """

        params = {
            'include': 'answer.link;answer.score;answer.body',
            'unsafe': 'false'
        }

        response = self.session.post(f'{self.base_url}/filters/create', params=params)
        return response.json()['items'][0]['filter']

    def _make_request(self,
                      endpoint: str,
                      params: Dict[Any, Any] = None):
        if params is None:
            params = {}
        items = []
        page = 1
        while True:
            current_params = params.copy()
            current_params.update(
                {
                    'page': page,
                    'pagesize': 100,
                    'filter': self.filter_id
                })
            response = self.session.get(f'{self.base_url}/{endpoint}', params=current_params)
            response.raise_for_status()
            data = response.json()
            items.extend(data['items'])
            if not data['has_more']:
                break
            page += 1
        return items

    def get_site_stats(self, **kwargs):
        """ Get current site statistics

        Returns:
            JSON object with the site information
        """

        params = kwargs
        return self._make_request('info', params)[0]

    def get_site_info(self, **kwargs):
        """ Get information on the current site

        Returns:
            JSON object with the site information
        """

        params = kwargs
        return self._make_request('sites', params)[0]

    def get_question(self, question_id: str, **kwargs):
        """ Get a question by ID

        Args:
            question_id: ID of the question to return
        Returns:
            JSON object with the question
        """

        params = kwargs
        return self._make_request(f'questions/{question_id}', params)[0]

    def get_answer(self, answer_id: str, **kwargs):
        """ Get an answer by ID

        Args:
            answer_id: ID of the answer to return
        Returns:
            JSON object with the answer
        """

        params = kwargs
        return self._make_request(f'answers/{answer_id}', params)[0]

    def get_user(self, user_id: str, **kwargs):
        """ Get a user by ID

        Args:
            user_id: ID of the answer to return
        Returns:
            JSON object with the user
        """

        params = kwargs
        return self._make_request(f'users/{user_id}', params)[0]

    def search_advanced(self, query: str, timeframe: str or int, **kwargs):
        """ Search for questions meeting the set criteria

        Args:
            query: Text query to search for
            timeframe: How far back to search (epoch timeframe)
        Returns:
            JSON object with matching questions
        """

        params = {
            'order': 'desc',
            'sort': 'activity',
            'q': query,
            'fromdate': timeframe
        }
        params.update(kwargs)
        return self._make_request('search/advanced', params)

    def search_excerpts(self, query: str, timeframe: str or int or None, **kwargs):
        """ Search for excerpts meeting the set criteria

        Args:
            query: Text query to search for
            timeframe: How far back to search (epoch timeframe)
        Returns:
            JSON object with matching excepts
        """

        params = {
            'order': 'desc',
            'sort': 'activity',
            'q': query,
            'fromdate': timeframe
        }
        params.update(kwargs)
        return self._make_request('search/excerpts', params)
