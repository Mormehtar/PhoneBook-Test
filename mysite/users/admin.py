# -*- encoding: utf-8 -*-

from django.contrib import admin

from mysite.users import models
from mysite.users import forms
from mysite import trans


admin.site.register = trans.I18nLabel(admin.site.register).register()
admin.site.app_index = trans.I18nLabel(admin.site.app_index).index()


class UserProfileAdmin(admin.ModelAdmin):
    form = forms.UserProfileAdminForm
    search_fields = ('first_name', 'last_name', 'surname')
    list_filter = ('position', )


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head')


admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Position)
admin.site.register(models.Department, DepartmentAdmin)
