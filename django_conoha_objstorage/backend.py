import os
import requests
from datetime import datetime
from pytz import timezone
# import email.utils
from io import BytesIO
from django.core.files import File
from django.core.files.storage import Storage
from django.conf import settings
from .api import RestApi


def split_name(name):
    container_name, object_name = name.split('/')
    return container_name, object_name


class ConohaObjectStorage(Storage):
    def __init__(self):
        self.api = RestApi()

    def _open(self, name):
        container_name, object_name = split_name(name)
        response = self.api.get_object(container_name, object_name)
        return File(BytesIO(response))

    def _save(self, name, content):
        container_name, object_name = split_name(name)
        # Confirm the existence of the container. Create container if it does not exist.
        if type(self.api.head_container(container_name)) == dict:
            pass
        else:
            self.api.put_container(container_name)
        # Add post processing if there is an object with the same name in the container.
        if self.exists(name):
            pass  # post
        else:
            self.api.put_object(container_name, object_name, content)
        return name

    def delete(self, name):
        container_name, object_name = split_name(name)
        self.api.delete_object(container_name, object_name)

    def exists(self, name):
        container_name, object_name = split_name(name)
        response = self.api.head_object(container_name, object_name)
        if type(response) == dict:
            return True
        else:
            return False

    def size(self, name):
        container_name, object_name = split_name(name)
        response = self.api.head_object(container_name, object_name)
        if type(response) == dict:
            size = int(response['content-length'])
        else:
            size = 0
        return size

    def path(self, name):
        full_path = os.path.join(self.api.auth['endpoint_url'], name)
        return full_path

    def url(self, name):
        full_path = os.path.join(self.api.auth['endpoint_url'], name)
        res = requests.get(full_path)
        if res.status_code != 200:
            container_name, object_name = split_name(name)
            full_path = self.api.get_temp_url(container_name, object_name)
        return full_path

    def listdir(self, path):
        """
        :param path:
        :return: pending
        """
        pass

    def get_accessed_time(self, name):
        """
        :param name:
        :return: RFC 2822(Pending)
        """
        container_name, object_name = split_name(name)
        response = self.api.head_object(container_name, object_name)
        if type(response) == dict:
            access_date = response['date']
            # ad = email.utils.parsedate_tz(response['date'])
            # dt = datetime(*ad[:7]).strftime('%Y-%m-%d %H:%M:%S')
            # access_date = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            # access_date = access_date.astimezone(timezone(settings.TIME_ZONE))
        else:
            access_date = 0
        return access_date

    def get_created_time(self, name):
        container_name, object_name = split_name(name)
        response = self.api.head_object(container_name, object_name)
        if type(response) == dict:
            create_epoch = int(float(response['x-timestamp']))
        else:
            create_epoch = 0
        return datetime.fromtimestamp(create_epoch, tz=timezone(settings.TIME_ZONE))

    def get_modified_time(self, name):
        """
        Pending
        :param name:
        :return: RFC 2822(Pending)
        """
        container_name, object_name = split_name(name)
        response = self.api.head_object(container_name, object_name)
        if type(response) == dict:
            access_date = response['last-modified']
            # ad = email.utils.parsedate_tz(response['date'])
            # dt = datetime(*ad[:7]).strftime('%Y-%m-%d %H:%M:%S')
            # access_date = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            # access_date = access_date.astimezone(timezone(settings.TIME_ZONE))
        else:
            access_date = 0
        return access_date
