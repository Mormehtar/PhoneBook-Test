# -*- encoding: utf-8 -*-

from django.contrib import admin

from mysite.users import models
from mysite.users import forms
from mysite import trans


admin.site.register = trans.I18nLabel(admin.site.register).register()
admin.site.app_index = trans.I18nLabel(admin.site.app_index).index()

#admin.ModelAdmin.message_user = trans.message_wrapper(admin.ModelAdmin.message_user)


class UserProfileAdmin(admin.ModelAdmin):
#    list_display = (
#        'first_name','last_name','surname','email',
#        'mob_tel','work_tel','department','position'
#        )
    form = forms.UserProfileForm
    search_fields = ('first_name','last_name','surname')
    list_filter = ('position',)
#    exclude = ['is_staff', 'is_active', 'last_login', 'date_joined', 'groups', 'user_permissions']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'head')


#class PositionAdmin(admin.ModelAdmin):
#    list_display = ('name',)

admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.Position)
admin.site.register(models.Department,DepartmentAdmin)
