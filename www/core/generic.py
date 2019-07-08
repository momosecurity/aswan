# coding=utf8
from math import ceil

from django.conf import settings
from django_tables2 import SingleTableView, RequestConfig
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

__all__ = (
    "ListView",
)


class PaginatorClass(Paginator):
    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        if number > self.num_pages:
            if number == 1 and self.allow_empty_first_page:
                pass
            else:
                number = self.num_pages
        return number


class PagedFilterTableView(SingleTableView):
    empty_text = u"暂无数据"
    enable_page_size_config = None
    collection_name = None
    paginate_by = 50
    paginator_class = PaginatorClass

    def get_queryset(self):
        """子类重写获取数据源方法"""
        raise Exception("subclass must overwrite get_queryset method")

    def get_table(self, **kwargs):
        paginate_data = {
            "per_page": self.paginate_by or getattr(settings, 'PER_PAGE', 50),
        }
        table = super(PagedFilterTableView, self).get_table(**kwargs)
        table.empty_text = self.get_empty_text()
        RequestConfig(self.request, paginate=paginate_data).configure(table)
        return table

    def get_qs_count(self):
        if self.collection_name:
            raise Exception("please overwrite get_qs_count method")
        return len(self.object_list)

    def _get_page_count(self):
        if self.collection_name:
            paginate_by = self.get_paginate_by(None)
            count = int(ceil(self.get_qs_count() / float(paginate_by)))
        else:
            count = self.get_table().paginator.num_pages or 1
        return count

    def _build_pages(self):
        page_count = self._get_page_count()
        current_page = int(self.request.GET.get('page', 0))
        pages = list(range(1, page_count + 1))
        if page_count > 8:
            pages = pages[:3] + pages[-3:]
        if 1 < current_page < page_count - 1:
            pages.append(current_page - 1)
            pages.append(current_page)
            pages.append(current_page + 1)
        pages = list(set(pages))
        pages.sort()
        new_pages = [pages[0], ] if pages else []
        for i in range(1, len(pages)):
            gap = pages[i] - pages[i - 1]
            if gap >= 3:
                new_pages.append(0)
            elif gap == 2:
                new_pages.append(pages[i] - 1)
            new_pages.append(pages[i])
        return new_pages

    def get_context_data(self, **kwargs):
        context = super(PagedFilterTableView, self).get_context_data(**kwargs)
        context['pages'] = self._build_pages()
        context['filter_form'] = self.get_filter_form()
        context['record_count'] = self.get_qs_count()
        context['page_size'] = str(self.get_paginate_by(None))
        if self.enable_page_size_config:
            context['enable_page_size_config'] = True
            context['page_values'] = self.get_page_values()
        return context

    def get_page_values(self):
        """分页配置"""
        defaults = ['50', '100', '200', '500', '1000']
        return defaults

    def get_paginate_by(self, queryset):
        """获取分页参数"""
        if self.enable_page_size_config:
            paginate_by = self.request.GET.get('page_size') or self.paginate_by
            self.paginate_by = int(paginate_by)
        return self.paginate_by

    def get_filter_form(self):
        """重载该方法返回返回搜索表单对象(django.forms.Form或其子类)"""
        raise Exception("subclass must overwrite get_filter_form method")

    def get_empty_text(self):
        """重载该方法替换空数据时的文字提示"""
        return self.empty_text


ListView = PagedFilterTableView
