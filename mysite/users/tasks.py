# -*- encoding: utf-8 -*-

from celery.task import task

from django.core.mail import send_mail
from django.template.loader import render_to_string

from mysite.users import models


@task()
def make_async_sending(message_context, changed_user_department, title):
    to = models.get_list_of_addressees_and_names(changed_user_department)
    for person in to:
        message_context['adressee'] = person['person']
        message = render_to_string('mail_template',message_context)
        send_mail(title, message, u'dont@reply.ua',[person['email']])


class CeleryAsyncMailer():
    sending_function = make_async_sending.delay

    def send(self,message_context, changed_user_department, title):
        self.sending_function(message_context, changed_user_department, title)

    def swich_test_mode(self, test):
        if test:
            self.sending_function = make_async_sending
        else:
            self.sending_function = make_async_sending.delay

celery_async_mailer = CeleryAsyncMailer()
