import pandas as pd
import requests


class GetSlateData:
    '''Returns the results of a Slate query exposed through webservices'''
    def __init__(self):
        self.url = 'https://gradadmissions.du.edu/manage/query/run'

    def query(self, h, id):
        '''
        Simply use the parameters from the webservices URL and the results of that query will be returned as a pandas
        dataframe.
        :param h: str, The value labels "h" in the webservices url (the last parameter)
        :param id: str, The query id
        :return: pd.DataFrame
        '''
        params = {
            'id': id,
            'cmd': 'service',
            'output': 'json',
            'h': h
        }
        req = requests.get(self.url, params)
        return pd.json_normalize(req.json(), record_path="row")
