# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
import pymongo

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length = 30, verbose_name=_(u'Name'))
    head = models.ForeignKey(
        "UserProfile", related_name='head',
        null='true', blank='true', verbose_name=_(u'Head')
    )

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _(u'department')
        verbose_name_plural = _(u'departments')


class Position(models.Model):
    name = models.CharField(max_length = 30, verbose_name=_(u'Position'))

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        verbose_name = _(u'position')
        verbose_name_plural = _(u'positions')


class UserProfile(User):
    surname = models.CharField(max_length = 30, verbose_name=_(u'Surname'))
    mob_tel = models.DecimalField(
        max_digits=10, decimal_places=0,
        blank='true', null='true', verbose_name=_(u'Mobile telephone')
    )
    work_tel = models.DecimalField(
        max_digits=10, decimal_places=0,
        blank='true', null='true', verbose_name=_(u'Work telephone')
    )
    department = models.ForeignKey(Department, verbose_name=_(u'Department'))
    position = models.ForeignKey(Position, verbose_name=_(u'Position'))
    skills = []

    class Meta:
        verbose_name = _(u'employee')
        verbose_name_plural = _(u'empolyees')

    def __unicode__(self):
        return u'%s %s %s в %s' % (self.first_name, self.last_name,
                                   self.position.name, self.department.name)


    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)

        temp_skills = pymongo.Connection().test_db['madskillz'].find_one({u'id':self.username})
        if temp_skills:
            self.skills = temp_skills[u'skills']
        else:
            self.skills = []


    def save(self, *args, **kwargs):
        if not (self.pk):
            if (self.email):
                password = auth_models.UserManager().make_random_password()
                message = _(u'You have signed on mysite.\nYour username is: %(username)s\nYour password is: %(password)s')\
                          % {'username' : self.username, 'password' : password}
                send_mail(_(u'Your password on mysite'),
                          message,
                          settings.EMAIL_BASE,[self.email])
            else:
                password = u''
            self.set_password(password)
        super(UserProfile, self).save(*args, **kwargs)
        pymongo.Connection().test_db['madskillz'].find_and_modify(
            query={u'id':self.username},
            upsert=True,
            update={'$set' : {u'skills' : self.skills}}
        )
        connection.end_request()
