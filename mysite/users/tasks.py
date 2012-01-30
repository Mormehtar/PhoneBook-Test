# -*- encoding: utf-8 -*-
from celery.task import task

from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from mysite.users import models
#from mysite.users import forms

#from mysite.users import models

@task()
def MakeSending(ConstMessagePart, ChangedUserDepartment, ChangedUserReference):
    To = models.GetListOfAddresses(ChangedUserDepartment)
    Message = ConstMessagePart + u'\n\n' + GetUnicodeFromListOfDict(To)
    send_mail(u'Тестовое письмо MySite', Message, u'dont@reply.ua',[u'mormehtar@gmail.com'])
    for person in To:
        header = _(u'Dear %s you recieve this letter becouse ') % (person['person'])
        title = _(u'User %s chaged his data on Mysite') % (ChangedUserReference)
        message = header + ConstMessagePart
        AsyncSendEmail.delay(title, message, u'dont@reply.ua',person['email'])

@task()
def AsyncSendEmail(Title,Message,From,To):
    send_mail(Title, Message, From,[To])


def GetUnicodeFromListOfDict(ListOfDict):
    return '\n'.join([ u'%s: %s\n' % (Element['person'], Element['email']) for Element in ListOfDict])