from requests import post
from requests import get
from json import loads
from os.path import join
from os import chmod
from subprocess import Popen, PIPE
from swiftclient import (
    put_object,
    get_object,
    delete_object,
    head_object,
    head_container,
    put_container
)
from swiftclient.utils import generate_temp_url
from swiftclient.exceptions import ClientException
from django.conf import settings


class RestApi(object):
    def __init__(self):
        self.auth: dict = {
            'tenant_name': settings.OS_TENANT_NAME,
            'tenant_id': settings.OS_TENANT_ID,
            'auth_url': settings.OS_AUTH_URL,
            'endpoint_url': settings.OS_ENDPOINT_URL,
            'password_credentials': {
                'username': settings.OS_USERNAME,
                'password': settings.OS_PASSWORD,
            },
            'tempurl_key': settings.OS_TEMPURL_KEY,
        }

    def fetch_token(self) -> str:
        """
        apiアクセスにはtoken取得が必要なので、事前にこの関数を実行して返り値を貰う必要があります。
        """
        url: str = join(self.auth['auth_url'], 'tokens')
        data: dict = {
            "auth": {
                'passwordCredentials': self.auth['password_credentials'],
                'tenantId': self.auth['tenant_id'],
            }
        }
        r = post(url=url, json=data)
        if r.status_code == 200:
            return loads(r.text, encoding='utf-8')['access']['token']['id']
        else:
            raise AuthorizedError()

    def fetch(self, container: str = '', obj: str = ''):
        """
        container, objが共に空なら、オブジェクトストレージ全体の情報を返します。
        objのみが空なら対象オブジェクト内に存在するファイルをdictで返します。
        container, objに文字列が渡されていれば、対象objectファイルのバイナリを返却します。
        """
        url: str = join(self.auth['endpoint_url'], container, obj)
        payload: dict = {
            'X-Auth-Token': self.fetch_token(),
            'Accept': 'application/json',
        }

        r = get(url=url, headers=payload)
        if r.status_code == 200:
            if obj:
                return r.content
            else:
                return loads(r.text, encoding='utf-8')
        else:
            raise AuthorizedError()

    def fetch_container(self) -> iter:
        r = self.fetch()
        return (i['name'] for i in r)

    def create_tempurl(self, container: str, obj: str) -> str:
        method: str = 'GET'
        expires: str = "600"
        path: str = join(self.auth['endpoint_url'], container, obj)
        key: str = self.auth['tempurl_key']
        command: list = f'swift tempurl {method} {expires} {path} {key}'.split(
            ' ')
        std = Popen(command, shell=False, encoding='utf-8',
                    stdout=PIPE, stderr=PIPE)
        outs, _ = std.communicate()
        if '\n' in outs:
            outs = outs.replace('\n', '')
        return outs

    def register_for_metadata(self, payload: dict, container: str = "", obj: str = ""):
        url: str = join(self.auth['endpoint_url'], container, obj)
        r = post(url=url, headers=payload)
        return r.status_code, r.headers, r.text

    def remove_for_metadata(self, metaname: str, container: str = "", obj: str = ""):
        metaname = metaname.title()
        if metaname[:2] == 'X-':
            metaname = metaname[2:]
        url: str = join(self.auth['endpoint_url'], container, obj)
        meta = 'X-Remove-' + metaname
        payload: dict = {
            'X-Auth-Token': self.fetch_token(),
            meta: '',
        }
        r = post(url=url, headers=payload)
        return r.status_code, r.headers, r.text

    def write_token(self,
                    path: str = "./token.txt",
                    mode: str = 'wt',
                    encoding: str = 'utf-8'):
        token: str = self.fetch_token()
        try:
            with open(file=path, mode=mode, encoding=encoding) as fp:
                fp.write(token)
        except (IOError, OSError, TypeError):
            raise IOError
        else:
            chmod(path, 0o704)

    # ここからswift clientを利用
    def head_container(self, container_name):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            response = head_container(url=url, token=token, container=container_name)
        except ClientException:
            response = None
        return response

    def put_container(self, container_name):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            put_container(url=url, token=token, container=container_name)
        except ClientException:
            pass

    def head_object(self, container_name, object_name):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            response = head_object(url=url, token=token, container=container_name, name=object_name)
        except ClientException:
            response = None
        return response

    def get_object(self, container_name, object_name):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            response = get_object(url=url, token=token, container=container_name, name=object_name)
        except ClientException:
            response = None
        return response

    def put_object(self, container_name, object_name, content):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            response = put_object(url=url, token=token, container=container_name, name=object_name, contents=content)
        except ClientException:
            response = None
        return response

    def delete_object(self, container_name, object_name):
        token = self.fetch_token()
        url = self.auth['endpoint_url']
        try:
            delete_object(url=url, token=token, container=container_name, name=object_name)
        except ClientException:
            pass

    def get_temp_url(self, container_name, object_name):
        tenant_id = self.auth['tenant_id']
        url = f'/v1/nc_{tenant_id}/{container_name}/{object_name}'
        key = self.auth['tempurl_key'].encode('utf-8')
        method = 'GET'
        seconds = 60 * 60 * 24
        temp_url = generate_temp_url(path=url, seconds=seconds, key=key, method=method)
        return 'https://object-storage.tyo2.conoha.io' + temp_url


class AuthorizedError(Exception):
    pass