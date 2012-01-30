# Create your views here.
from os import path

from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _

from mysite.users.forms import MongoSearchForm
from mysite.users import models
import pymongo


class empoyee():
    worker = u''
    skills = u''

    def __init__(self, w, s):
        self.worker = w
        self.skills = s


def index(request):
    title = _(u'Skilled employees search engine!')
    searchTitle = title
    send = _(u'Search')
    ChangeBase = _(u'Enter base')
    WayToAdmin = path.join(request.path + 'admin/')
    noresult = _(u'Nothing was found')
    CleanEmployees = []
    if request.method == 'POST':
        form = MongoSearchForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            UnCleanEmployees = models.MongoGetBySkill(cd['search'])
            for Employee in UnCleanEmployees:
                try :
                    CleanEmployees.append(
                        empoyee(models.UserProfile.objects.get(username__exact=Employee[0]),
                        Employee[1]))
                except:
                    pass
            return render_to_response('search_form.html', {
                'title':title,
                'searchTitle':searchTitle,
                'form':MongoSearchForm,
                'send':send,
                'request':True,
                'result':CleanEmployees,
                'noresult':noresult,
                'WayToAdmin':WayToAdmin,
                'ChangeBase':ChangeBase
            })
    else:
        return render_to_response('search_form.html', {
            'title':title,
            'searchTitle':searchTitle,
            'form':MongoSearchForm,
            'send':send,
            'request':False,
            'result':CleanEmployees,
            'noresult':noresult,
            'WayToAdmin':WayToAdmin,
            'ChangeBase':ChangeBase
        })



