import string
import pymongo

from django import forms
from django.utils.translation import ugettext_lazy as _

from mysite.users import models


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ['username', 'last_name', 'first_name', 'surname', 'email',
                  'mob_tel', 'work_tel', 'department', 'position', 'is_superuser']

    skills = forms.CharField(max_length=255, label=_(u'MadSkillz'), widget=forms.Textarea(), required=False)


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.initial[u'skills'] = u',\n'.join(self.instance.skills)


    def save(self, *args, **kwargs):
        skills = [s for s in (k.strip(string.whitespace) for k in self.cleaned_data['skills'].split(u',')) if s!=u'']
        self.instance.skills = skills
        super(UserProfileForm, self).save(*args, **kwargs)
        return self.instance
