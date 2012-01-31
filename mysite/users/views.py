# -*- encoding: utf-8 -*-

# Create your views here.
from os import path

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from mysite.users.forms import mongo_search_form
from mysite.users import models
import pymongo


class empoyee():
    worker = u''
    skills = u''

    def __init__(self, w, s):
        self.worker = w
        self.skills = s


def index(request):
    way_to_admin = path.join(request.path + 'admin/')
    if request.method == 'POST':
        form = mongo_search_form(request.POST)
        if form.is_valid():
            Employees = FindEmloyeesBySkills(form)
            return render_to_response('search_form.html', {
                'form':mongo_search_form,
                'request':True,
                'result':Employees,
                'WayToAdmin':way_to_admin,
            })
    else:
        return render_to_response('search_form.html', {
            'form':mongo_search_form,
            'request':False,
            'result':[],
            'WayToAdmin':way_to_admin,
        })


def FindEmloyeesBySkills(form):
    cd = form.cleaned_data
    employees_in_mogodb_format = models.MongoGetBySkill(cd['search'])
    employees = []
    for employee in employees_in_mogodb_format:
        try:
            employees.append(
                empoyee(models.UserProfile.objects.get(username__exact=employee[0]),
                        employee[1]))
        except: # On case of MongoDB-SQLite3 bases inconsistency
            pass
    return employees