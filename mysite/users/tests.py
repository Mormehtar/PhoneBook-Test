# -*- encoding: utf-8 -*-

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""

#from selenium.webdriver.firefox.webdriver import WebDriver
#from django.test import LiveServerTestCase

from django.test.client import Client

from django.test import TestCase
from django.core import mail

import pymongo
import time
from django.utils.unittest.case import skip

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


class MySeleniumTests(LiveServerTestCase):
    fixtures = ['user-data.json']

    @classmethod
    def setUpClass(cls):
        cls.new_users = create_test_base()
        cls.selenium = WebDriver()
        super(MySeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        clear_test_base()
        super(MySeleniumTests, cls).tearDownClass()
        cls.selenium.quit()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(u'NamelessHeadOfCommon')
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('password')
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()


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


    def test_admin_work(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200, "Admin doesn't answer")


    def test_positions_work(self):
        response = self.client.get('/admin/users/position/')
        self.assertEqual(response.status_code, 200, "Positions don't answer")


    def test_login(self):
        self.assertTrue(self.client.login(username=u'NamelessHeadOfCommon', password='password'), 'Login failed!')


    def test_position1_work(self):
#        print self.client.login(username=u'NamelessHeadOfCommon', password='password')
        c = Client(enforce_csrf_checks = True, follow = True)
        response = c.post('/admin/', {'username':u'NamelessHeadOfCommon', 'password':'password'})
        print
        print
        print response.context
        print
        print
        response = c.get('/admin/users/position/1/')
        print
        print
        print response.context
        print
        print
        print response
        print
        print



        self.assertEqual(response.status_code, 200, "Position 1 don't answer")


#    def test_departments_work(self):
#        response = self.client.get('/admin/users/department/')
#        self.assertEqual(response.status_code, 200, "Departments don't answer")
#
#    def test_department1_work(self):
#        print self.client.login(username=u'NamelessHeadOfCommon', password='password')
#        response = self.client.get('/admin/users/department/1/')
#        print response.context
#        self.assertEqual(response.status_code, 200, "Department 1 don't answer")




@skip('Too low abstraction')
class TestForms(TestCase):

    def setUp(self):
        self.new_users = create_test_base()

    def tearDown(self):
        clear_test_base()


    def test_new_employee_saving(self):
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department'])
        new_user.is_valid()
        new_user.save()
        self.assertIsNotNone(models.UserProfile.objects.filter(username=u'Newuser'), u"New user wasn't created")


    def test_new_employee_in_empty_department_mailing(self):
        mail.outbox = []
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_empty_department'])
        new_user.is_valid()
        new_user.save()
        time.sleep(0.1)
        adresses = []
        for letter in mail.outbox:
            adresses.append(letter.to)
        self.assertIn([u'new@user.com'], adresses, u"Letter with password didn't come")
        self.assertIn([u'nameless@head.com'], adresses, u"Letter didn't come to boss working in another department")
        self.assertIn([u'petr@petrov.com'], adresses, u"Letter didn't come to boss of headless department")
        self.assertEqual(len(mail.outbox), 3, u'Wrong number of letters')


    def test_new_employee_in_common_department_mailing(self):
        mail.outbox = []
        new_user = forms.UserProfileAdminForm(self.new_users['data_for_new_user_in_common_department'])
        new_user.is_valid()
        new_user.save()
        time.sleep(0.1)
        adresses = []
        for letter in mail.outbox:
            adresses.append(letter.to)
        self.assertIn([u'new@user.com'], adresses, u"Letter with password didn't come")
        self.assertIn([u'ivan@ivanov.com'], adresses, u"Letter didn't come to a colegue")
        self.assertIn([u'nameless@head.com'], adresses, u"Letter didn't come to boss working in another department")
        self.assertIn([u'petr@petrov.com'], adresses, u"Letter didn't come to boss of headless department")
        self.assertEqual(len(mail.outbox), 4, u'Wrong number of letters')


