# -*- encoding: utf-8 -*-

from celery.task import task

from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from mysite.users import models
#from mysite.users import forms

#from mysite.users import models

@task()
def make_sending(const_message_part, changed_user_department, title):
    To = models.get_list_of_consignees_and_names(changed_user_department)
    for person in To:
        header = u'Уважаемый, %s, вы получили это письмо потому, что ' % person['person']
        message = header + const_message_part
        async_send_email.delay(title, message, u'dont@reply.ua',person['email'])

@task()
def async_send_email(title,message,from_,to):
    send_mail(title, message, from_,[to])