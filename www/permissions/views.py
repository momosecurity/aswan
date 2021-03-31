# -*- coding: utf-8 -*-

from braces.views import JSONResponseMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http.request import QueryDict
from django.views.generic import TemplateView, ListView as OriginListView

from www.core.generic import ListView
from www.core.utils import errors_to_dict
from www.permissions.forms import (
    UserPermFilterForm, UserPermUpdateForm,
    GroupPermUpdateForm, UriGroupPermUpdateForm,
)
from www.permissions.permission import (
    UserPermission, GroupPermission, UriGroupPermission,
)
from www.permissions.tables import (
    UserPermissionTable, GroupPermissionTable, UriGroupPermissionTable
)


###################
# user permission #
###################


class UserPermListView(ListView):
    template_name = "permissions/user_list.html"
    table_class = UserPermissionTable
    enable_page_size_config = True

    def build_filter_query(self):
        query = {}
        form = UserPermFilterForm(data=self.request.GET)
        if form.is_valid():
            for key, value in form.cleaned_data.items():
                value = value.strip()
                if value:
                    query[key] = value

            if 'fullname' in query:
                value = query['fullname']
                value = value.encode('utf-8', 'ignore')
                query['fullname'] = {'$regex': value}
        return query

    def get_qs_count(self):
        return UserPermission.objects.all().count()

    def get_queryset(self):
        query = self.build_filter_query()
        users = UserPermission.objects.raw_query(query)
        user_msgs = [user.json() for user in users if user]
        return user_msgs

    def get_filter_form(self):
        return UserPermFilterForm(data=self.request.GET)


class UserPermUpdateView(JSONResponseMixin, TemplateView):
    template_name = 'permissions/user_update.html'
    post_form = UserPermUpdateForm

    def get_context_data(self, **kwargs):
        context = super(UserPermUpdateView, self).get_context_data(**kwargs)

        entity_id = self.request.GET.get('entity_id')
        if not entity_id:
            raise Http404
        user = UserPermission.objects.get_by_id(entity_id)
        if not user:
            raise Http404
        initial = user.json()

        context['form'] = self.post_form(
            initial=initial, request=self.request,
        )
        return context

    def post(self, request):
        form = self.post_form(data=request.POST)
        if form.is_valid():
            form.save()
            return self.render_json_response({
                'state': True, 'redirect_url': reverse('permissions:users')
            })
        else:
            return self.render_json_response({
                'state': False, 'error': errors_to_dict(form.errors)
            })


####################
# group permission #
####################


class GroupPermListView(JSONResponseMixin, OriginListView):
    template_name = 'permissions/group_list.html'
    table_class = GroupPermissionTable

    def get_queryset(self):
        groups = GroupPermission.objects.raw_query({})
        return [group.json() for group in groups if group]

    def get_context_data(self, **kwargs):
        return {'table': self.table_class(self.get_queryset())}

    def delete(self, request):
        request.DELETE = QueryDict(request.body)
        entity_id = request.DELETE.get('entity_id')
        if not entity_id:
            return self.render_json_response({
                'state': False,
                'error': 'entity_id is required!'
            }, status=400)
        group = GroupPermission.objects.get_by_id(entity_id)
        group.delete()
        return self.render_json_response({'state': True})


class GroupPermUpdateView(JSONResponseMixin, TemplateView):
    template_name = 'permissions/group_update.html'
    post_form = GroupPermUpdateForm

    def get_context_data(self, **kwargs):
        context = super(GroupPermUpdateView, self) \
            .get_context_data(**kwargs)

        entity_id = self.request.GET.get('entity_id')
        if not entity_id:
            raise Http404

        group = GroupPermission.objects.get_by_id(entity_id)
        if not group:
            raise Http404

        context['form'] = self.post_form(
            initial=group.json(), request=self.request,
        )
        return context

    def post(self, request):
        form = self.post_form(data=request.POST)
        if form.is_valid():
            form.save()
            return self.render_json_response({
                'state': True, 'redirect_url': reverse('permissions:groups')
            })
        else:
            return self.render_json_response({
                'state': False, 'error': errors_to_dict(form.errors)
            })


class GroupPermCreateView(GroupPermUpdateView):
    def get_context_data(self, **kwargs):
        return {'form': self.post_form(
            request=self.request,
            disable_name=False,
        )}


########################
# uri group permission #
########################


class UriGroupPermListView(JSONResponseMixin, OriginListView):
    template_name = 'permissions/uri_group_list.html'
    table_class = UriGroupPermissionTable
    enable_page_size_config = False

    def get_queryset(self):
        uri_groups = UriGroupPermission.objects.raw_query({})
        return [uri.json() for uri in uri_groups if uri]

    def get_context_data(self, **kwargs):
        return {'table': self.table_class(self.get_queryset())}

    def delete(self, request):
        request.DELETE = QueryDict(request.body)
        entity_id = request.DELETE.get('entity_id')
        if not entity_id:
            return self.render_json_response({
                'state': False,
                'error': 'entity_id is required!'
            }, status=400)
        group = UriGroupPermission.objects.get_by_id(entity_id)
        group.delete()
        return self.render_json_response({'state': True})


class UriGroupPermUpdateView(JSONResponseMixin, TemplateView):
    template_name = 'permissions/uri_group_update.html'
    post_form = UriGroupPermUpdateForm

    def get_context_data(self, **kwargs):
        context = super(UriGroupPermUpdateView, self).get_context_data(
            **kwargs)

        entity_id = self.request.GET.get('entity_id')
        if not entity_id:
            raise Http404

        uri_group = UriGroupPermission.objects.get_by_id(entity_id)
        if not uri_group:
            raise Http404

        initial = uri_group.json()
        initial['uris'] = '\n'.join(initial['uris'])
        context['form'] = self.post_form(
            initial=initial,
            request=self.request,
        )
        return context

    def post(self, request):
        form = self.post_form(
            data=request.POST,
        )
        if form.is_valid():
            form.save()
            return self.render_json_response({
                'state': True,
                'redirect_url': reverse('permissions:uri_groups')
            })
        else:
            return self.render_json_response({
                'state': False, 'error': errors_to_dict(form.errors)
            })


class UriGroupPermCreateView(UriGroupPermUpdateView):
    def get_context_data(self, **kwargs):
        return {'form': self.post_form(
            request=self.request,
            disable_name=False,
        )}
