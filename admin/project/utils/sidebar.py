# -*- coding: utf-8 -*-


from django.urls import reverse, NoReverseMatch


class Menu:
    """Sidebar 菜单栏 数据结构"""
    category = "menu"
    default_icon = 'box'

    def __init__(self, name, value: list, icon=None):
        self.name = name
        self.value = value
        self.icon = icon or self.default_icon

    def __bool__(self):
        return bool(self.value)

    def to_dict(self, permissions=None):
        """
        转换为前端可用的dict结构
        根据permissions列表控制是否展示对应模块
        """

        value = []
        for item in self.value:
            if not item:
                continue

            if isinstance(item, Menu):
                result = item.to_dict(permissions)
                if result['value']:
                    value.append(result)
            else:
                try:
                    path = reverse(item)
                except NoReverseMatch:
                    continue

                if not permissions or path in permissions:
                    value.append(path)

        return {
            'name': self.name,
            'category': self.category,
            'value': value,
            'icon': self.icon,
        }

    def get_leaf_menu(self, value):
        for item in self.value:
            if item == value:
                return self

            if isinstance(item, Menu):
                result = item.get_leaf_menu(value)
                if result:
                    return result


class SubMenu(Menu):
    """Sidebar 二级菜单"""
    category = "submenu"
    default_icon = 'folder'


class LeafMenu(Menu):
    """Sidebar 指向页面的菜单"""
    category = "leaf_menu"
    default_icon = 'minus'
