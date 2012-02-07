# -*- encoding: utf-8 -*-

from celery.task import task

from django.core.mail import send_mail

from mysite.users import models
#from mysite.settings import celery_mailing

def make_sending(const_message_part, changed_user_department, title):
    celery_mailing(const_message_part, changed_user_department, title)


@task()
def make_async_sending(const_message_part, changed_user_department, title):
    To = models.get_list_of_addressees_and_names(changed_user_department)
    for person in To:
        header = u'Уважаемый, %s, вы получили это письмо потому, что ' % person['person']
        message = header + const_message_part
        send_mail(title, message, u'dont@reply.ua',[person['email']])

celery_mailing = make_async_sending.delay