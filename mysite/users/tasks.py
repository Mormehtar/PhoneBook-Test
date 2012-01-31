# -*- encoding: utf-8 -*-

from celery.task import task

from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from mysite.users import models
#from mysite.users import forms

#from mysite.users import models

@task()
def MakeSending(ConstMessagePart, ChangedUserDepartment, title):
    To = models.get_list_of_addresses_and_names(ChangedUserDepartment)
    for person in To:
        header = u'Уважаемый, %s, вы получили это письмо потому, что ' % person['person']
        message = header + ConstMessagePart
        AsyncSendEmail.delay(title, message, u'dont@reply.ua',person['email'])

@task()
def AsyncSendEmail(Title,Message,From,To):
    send_mail(Title, Message, From,[To])