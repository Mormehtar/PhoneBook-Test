# -*- encoding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import models as auth_models
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail
from django.core.validators import RegexValidator
import pymongo

import string

# Create your models here.

WRONG_NUMBER = _(u'Wrong phone number')
COUNTRY_CODE = r'(\+?\d)'
CITY_CODE = r'(\(\d{1,5}\))'
PHONE_NUMBER = r'((\d{1,3}[\s-]?){1,3})'
CONCATENATOR = r'?\s*'
PHONE_NUMBER_REGEXP = '^'\
                      + COUNTRY_CODE\
                      + CONCATENATOR\
                      + CITY_CODE\
                      + CONCATENATOR\
                      + PHONE_NUMBER\
                      + '$'

class Department(models.Model):
    name = models.CharField(max_length = 30, verbose_name=_(u'Name'))
    head = models.ForeignKey(
        "UserProfile", related_name='head',
        null='true', blank='true', verbose_name=_(u'Head')
    )

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'department')
        verbose_name_plural = _(u'departments')


class Position(models.Model):
    name = models.CharField(max_length = 30, verbose_name=_(u'Position'))

    def __unicode__(self):
        return u'%s' % self.name

    class Meta:
        verbose_name = _(u'position')
        verbose_name_plural = _(u'positions')


class UserProfile(User):
    surname = models.CharField(max_length = 30, blank=True, null=True, verbose_name=_(u'Surname'))
    mob_tel = models.CharField(
        max_length = 30, blank=True, null=True,
        verbose_name=_(u'Mobile telephone'),
        validators=[RegexValidator(PHONE_NUMBER_REGEXP,WRONG_NUMBER)]
    )
    work_tel = models.CharField(
        max_length = 30, blank=True, null=True,
        verbose_name=_(u'Work telephone'),
        validators=[RegexValidator(PHONE_NUMBER_REGEXP,WRONG_NUMBER)]
    )
    myemail = models.EmailField(verbose_name=_(u'E-mail'))
    department = models.ForeignKey(Department, verbose_name=_(u'Department'))
    position = models.ForeignKey(Position, verbose_name=_(u'Position'))

    skills = []


    class Meta:
        verbose_name = _(u'employee')
        verbose_name_plural = _(u'empolyees')


    def get_model_field_by_name(self, field_name):
        return self._meta.get_field_by_name(field_name)[0]


    def __unicode__(self):
        return u'%s %s в %s' % (form_reference(self.last_name, self.first_name, self.surname, self.username),
                                self.position.name, self.department.name)


    def __init__(self, *args, **kwargs):
        super(UserProfile, self).__init__(*args, **kwargs)
        self.skills = mongo_read(self.username)


    def save(self, *args, **kwargs):
        self.generate_pass_if_needed()
        super(UserProfile, self).save(*args, **kwargs)
        mongo_write(self.username, self.skills)


    def generate_pass_if_needed(self):
        if not self.pk:
            password = auth_models.UserManager().make_random_password()
            message = _(u'You have signed on mysite.\nYour username is: %(username)s\nYour password is: %(password)s\n') \
                % {'username': self.username, 'password': password}
            header = _(u'Your password on mysite')
            send_mail(header, message, u'dont@reply.ua', [self.myemail])
            self.set_password(password)


def get_list_of_addressees_and_names(user_department):
    addressees = get_list_of_addressees(user_department)
    return [{
        'email': addressee.myemail,
        'person':form_reference(addressee.last_name,addressee.first_name,addressee.surname,addressee.username)
    } for addressee in addressees]


def get_list_of_addressees(user_department):
    boss_names = set()
    for boss in Department.objects.all():
        boss_names.add(boss.head)
    colleagues = set(UserProfile.objects.filter(department=user_department))
    addressees = (boss_names | colleagues)
    addressees.discard(None) # On case of headless departments
    return addressees


def form_reference(last_name,first_name,surname,username):
    if len(last_name)+len(first_name)+len(surname) :
        reference = ((last_name + u' ' + first_name).strip(string.whitespace) + u' ' + surname).strip(string.whitespace)
    else:
        reference = username
    return reference


def mongo_read(name):
    connection = pymongo.Connection()
    temp_skills = connection.test_db['madskillz'].find_one({u'id':name})
    connection.end_request()
    if temp_skills:
        return temp_skills[u'skills']
    else:
        return []


def mongo_write(name, skills):
    connection = pymongo.Connection()
    connection.test_db['madskillz'].find_and_modify(
        query={u'id':name},upsert=True,update={'$set' : {u'skills' : skills}})
    connection.end_request()


def mongo_get_by_skill(skill):
    connection = pymongo.Connection()
    result = connection.test_db['madskillz'].find({u'skills':skill})
    retvalue = []
    for doc in result:
        retvalue.append([doc[u'id'],', '.join(doc[u'skills'])])
    return retvalue