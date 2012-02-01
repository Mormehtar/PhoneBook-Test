# -*- encoding: utf-8 -*-

# Create your views here.
from os import path

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from mysite.users.forms import MongoSearchForm
from mysite.users import models
import pymongo

from django.template.context import RequestContext

def index(request):
    render = {'form':MongoSearchForm}
    if request.method == 'POST':
        Form = MongoSearchForm(request.POST)
        if Form.is_valid():
            Employees = FindEmloyeesBySkills(Form)
            render = {'request':True, 'result':Employees, 'form':Form}
    return render_to_response('search_form.html', {'render':render}, context_instance=RequestContext(request))



def FindEmloyeesBySkills(form):
    cd = form.cleaned_data
    employees_in_mogodb_format = models.mongo_get_by_skill(cd['search'])
    employees = []
    for employee in employees_in_mogodb_format:
        try:
            employees.append({
                'worker':models.UserProfile.objects.get(username__exact=employee[0]),
                'skills':employee[1]
            })
        except: # On case of MongoDB-SQLite3 bases inconsistency
            pass
    return employees
