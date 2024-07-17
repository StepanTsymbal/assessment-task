import requests

DEFAULT_API_VERSION = "v58.0"


def get_auth_response(token_uri=None, consumer_key=None, consumer_secret=None, user_name=None, password=None):
    if not token_uri or not consumer_key or not consumer_secret or not user_name or not password:
        raise RuntimeError("Must provide token_uri, consumer_key, consumer_secret, user_name and password!")

    base_url = '{}?grant_type=password&client_id={}&client_secret={}&username={}&password={}'
    url = base_url.format(token_uri, consumer_key, consumer_secret, user_name, password)
    res_at = requests.post(url)
    res_json = res_at.json()

    if 'error' in res_json:
        raise ConnectionError("Auth failed!", res_json['error'])

    return res_json


class SalesforceConnector(object):
    def __init__(self, access_token=None, instance_url=None, api_version=DEFAULT_API_VERSION):
        if not access_token or not instance_url:
            raise RuntimeError("Must provide access_token and instance_url!")
        self.access_token = access_token
        self.instance_url = instance_url
        self.api_version = api_version

    def create_job(self, operation=None, obj=None, external_id_field_name=None, content_type='CSV', line_ending='LF'):
        if not operation or not obj:
            raise RuntimeError("Must provide operation and obj!")

        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }
        body = {
            "object": obj,
            "contentType": content_type,
            "operation": operation,
            "externalIdFieldName": external_id_field_name,
            "lineEnding": line_ending
        }
        uri = '{}/services/data/{}/jobs/ingest/'.format(self.instance_url, self.api_version)
        response = requests.post(uri, headers=headers, json=body)
        job_id = response.json()['id']

        return job_id

    def get_job_status(self, job_id=None, optype=None):
        if not job_id:
            raise RuntimeError("Must provide job_id!")
        if not optype:
            raise RuntimeError("Must provide optype ['ingest', 'query']!")

        uri = '{}/services/data/{}/jobs/{}/{}'.format(self.instance_url, self.api_version, optype, job_id)
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }
        post_res = requests.get(uri, headers=headers)

        return post_res

    def put_data(self, content_url=None, data=None):
        if not content_url or not data:
            raise RuntimeError("Must provide contentUrl and data!")

        put_uri = '{}/{}'.format(self.instance_url, content_url)
        put_headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'text/csv',
            'Accept': 'application/json'
        }

        put_response = requests.put(put_uri, headers=put_headers, data=data)

        return put_response

    def patch_state(self, job_id=None, state=None):
        if not job_id:
            raise RuntimeError("Must provide job_id!")
        if not state:
            raise RuntimeError("Must provide state: ['UpdateComplete']")

        patch_uri = '{}/services/data/{}/jobs/ingest/{}'.format(self.instance_url, self.api_version, job_id)
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }

        patch_body = {"state": state}
        patch_res = requests.patch(patch_uri, json=patch_body, headers=headers)

        return patch_res

    def get_failure_status(self, job_id=None):
        if not job_id:
            raise RuntimeError("Must provide job_id!")

        jobs_failure_uri = '{}/services/data/{}/jobs/ingest/{}/failedResults/'.format(self.instance_url,
                                                                                      self.api_version, job_id)
        headers = {
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json'
        }
        failure_res = requests.get(jobs_failure_uri, headers=headers)

        return failure_res
