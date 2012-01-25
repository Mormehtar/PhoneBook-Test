# -*- encoding: utf-8 -*-

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.utils.text import capfirst
from django.db.models.base import ModelBase
from django.conf import settings

#from django import template
#from django.conf import settings
#from pymorphy import get_morph

#morph = get_morph(settings.PYMORPHY_DICTS['ru']['dir'])

#register = template.Library()
#
#@register.filter
#def plural_from_object(source, object):
#    l = len(object[0])
#    if 1 == l:
#        return source
#    return morph.pluralize_inflected_ru(source.upper(), l).lower()

class I18nLabel():
    def __init__(self, function):
        self.target = function
        self.app_label = u''

    def rename(self, f, name = u''):
        def wrapper(*args, **kwargs):
            extra_context = kwargs.get('extra_context', {})
            if 'delete_view' != f.__name__:
                extra_context['title'] = self.get_title_by_name(f.__name__, args[1], name)
            else:
                extra_context['object_name'] = name
            kwargs['extra_context'] = extra_context
            return f(*args, **kwargs)
        return wrapper

    def get_title_by_name(self, name, request={}, obj_name = u''):
        if 'add_view' == name:
            return _('Add %s') % obj_name
        elif 'change_view' == name:
            return _('Change %s') % obj_name
        elif 'changelist_view' == name:
            if 'pop' in request.GET:
                title = _('Select %s')
            else:
                title = _('Select %s to change')
            return title % obj_name
        else:
            return ''

    def wrapper_register(self, model_or_iterable, admin_class=None, **option):
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if admin_class is None:
                admin_class = type(model.__name__+'Admin', (admin.ModelAdmin,), {})
            self.app_label = model._meta.app_label
            current_name = model._meta.verbose_name
            admin_class.add_view = self.rename(admin_class.add_view, current_name)
            admin_class.change_view = self.rename(admin_class.change_view, current_name)
            admin_class.changelist_view = self.rename(admin_class.changelist_view, current_name)
            admin_class.delete_view = self.rename(admin_class.delete_view, current_name)
        return self.target(model, admin_class, **option)

    def wrapper_app_index(self, request, app_label, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['title'] = _('%s administration') % _(capfirst(app_label))
        return self.target(request, app_label, extra_context)

    def register(self):
        return self.wrapper_register

    def index(self):
        return self.wrapper_app_index


#def message_wrapper(f):
#    def wrapper(self, request, message):
#        gram_info = morph.get_graminfo( self.model._meta.verbose_name.upper() )[0]
#        if -1 != message.find(u'"'):
#            """
#            Message about some action with a single element
#            """
#            words = [w for w in re.split("( |\\\".*?\\\".*?)", message) if w.strip()]
#            form = gram_info['info'][:gram_info['info'].find(',')]
#            message = u' '.join(words[:2])
#            for word in words[2:]:
#                if not word.isdigit():
#                    word = word.replace(".", "").upper()
#                    try:
#                        info = morph.get_graminfo(word)[0]
#                        if u'КР_ПРИЛ' != info['class']:
#                            word = morph.inflect_ru(word, form).lower()
#                        elif 0 <= info['info'].find(u'мр'):
#                            word = morph.inflect_ru(word, form, u'КР_ПРИЧАСТИЕ').lower()
#                        else:
#                            word = word.lower()
#                    except IndexError:
#                        word = word.lower()
#                message += u' ' + word
#        else:
#            """
#            Message about some action with a group of elements
#            """
#            num = int(re.search("\d", message).group(0))
#            words = message.split(u' ')
#            message = words[0]
#            pos = gram_info['info'].find(',')
#            form = gram_info['info'][:pos] + u',' + u'ед' if 1 == num else u'мн'
#            for word in words[1:]:
#                if not word.isdigit():
#                    word = word.replace(".", "").upper()
#                    info = morph.get_graminfo(word)[0]
#                    if u'КР_ПРИЛ' != info['class']:
#                        word = morph.pluralize_inflected_ru(word, num).lower()
#                    else:
#                        word = morph.inflect_ru(word, form, u'КР_ПРИЧАСТИЕ').lower()
#                message += u' ' + word
#
#        message += '.'
#        return f(self, request, capfirst(message))
#    return wrapper
  