"""

This app is taken from http://code.google.com/p/django-tagging/
This chunk of code was moved from __init__ temporarily 
in order to solve some weird settings issues with rapidsms
11/22/09
"""

from django.utils.translation import ugettext as _

VERSION = (0, 3, 'pre')

class AlreadyRegistered(Exception):
    """
    An attempt was made to register a model more than once.
    """
    pass

registry = []

def register(model, tag_descriptor_attr='tags',
             tagged_item_manager_attr='tagged'):
    """
    Sets the given model class up for working with tags.
    """
    if model in registry:
        raise AlreadyRegistered(
            _('The model %s has already been registered.') % model.__name__)
    registry.append(model)

    # Add tag descriptor
    setattr(model, tag_descriptor_attr, TagDescriptor())

    # Add custom manager
    ModelTaggedItemManager().contribute_to_class(model,
                                                 tagged_item_manager_attr)



"""
Custom managers for Django models registered with the tagging
application.
"""
from django.contrib.contenttypes.models import ContentType
from django.db import models

from tagging.models import Tag, TaggedItem

class ModelTagManager(models.Manager):
    """
    A manager for retrieving tags for a particular model.
    """
    def get_query_set(self):
        ctype = ContentType.objects.get_for_model(self.model)
        return Tag.objects.filter(
            items__content_type__pk=ctype.pk).distinct()

    def cloud(self, *args, **kwargs):
        return Tag.objects.cloud_for_model(self.model, *args, **kwargs)

    def related(self, tags, *args, **kwargs):
        return Tag.objects.related_for_model(tags, self.model, *args, **kwargs)

    def usage(self, *args, **kwargs):
        return Tag.objects.usage_for_model(self.model, *args, **kwargs)

class ModelTaggedItemManager(models.Manager):
    """
    A manager for retrieving model instances based on their tags.
    """
    def related_to(self, obj, queryset=None, num=None):
        if queryset is None:
            return TaggedItem.objects.get_related(obj, self.model, num=num)
        else:
            return TaggedItem.objects.get_related(obj, queryset, num=num)

    def with_all(self, tags, queryset=None):
        if queryset is None:
            return TaggedItem.objects.get_by_model(self.model, tags)
        else:
            return TaggedItem.objects.get_by_model(queryset, tags)

    def with_any(self, tags, queryset=None):
        if queryset is None:
            return TaggedItem.objects.get_union_by_model(self.model, tags)
        else:
            return TaggedItem.objects.get_union_by_model(queryset, tags)

class TagDescriptor(object):
    """
    A descriptor which provides access to a ``ModelTagManager`` for
    model classes and simple retrieval, updating and deletion of tags
    for model instances.
    """
    def __get__(self, instance, owner):
        if not instance:
            tag_manager = ModelTagManager()
            tag_manager.model = owner
            return tag_manager
        else:
            return Tag.objects.get_for_object(instance)

    def __set__(self, instance, value):
        Tag.objects.update_tags(instance, value)

    def __delete__(self, instance):
        Tag.objects.update_tags(instance, None)
