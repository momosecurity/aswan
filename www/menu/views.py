# coding=utf8
from datetime import datetime
from collections import defaultdict

import pymongo
from bson import ObjectId
from django.views.generic import View
from braces.views import JSONResponseMixin
from django.core.urlresolvers import reverse

from core.generic import ListView
from core.utils import errors_to_dict
from core.pymongo_client import get_mongo_client
from core.redis_client import get_redis_client
from risk_models.menu import build_redis_key
from menu.forms import MenuCreateForm, MenuEventCreateForm, MenuFilterForm
from menu.tables import (
    EventTable, UseridTable, IPTable, UidTable, PayTable, PhoneTable
)


class EventListView(ListView):
    template_name = "menu/event_list.html"
    table_class = EventTable
    enable_page_size_config = True
    collection_name = "menu_event"

    def get_filter_form(self):
        return None

    def get_queryset(self):
        db = get_mongo_client()
        qs = db[self.collection_name].find()
        return qs

    def get_qs_count(self):
        db = get_mongo_client()
        count = db[self.collection_name].count()
        return count


class EventCreateView(JSONResponseMixin, View):
    def post(self, request, *args):
        form = MenuEventCreateForm(data=request.POST, request=request)
        if form.is_valid():
            event_code = form.save()
            data = dict(
                event_code=event_code,
                state=True,
                msg="ok"
            )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class EventDestroyView(JSONResponseMixin, View):
    def _check_event(self, event_code):
        """check名单项目是否被名单策略原子引用"""
        client = get_redis_client()
        for r in client.scan_iter(match="strategy_menu:*"):
            event_id = client.hget(r, 'event')
            if event_code == event_id:
                return True
        return False

    def post(self, request, *args, **kwargs):
        db = get_mongo_client()
        event_code = request.POST.get('id', '')
        res = db.menu_event.find_one({'event_code': event_code})
        if not res:
            return self.render_json_response(dict(
                state=False,
                error="not found"
            ))

        # 1 确保没有被名单管理使用
        if db.menus.find_one({"event": event_code}):
            return self.render_json_response(dict(
                state=False,
                error=u"已生成名单，无法删除"
            ))

        # 2 确保没有被名单策略使用
        is_using = self._check_event(event_code)
        if is_using:
            return self.render_json_response(dict(
                state=False,
                error=u"已生成名单策略原子，无法删除"
            ))

        db.menu_event.delete_one({'event_code': event_code})

        return self.render_json_response(dict(
            state=True,
            msg=u"ok"
        ))


class BaseMenuListView(ListView):
    enable_page_size_config = True
    collection_name = "menus"
    filter_form = MenuFilterForm
    extra_filter_kwargs = {}

    def build_filter_query(self):
        form_obj = self.filter_form(data=self.request.GET)
        if not form_obj.is_valid():
            return self.extra_filter_kwargs

        data = form_obj.cleaned_data
        value = data['filter_value']
        menu_type = data['filter_menu_type']
        event_code = data['filter_event_code']
        menu_status = data['filter_menu_status']
        query = {}
        if value:
            query['value'] = {'$regex': value}
        if menu_type:
            query['menu_type'] = menu_type
        if event_code:
            query['event_code'] = event_code
        if not menu_status:
            menu_status = u'有效'
        if menu_status != u'全部':
            query['menu_status'] = menu_status
        query.update(self.extra_filter_kwargs)
        return query

    def get_queryset(self):
        db = get_mongo_client()
        qs = db[self.collection_name].find(
            self.build_filter_query(),
            sort=[("create_time", pymongo.DESCENDING)]
        )
        return qs

    def get_qs_count(self):
        db = get_mongo_client()
        count = db[self.collection_name].find(
            self.build_filter_query()).count()
        return count

    def get_filter_form(self):
        return self.filter_form(data=self.request.GET,
                                dimension=self.extra_filter_kwargs.get("dimension"))

    def get_context_data(self, **kwargs):
        context = super(BaseMenuListView, self).get_context_data(**kwargs)
        context["create_form"] = MenuCreateForm()
        context["batch_delete_uri"] = reverse("menus:delete")
        return context


class MenuCreateView(JSONResponseMixin, View):
    def post(self, request, *args):
        form = MenuCreateForm(data=request.POST, request=request)
        if form.is_valid():
            error_datas = form.save()
            if error_datas:
                data = dict(
                    state=False,
                    error={"value": [u"以下数据添加失败:{0}".format(error_datas)]}
                )
            else:
                data = dict(
                    state=True,
                    msg="ok"
                )
        else:
            data = dict(
                state=False,
                error=errors_to_dict(form.errors)
            )
        return self.render_json_response(data)


class MenuDestroyView(JSONResponseMixin, View):
    def post(self, request, *args, **kwargs):
        db = get_mongo_client()
        ids = request.POST.get('ids')
        try:
            assert ids
            obj_ids = [ObjectId(id_) for id_ in ids.split(',')]
        except Exception:
            return self.render_json_response(dict(
                state=False,
                error=u"id不合法"
            ))

        redis_values_should_remove = defaultdict(list)

        menus_records = list(
            db['menus'].find({'_id': {"$in": obj_ids}, 'menu_status': u'有效'},
                             {'event_code': True, '_id': False,
                              'dimension': True,
                              'menu_type': True, 'value': True,
                              }))

        if not menus_records:
            return self.render_json_response(dict(
                state=False,
                error=u"记录均不存在"
            ))

        for d in menus_records:
            redis_key = build_redis_key(d['event_code'], d['dimension'],
                                        d['menu_type'])
            if redis_key:
                redis_values_should_remove[redis_key].append(d['value'])

        update_payload = {
            'menu_status': u'无效',
            'creator': request.user.username,
            'create_time': datetime.now(),
        }
        try:
            db.menus.update_many({'_id': {"$in": obj_ids}},
                                 {"$set": update_payload})

            #  同时删除redis中数据
            redis_client = get_redis_client()
            pipeline = redis_client.pipeline(transaction=False)
            for key, values in redis_values_should_remove.items():
                pipeline.srem(key, *values)
            pipeline.execute()
        except Exception:
            return self.render_json_response(dict(
                state=False,
                error=u"操作失败，请稍后重试"
            ))
        return self.render_json_response(dict(
            state=True,
            msg="ok"
        ))


class UseridListView(BaseMenuListView):
    template_name = "menu/userid_list.html"
    table_class = UseridTable
    extra_filter_kwargs = {"dimension": "user_id"}


class IpListView(BaseMenuListView):
    template_name = "menu/ip_list.html"
    table_class = IPTable
    extra_filter_kwargs = {"dimension": "ip"}


class UidListView(BaseMenuListView):
    template_name = "menu/uid_list.html"
    table_class = UidTable
    extra_filter_kwargs = {"dimension": "uid"}


class PayListView(BaseMenuListView):
    template_name = "menu/pay_list.html"
    table_class = PayTable
    extra_filter_kwargs = {"dimension": "pay"}


class PhoneListView(BaseMenuListView):
    template_name = "menu/phone_list.html"
    table_class = PhoneTable
    extra_filter_kwargs = {"dimension": "phone"}
