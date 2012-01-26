import string
import pymongo

from django import forms
from django.utils.translation import ugettext_lazy as _

from mysite.users import models


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ['username', 'last_name', 'first_name', 'surname', 'myemail',
                  'mob_tel', 'work_tel', 'department', 'position', 'is_superuser']

    skills = forms.CharField(max_length=255, label=_(u'MadSkillz'), widget=forms.Textarea(), required=False)


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.initial[u'skills'] = u'\n'.join(self.instance.skills)


    def save(self, *args, **kwargs):
        skills = [s for s in (k.strip(string.whitespace) for k in self.cleaned_data['skills'].split(u'\n')) if s!=u'']

        Message = MakeMessage(self)
        ToList = models.GetListOfAdresses(Meta.model.PK)

        self.instance.skills = skills

        super(UserProfileForm, self).save(*args, **kwargs)
        return self.instance


def MakeMessage(ChangedForm):
    ChangedData = ChangedForm.changed_data
    Model = ChangedForm.model
    Message = _(u'The following data of User %s') % Model.GetModelFieldByName('last_name').strip(string.whitespace) \
        + u' %s' % Model.GetModelFieldByName('first_name').strip(string.whitespace) \
        + u' %s' % Model.GetModelFieldByName('surname').strip(string.whitespace) \
        + u' (%s) were changed:\n' % Model.GetModelFieldByName('username')
    for FieldName in ChangedData:
        if not u'skills':
            Message += GetModelFieldChange(Model, FieldName)
        else:
            Message += GetSkillsChanges(self.instance.skills, skills, Message)
    return Message


def GetSkillsChanges(SkillsBefore, SkillsAfter, Message):
    NewSkills = SkillsDifference(SkillsAfter, SkillsBefore)
    DeletedSkills = SkillsDifference(SkillsBefore, SkillsAfter)
    Message = GetDeletedSkillsMessage(DeletedSkills, Message)
    Message = GetFinalSkillsMessageWithNew(Message, NewSkills, SkillsAfter)
    return Message


def GetDeletedSkillsMessage(DeletedSkills, Message):
    if len(DeletedSkills) > 0:
        Message += _(u'The following skills were deleted:\n')
        for Skill in DeletedSkills:
            Message += u'\t' + Skill + u'\n'
    return Message


def GetFinalSkillsMessageWithNew(Message, NewSkills, SkillsAfter):
    if len(NewSkills) > 0:
        Message += _(u'Final list of skills is:\n')
        for Skill in SkillsAfter:
            Message += u'\t' + Skill
            if Skill in NewSkills:
                Message += u' (added!)'
        Message += u'\n'
    return Message


def SkillsDifference (skills1, skills2):
    return set(skills1) - set(skills2)


def GetModelFieldChange(model, FieldName):
    return u'\t' + GetModelFieldData(FieldName).verbouse_name + u': ' + GetModelFieldData(FieldName) + u'\n'

