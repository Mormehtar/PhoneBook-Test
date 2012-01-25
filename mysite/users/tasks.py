# -*- encoding: utf-8 -*-
from celery.task import task

#from mysite.users import models


@task()
def NotificationOfChanges(Message):
    send_mail(Message.Title, Message.Message, Message.From,[Message.To])