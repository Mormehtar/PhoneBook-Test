# -*- encoding: utf-8 -*-

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
        form = MongoSearchForm(request.POST)
        if form.is_valid():
            employees = find_emloyees_by_skills(form)
            render = {'request':True, 'result':employees, 'form':form}
    return render_to_response('search_form.html', {'render':render}, context_instance=RequestContext(request))



def find_emloyees_by_skills(form):
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
