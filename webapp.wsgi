#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os, sys

os.environ["CELERY_LOADER"] = "django"
sys.path.append('/usr/local/lib/python2.7/dist-packages')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler() 
