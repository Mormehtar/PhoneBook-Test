import string
import pymongo

from django import forms
from django.utils.translation import ugettext as _

from mysite.users import models
from mysite.users import tasks


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ['username', 'last_name', 'first_name', 'surname', 'myemail',
                  'mob_tel', 'work_tel', 'department', 'position', 'is_superuser']

    skills = forms.CharField(max_length=255, label=_(u'MadSkillz'), widget=forms.Textarea(), required=False, help_text=_(u'Each skill from new line'))


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.initial[u'skills'] = u'\n'.join(self.instance.skills)


    def save(self, *args, **kwargs):
        self.SendNotifications()
        self.instance.skills = self.ParcedSkills()
        super(UserProfileForm, self).save(*args, **kwargs)
        return self.instance


    def ParcedSkills(self):
        return [parced_skills_cleared_of_whitespaces for parced_skills_cleared_of_whitespaces in (parced_skills_with_whitespaces.strip(string.whitespace) for parced_skills_with_whitespaces in self.cleaned_data['skills'].split(u'\n')) if parced_skills_cleared_of_whitespaces!=u'']

    def SendNotifications(self):
        ChangedUserReference = self.ChangedUserReference()
        Message = MakeMessage(self, ChangedUserReference)

        tasks.MakeSending.delay(
            ConstMessagePart=Message,
            ChangedUserDepartment=self.instance.department,
            ChangedUserReference=ChangedUserReference)


    def ChangedUserReference(self):
        model = self.Meta.model
        if self.is_bound:
            return models.FormReference(
                self.instance.last_name,
                self.instance.first_name,
                self.instance.surname,
                self.instance.username)
        else:
            return models.FormReference(
                model.GetModelFieldByName('last_name'),
                model.GetModelFieldByName('first_name'),
                model.GetModelFieldByName('surname'),
                model.GetModelFieldByName('username'))


def MakeMessage(ChangedForm, ChangedUser):
    ChangedData = ChangedForm.changed_data
    Message = _(u'the following data of User %s has been changed:\n') % (ChangedUser)
    for FieldName in ChangedData:
        if not (FieldName == u'skills'):
            Message += GetModelFieldChange(ChangedForm, FieldName)
    if u'skills' in ChangedData:
        Message += GetSkillsChanges(ChangedForm.instance.skills, ChangedForm.ParcedSkills())
    return Message


def GetSkillsChanges(SkillsBefore, SkillsAfter):
    NewSkills = SkillsDifference(SkillsAfter, SkillsBefore)
    DeletedSkills = SkillsDifference(SkillsBefore, SkillsAfter)
    Message = GetDeletedSkillsMessage(DeletedSkills)
    Message += GetFinalSkillsMessageWithNew(NewSkills, SkillsAfter)
    return Message


def GetDeletedSkillsMessage(DeletedSkills):
    Message = u''
    if len(DeletedSkills) > 0:
        Message = _(u'The following skills were deleted:\n')
        for Skill in DeletedSkills:
            Message += u'\t' + Skill + u'\n'
    return Message


def GetFinalSkillsMessageWithNew(NewSkills, SkillsAfter):
    Message = u''
    if len(NewSkills) > 0:
        Message = _(u'Final list of skills is:\n')
        for Skill in SkillsAfter:
            Message += u'\t' + Skill
            if Skill in NewSkills:
                Message += _(u' (added!)')
            Message += u'\n'
    return Message


def SkillsDifference (skills1, skills2):
    return set(skills1) - set(skills2)


def GetModelFieldChange(form, FieldName):
    return u'\t%s: %s\n' \
        % (form.instance.GetModelFieldByName(FieldName).verbose_name,
           form.cleaned_data[FieldName])


class MongoSearchForm(forms.Form):
    search = forms.CharField(max_length=255, label=_(u'Search skill'), required=False)