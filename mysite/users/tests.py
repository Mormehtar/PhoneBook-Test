"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""

from django.test import TestCase
from django.core import mail

import pymongo
import time

from mysite import settings
from mysite.users import models
from mysite.users import forms

def create_test_base():

    common_department = models.Department(name=u'Common')
    common_department.save()
    headless_department = models.Department(name=u'Headless')
    headless_department.save()
    empty_department = models.Department(name=u'Empty but with head')
    empty_department.save()

    position1 = models.Position(name=u'Position 1')
    position1.save()
    position2 = models.Position(name=u'Position 2')
    position2.save()

    head_of_common = models.UserProfile(
        username=u'NamelessHeadOfCommon',
        last_name=u'',
        first_name=u'',
        surname=u'',
        myemail=u'nameless@head.com',
        mob_tel=u'',
        work_tel=u'',
        department=common_department,
        position=position1
    )
    head_of_common.save()

    employee_of_common = models.UserProfile(
        username=u'Employee1',
        last_name=u'Ivan',
        first_name=u'Ivanov',
        surname=u'Ivanovich',
        myemail=u'ivan@ivanov.com',
        mob_tel=u'',
        work_tel=u'',
        department=common_department,
        position=position2
    )
    employee_of_common.save()

    employee_of_headless = models.UserProfile(
        username=u'HeadOfAnother',
        last_name=u'',
        first_name=u'',
        surname=u'Petrovich',
        myemail=u'petr@petrov.com',
        mob_tel=u'',
        work_tel=u'',
        department=headless_department,
        position=position1
    )
    employee_of_headless.save()

    common_department.head = head_of_common
    common_department.save()
    empty_department.head = employee_of_headless
    empty_department.save()

    settings.MONGODB_DOCUMENT = 'test_madskillz'
    models.mongo_write(employee_of_common.username,[u'1',u'2',u'3'])
    models.mongo_write(employee_of_headless.username,[u'2',u'2',u'3'])

    data_for_new_user_in_empty_department = {
        'username' : u'Newuser',
        'last_name' : u'New',
        'first_name' : u'Newov',
        'surname' : u'Newovich',
        'myemail' : u'new@user.com',
        'department' : empty_department.id,
        'position': position1.id
    }

    data_for_new_user_in_common_department = {
        'username' : u'Newuser',
        'last_name' : u'New',
        'first_name' : u'Newov',
        'surname' : u'Newovich',
        'myemail' : u'new@user.com',
        'department' : common_department.id,
        'position': position1.id
    }
    return {
        'data_for_new_user_in_empty_department':data_for_new_user_in_empty_department,
        'data_for_new_user_in_common_department':data_for_new_user_in_common_department}


def clear_test_base():
    connection = pymongo.Connection()
    connection.test_db[settings.MONGODB_DOCUMENT].remove()
    connection.end_request()
    settings.MONGODB_DOCUMENT = 'madskillz'


class TestForms(TestCase):

    def setUp(self):
        self.new_users = create_test_base()

    def tearDown(self):
        clear_test_base()


    def test_new_employee_saving(self):
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department'])
        new_user.save()
        self.assertIsNotNone(models.UserProfile.objects.filter(username=u'Newuser'), u"New user wasn't created")


    def test_new_employee_in_empty_department_mailing(self):
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department'])
        new_user.save()
        time.sleep(10)
        adresses = []
        for letter in mail.outbox:
            adresses.append(letter.to)
        self.assertIn(u'new@user.com', adresses, u"Letter with password didn't come")
        self.assertIn(u'nameless@head.com', adresses, u"Letter didn't come to boss working in another department")
        self.assertIn(u'petr@petrov.com', adresses, u"Letter didn't come to boss of headless department")
        self.assertEqual(len(mail.outbox), 3, u'Wrong number of letters')


    def test_new_employee_in_common_department_mailing(self):
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_common_department'])
#        print u'\n New form is bound: ', new_user.is_bound
#        print u'New form is valid: ', new_user.is_valid()
#        print new_user.cleaned_data
#        print self.new_users['data_for_new_user_in_common_department']
#        print new_user.cleaned_data.get('username')
        print new_user.is_valid()
        new_user.save()
        time.sleep(10)
        adresses = []
        for letter in mail.outbox:
            adresses.append(letter.to)
        self.assertIn(u'new@user.com', adresses, u"Letter with password didn't come")
        self.assertIn(u'ivan@ivanov.com', adresses, u"Letter didn't come to a colegue")
        self.assertIn(u'nameless@head.com', adresses, u"Letter didn't come to boss working in another department")
        self.assertIn(u'petr@petrov.com', adresses, u"Letter didn't come to boss of headless department")
        self.assertEqual(len(mail.outbox), 4, u'Wrong number of letters')








