from django.db import models
from django_conoha_objstorage.api import RestApi


def create_choice_tuple():
    """
    This function returns a tuple of containers.
    Please use it when setting the argument choice of container_name.
    """
    api = RestApi()
    container_list = api.fetch()
    return tuple([tuple([container['name'], container['name']]) for container in container_list])


def get_upload_container(instance, filename):
    container = instance.container_name
    return f'{container}/{filename}'


class ObjectQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.object.storage.delete(obj.object.name)
        super(ObjectQuerySet, self).delete()


class BaseObjectStorage(models.Model):
    objects = ObjectQuerySet.as_manager()

    object = models.FileField(upload_to=get_upload_container)
    container_name = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        super().delete()  # model delete
        self.object.storage.delete(self.object.name)

    class Meta:
        abstract = True
