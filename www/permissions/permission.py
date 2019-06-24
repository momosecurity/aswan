# -*- coding: utf-8 -*-

import logging
import sys
import traceback

import pymongo
from bson import ObjectId
from bson.errors import InvalidId
from pymongo.errors import PyMongoError

from core.pymongo_client import get_mongo_client


logger = logging.getLogger(__name__)


class DBError(Exception):
    pass


def mongodb_error_log(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except PyMongoError as err:
            tb_content = ' '.join(traceback.format_exception(*sys.exc_info()))
            msg = (
                '\nOperate Mongodb error! \n Func: {}, args: {}, kwargs: {} '
                '\n Error: {} \n {}'
            ).format(func.__name__, args, kwargs, err, tb_content)
            logger.error(msg)
            raise DBError(msg)
        except InvalidId as err:
            logger.error('Invalid BSON ObjectId: {}'.format(err))
    return wrapper


class PermManager(object):
    def __get__(self, instance, klass):
        """lazy bind proxy"""
        if instance:
            self.collection = instance.COLLECTION
            self.primary_key = instance.PRIMARY_KEY
        else:
            self.collection = klass.COLLECTION
            self.primary_key = klass.PRIMARY_KEY
        self.klass = klass
        self.projection_fields = klass.PROJECTION_FIELDS
        return self

    @mongodb_error_log
    def all(self, meta_only=False):
        db = get_mongo_client()
        projection = {f: True for f in self.projection_fields} if meta_only else {}
        return db[self.collection].find(projection=projection)

    @mongodb_error_log
    def all_fields(self):
        db = get_mongo_client()
        return db[self.collection].find({})

    @mongodb_error_log
    def delete_by_element(self, container, element):
        db = get_mongo_client()
        db[self.collection].update({}, {'$pull': {container: element}})

    @mongodb_error_log
    def get(self, item):
        db = get_mongo_client()
        doc = db[self.collection].find_one({self.primary_key: item})
        if not doc:
            return None
        return self.klass(**doc)

    @mongodb_error_log
    def get_by_id(self, entity_id):
        db = get_mongo_client()
        doc = db[self.collection].find_one({'_id': ObjectId(entity_id)})
        if not doc:
            return None
        return self.klass(**doc)

    @mongodb_error_log
    def raw_query(self, query):
        db = get_mongo_client()
        docs = db[self.collection].find(query).sort('_id', pymongo.DESCENDING)
        result = []
        for doc in docs:
            try:
                result.append(self.klass(**doc))
            except TypeError:
                logger.error('Permission data corruption! class: {}, doc: {}'
                             .format(self.klass, doc))
        return result

    @mongodb_error_log
    def multi_get(self, items):
        db = get_mongo_client()
        docs = db[self.collection].find({self.primary_key: {'$in': items}}) \
                                  .sort('_id', pymongo.DESCENDING)
        return [self.klass(**doc) for doc in docs]


class Permission(object):
    COLLECTION = None
    FIELDS = []
    PRIMARY_KEY = 'pk'

    objects = PermManager()

    def __init__(self, entity_id=None, **kwargs):
        self.entity_id = entity_id or kwargs.get('_id')

    def __getattr__(self, name):
        if name in self.FIELDS:
            return self.values[name]
        raise AttributeError('No such attribute in Permission: {}'.format(name))

    def __setattr__(self, name, value):
        if name in self.FIELDS:
            self.values[name] = value
            return
        return super(Permission, self).__setattr__(name, value)

    def __repr__(self):
        return '<{}>: {}'.format(self.__class__.__name__, self.pk)

    def json(self):
        data = {'entity_id': self.entity_id}
        data.update(self.values)
        return data

    @mongodb_error_log
    def save(self):
        db = get_mongo_client()
        if self.entity_id:
            entity_id = ObjectId(self.entity_id)
            return db[self.COLLECTION].update_one({'_id': entity_id},
                                                  {'$set': self.values})
        else:
            return db[self.COLLECTION].insert_one(self.values)

    @mongodb_error_log
    def delete(self):
        db = get_mongo_client()
        if not self.entity_id:
            return
        entity_id = ObjectId(self.entity_id)
        db[self.COLLECTION].delete_one({'_id': entity_id})


class UserPermission(Permission):
    COLLECTION = 'permission_user'
    FIELDS = ['pk', 'fullname', 'is_superuser', 'remark',
              'groups', 'permissions']
    PROJECTION_FIELDS = FIELDS[:4]

    def __init__(self, pk, fullname='', is_superuser=False,
                 remark='', groups=None, permissions=None, **kwargs):
        super(UserPermission, self).__init__(**kwargs)
        self.values = {
            'fullname': fullname,
            'is_superuser': is_superuser,
            'pk': pk,
            'remark': remark,
            'groups': groups or [],
            'permissions': permissions or [],
        }

    @property
    def perm_uris(self):
        perm_groups = GroupPermission.objects.multi_get(self.groups) or []
        perms = [perm for group in perm_groups
                 for perm in group.permissions if group]
        perms += self.permissions
        return UriGroupPermission.group_to_uri(list(set(perms)))


class GroupPermission(Permission):
    COLLECTION = 'permission_group'
    FIELDS = ['pk', 'desc', 'permissions']
    PROJECTION_FIELDS = FIELDS[:2]

    def __init__(self, pk, desc='', permissions=None, **kwargs):
        super(GroupPermission, self).__init__(**kwargs)
        self.values = {
            'pk': pk,
            'desc': desc,
            'permissions': permissions or [],
        }

    @property
    def perm_uris(self):
        return UriGroupPermission.group_to_uri(self.permissions)

    def delete(self):
        super(GroupPermission, self).delete()
        UserPermission.objects.delete_by_element('group', self.pk)


class UriGroupPermission(Permission):
    COLLECTION = 'permission_uri_group'
    FIELDS = ['pk', 'desc', 'uris']
    PROJECTION_FIELDS = FIELDS[:2]

    def __init__(self, pk, desc='', uris=None, **kwargs):
        super(UriGroupPermission, self).__init__(**kwargs)
        self.values = {
            'pk': pk,
            'desc': desc,
            'uris': uris or [],
        }

    def delete(self):
        super(UriGroupPermission, self).delete()
        GroupPermission.objects.delete_by_element('permission', self.pk)
        UserPermission.objects.delete_by_element('permission', self.pk)

    @classmethod
    def group_to_uri(cls, groups):
        perm_groups = cls.objects.multi_get(groups) or []
        return set(uri for group in perm_groups for uri in group.uris if group)
