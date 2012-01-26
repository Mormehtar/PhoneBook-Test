# -*- encoding: utf-8 -*-
from celery.task import task

from django.utils.translation import ugettext as _
from django.core.mail import send_mail

from mysite.users import models
#from mysite.users import forms

#from mysite.users import models

@task()
def MakeSending(ConstMessagePart, ChangedUser, ChangedUserReference):
#    a=b
    To = models.GetListOfAddresses(ChangedUser)
    for person in To:
        logger = AsyncSendEmail.get_logger()
        logger.info("Person %s" % (person))
        header = _(u'Dear %s you recieve this letter becouse ' % (person['person']))
        title = _(u'User %s chaged his data on Mysite') % (ChangedUserReference)
        message = header + ConstMessagePart
#        TestMSG = u'Title is: "%s" \n message is: "\n%s\n", adress is "' % (title, message) + person['email'] +u'"'
#        send_mail(u'Test!', TestMSG, u'dont@reply.ua',['mormehtar@gmail.com'])
        AsyncSendEmail.delay(title, message, u'dont@reply.ua',person['email'])
#        AsyncSendEmail(title, message, u'dont@reply.ua',person['email'])

@task()
def AsyncSendEmail(Title,Message,From,To):
#    a=a
#    logger = AsyncSendEmail.get_logger(loglevel='INFO')
##    logger.
#    logger.info("Title %s" % (Title))
#    logger.info("Message %s" % (Message))
#    logger.info("From %s" % (From))
#    logger.info("To %s" % (To))
    send_mail(Title, Message, From,[To])