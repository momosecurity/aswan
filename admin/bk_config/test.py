import json

from django.urls import reverse

from core.testcase import BaseTestCase
from core.utils import get_sample_str


class TestConfigView(BaseTestCase):
    create_uri = 'config:source_create'
    list_uri = 'config:source_list'
    destroy_uri = 'config:source_destroy'
    ajax_uri = 'config:source_ajax'

    def _test_create(self):
        content = json.dumps({
            "user_id": "string",
            "uid": "string",
            "ip": "string"
        })
        name_show = get_sample_str(8)
        name_key = get_sample_str(8)
        response = self.client.post(reverse(self.create_uri),
                                    data={'content': content,
                                          'name_show': name_show,
                                          'name_key': name_key})
        self.assertEquals(response.status_code, 200)
        resp_dict = json.loads(response.content)
        self.name_key = resp_dict['msg']
        self.assertEquals(name_key, self.name_key)
        self.assertIs(resp_dict['state'], True)

    def _test_destroy(self):
        req_body = {'name_key': self.name_key}
        response = self.client.post(reverse(self.destroy_uri), data=req_body)
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertIs(resp_json['state'], True)

    def _test_ajax(self):
        response = self.client.get(reverse(self.ajax_uri))
        self.assertEquals(response.status_code, 200)
        resp_json = json.loads(response.content)
        self.assertIs(resp_json['state'], True)
        self.assertEquals(len(resp_json['data']), 1)

    def _test_list(self):
        response = self.client.get(reverse(self.list_uri))
        self.assertEquals(response.status_code, 200)

    def test_method(self):
        self._test_create()
        self._test_list()
        self._test_ajax()
        self._test_destroy()
