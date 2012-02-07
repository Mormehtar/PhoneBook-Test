# -*- encoding: utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""

from django.test import TestCase
from django.core import mail

import pymongo

from mysite import settings
from mysite.users import models
from mysite.users import forms
from mysite.users import tasks

def create_test_base():

    common_department = models.Department(name=u'Common')
    common_department.save()
    headless_department = models.Department(name=u'Headless')
    headless_department.save()
    empty_department = models.Department(name=u'Empty but with head')
    empty_department.save()
    left_department = models.Department(name=u'Left department')
    left_department.save()

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
        is_superuser = True,
        department=common_department,
        position=position1
    )
    head_of_common.save()
    head_of_common.set_password('password')
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

    employee_of_left_department = models.UserProfile(
        username=u'LeftMan',
        last_name=u'Leva',
        first_name=u'Lvov',
        surname=u'',
        myemail=u'left@adress.com',
        mob_tel=u'',
        work_tel=u'',
        department=left_department,
        position=position1
    )
    employee_of_left_department.save()

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

    tasks.celery_mailing = tasks.make_async_sending

    return {
        'data_for_new_user_in_empty_department':data_for_new_user_in_empty_department,
        'data_for_new_user_in_common_department':data_for_new_user_in_common_department}


def clear_test_base():
    connection = pymongo.Connection()
    connection.test_db[settings.MONGODB_DOCUMENT].remove()
    connection.end_request()
    settings.MONGODB_DOCUMENT = 'madskillz'
    tasks.celery_mailing = tasks.make_async_sending.delay

def search_response(test, search):
    response = test.client.post('', {'search': search})
    return response.context['render']



TEMPLATE_MESSAGE = ur"""Уважаемый, %s, вы получили это письмо потому, что the following data of User %s has been changed:%s
The following skills were deleted:%s
Final list of skills is:%s
"""

def get_change_mail_body(address, changeduser, strlist):
    first_recipient = models.UserProfile.objects.get(myemail=address)
    return TEMPLATE_MESSAGE % (
        models.form_reference(
            first_recipient.last_name, first_recipient.first_name,
            first_recipient.surname, first_recipient.username),
        changeduser, strlist[0], strlist[1], strlist[2])


def make_changed_form(form,instance,changes):
    user = form(instance=instance)
    user_data = {}
    for dataname in user.changed_data:
        user_data[dataname] = user[dataname].value()
    for dataname in changes:
        user_data[dataname] = changes[dataname]
    return form(user_data, instance=instance)


def get_list_of_addresses():
    adresses = []
    for letter in mail.outbox:
        adresses.append(letter.to)
    return adresses


def save_form(form):
    form.is_valid()
    form.save()


class TestSite(TestCase):

    def setUp(self):
        self.new_users = create_test_base()

    def tearDown(self):
        clear_test_base()


    def test_skills_search(self):
        result = search_response(self, u'1')
        self.assertEqual(len(result['result']), 1, 'Wrong number of answers found!')
        self.assertEqual(result['result'][0]['skills'], u'1, 2, 3', 'Wrong answer found')
        self.assertEqual(unicode(result['result'][0]['worker']), u'Ivan Ivanov Ivanovich Position 2 в Common', 'Wrong answer found')


    def test_skills_multiple_result(self):
        result = search_response(self, u'2')
        self.assertEqual(len(result['result']), 2, 'Wrong number of answers found!')


    def test_skills_not_found(self):
        result = search_response(self, u'123')
        self.assertEqual(len(result['result']), 0, 'Wrong number of answers found!')
        self.assertTrue(result['request'], 'Wrong request sign')


    def test_skills_start(self):
        response = self.client.get('')
        self.assertNotIn('result',response.context['render'],'Wrong start page')


    def test_login(self):
        self.assertTrue(self.client.login(username=u'NamelessHeadOfCommon', password='password'), 'Login failed!')


class TestForms(TestCase):

    def check_mailing_list_recipients(self, list):
        self.assertEqual(len(mail.outbox), len(list), u'Wrong number of letters')
        adresses = get_list_of_addresses()
        for adr in list:
            self.assertIn([adr],adresses)

    def setUp(self):
        self.new_users = create_test_base()

    def tearDown(self):
        clear_test_base()


    def test_new_employee_saving(self):
        save_form(forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department']))
        self.assertIsNotNone(models.UserProfile.objects.filter(username=u'Newuser'), u"New user wasn't created")


    def test_new_employee_in_empty_department_mailing(self):
        mail.outbox = []
        save_form(forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department']))
        self.check_mailing_list_recipients([u'new@user.com',
                                            u'nameless@head.com',
                                            u'petr@petrov.com'])


    def test_new_employee_in_common_department_mailing(self):
        mail.outbox = []
        save_form(forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_common_department']))
        self.check_mailing_list_recipients([u'new@user.com',
                                            u'ivan@ivanov.com',
                                            u'nameless@head.com',
                                            u'petr@petrov.com'])

    def template_change_mailing_test(self, changeddata, uesrname, adresslist, changestrings):
        mail.outbox = []
        user = models.UserProfile.objects.get(username=uesrname)
        save_form(make_changed_form(
            forms.UserProfileAdminForm,
            user,
            changeddata))
        self.check_mailing_list_recipients(adresslist)
        self.assertEqual(mail.outbox[0].body,get_change_mail_body(mail.outbox[0].to[0],
                                                                  models.form_reference(
                                                                      user.last_name, user.first_name,
                                                                      user.surname, user.username),
                                                                  changestrings))



    def test_employee_in_common_department_change_mailing(self):
        self.template_change_mailing_test(
            {'work_tel': u'+7(123)123-45-67', 'skills':u'1\n2\n4'},
            u'Employee1',
            [u'ivan@ivanov.com', u'nameless@head.com', u'petr@petrov.com'],
            [u'\n\tWork telephone: +7(123)123-45-67', u'\n\t3', u'\n\t1\n\t2\n\t4 (added!)']
        )


    def test_employee_in_headless_department_change_mailing(self):
        self.template_change_mailing_test(
            {'work_tel': u'+7(123)123-45-67', 'skills':u'1\n2\n4'},
            u'HeadOfAnother',
            [u'nameless@head.com', u'petr@petrov.com'],
            [u'\n\tWork telephone: +7(123)123-45-67', u'\n\t3', u'\n\t1 (added!)\n\t2\n\t4 (added!)']
        )

class TestTelRegExp(TestCase):

    def test_tel_regexp(self):
        right_phones = [u'1234567', u'+7(123)123-12-12', u'(92557)4563', u'7 (903) 302 20 20', u'+71231212']
        wrong_phones = [u'+ 1234567', u'+7()1231212',u'123-123-123-123',u'127-CALL-US-NOW',u'(123 )123-12-12']
        for phone in right_phones:
            self.assertRegexpMatches(phone,models.PHONE_NUMBER_REGEXP)
        for phone in wrong_phones:
            self.assertNotRegexpMatches(phone,models.PHONE_NUMBER_REGEXP)