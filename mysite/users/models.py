# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
#from settings import EMAIL_BASE
import pymongo

import string

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
    surname = models.CharField(max_length = 30, blank='true', null='true', verbose_name=_(u'Surname'))
    mob_tel = models.DecimalField(
        max_digits=10, decimal_places=0,
        blank='true', null='true', verbose_name=_(u'Mobile telephone')
    )
    work_tel = models.DecimalField(
        max_digits=10, decimal_places=0,
        blank='true', null='true', verbose_name=_(u'Work telephone')
    )
    myemail = models.EmailField(verbose_name=_(u'E-mail'))
    department = models.ForeignKey(Department, verbose_name=_(u'Department'))
    position = models.ForeignKey(Position, verbose_name=_(u'Position'))
    skills = []

    class Meta:
        verbose_name = _(u'employee')
        verbose_name_plural = _(u'empolyees')

    def GetModelFieldByName(self, FieldName):
        return self._meta.get_field_by_name(FieldName)[0]

    def __unicode__(self):
        return u'%s %s в %s' % (FormReference(self.last_name, self.first_name, self.surname, self.username),
                                self.position.name, self.department.name)


    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.skills = MongoRead(self.username)


    def save(self, *args, **kwargs):
        self.GeneratePassIfNeeded()
        super(UserProfile, self).save(*args, **kwargs)
        MongoWrite(self.username, self.skills)


    def GeneratePassIfNeeded(self):
        if not (self.pk):
            password = auth_models.UserManager().make_random_password()
            message = _(u'You have signed on mysite.\nYour username is: %(username)s\nYour password is: %(password)s') \
                % {'username': self.username, 'password': password}
            header = _(u'Your password on mysite')
            send_mail(header, message, u'dont@reply.ua', [self.myemail])
            self.set_password(password)


def MongoRead(name):
    connection = pymongo.Connection()
    temp_skills = connection.test_db['madskillz'].find_one({u'id':name})
    connection.end_request()
    if temp_skills:
        return temp_skills[u'skills']
    else:
        return []

def MongoWrite(name, skills):
    connection = pymongo.Connection()
    connection.test_db['madskillz'].find_and_modify(
        query={u'id':name},upsert=True,update={'$set' : {u'skills' : skills}})
    connection.end_request()


def GetListOfAddresses(PK):
    UserDepartment = UserProfile.objects.get(pk=PK).department
    Bosses = Department.objects.all()
    BossNames = set()
    for Boss in Bosses:
        BossNames.add(Boss.head)
    Colleagues = set(UserProfile.objects.filter(department=UserDepartment))
    Addressants = BossNames | Colleagues
    return [{
        'email': Addressant.myemail,
        'person':FormReference(Addressant.last_name,Addressant.first_name,Addressant.surname,Addressant.username)
    } for Addressant in Addressants]


def FormReference(last_name,first_name,surname,username):
    if len(last_name)+len(first_name)+len(surname)>0 :
        reference = ((last_name + u' ' + first_name).strip(string.whitespace) + u' ' + surname).strip(string.whitespace)
    else:
        reference = username
    return reference