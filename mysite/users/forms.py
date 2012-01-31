# -*- encoding: utf-8 -*-

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

        self.instance.skills = self.ParseSkills()

        super(UserProfileForm, self).save(*args, **kwargs)
        return self.instance


    def ParseSkills(self):
        return [
            parsed_skills_with_empty_lines for parsed_skills_with_empty_lines in
                (
                    parsed_skills_with_whitespaces.strip(string.whitespace) for parsed_skills_with_whitespaces in
                        self.cleaned_data['skills'].split(u'\n')
                )
            if parsed_skills_with_empty_lines!=u''
        ]

    def SendNotifications(self):
        changed_user_reference = self.GetChangedUserReference()
        const_message_part = MakeMessage(self, changed_user_reference)

        tasks.MakeSending.delay(
            ConstMessagePart=const_message_part,
            ChangedUserDepartment=self.instance.department,
            title=u'Данные сотрудника %s на Mysite были изменены' % changed_user_reference)


    def GetChangedUserReference(self):
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


def MakeMessage(changed_form, changed_user):
    changed_data = changed_form.changed_data
    message = _(u'the following data of User %s has been changed:\n') % (changed_user)
    for field_name in changed_data:
        if not (field_name == u'skills'):
            message += GetModelFieldChange(changed_form, field_name)
    if u'skills' in changed_data:
        message += GetSkillsChanges(changed_form.instance.skills, changed_form.ParseSkills())
    return message


def GetSkillsChanges(skills_before, skills_after):
    new_skills = GetSkillsDifference(skills_after, skills_before)
    deleted_skills = GetSkillsDifference(skills_before, skills_after)
    message = GetDeletedSkillsMessage(deleted_skills)
    message += GetFinalSkillsMessageWithNew(new_skills, skills_after)
    return message


def GetDeletedSkillsMessage(deleted_skills):
    message = u''
    if len(deleted_skills) > 0:
        message = _(u'The following skills were deleted:\n')
        for skill in deleted_skills:
            message += u'\t' + skill + u'\n'
    return message


def GetFinalSkillsMessageWithNew(new_skills, skills_after):
    message = u''
    if len(new_skills) > 0:
        message = _(u'Final list of skills is:\n')
        for skill in skills_after:
            message += u'\t' + skill
            if skill in new_skills:
                message += _(u' (added!)')
            message += u'\n'
    return message


def GetSkillsDifference (skills1, skills2):
    return set(skills1) - set(skills2)


def GetModelFieldChange(form, field_name):
    return u'\t%s: %s\n' \
        % (form.instance.GetModelFieldByName(field_name).verbose_name,
           form.cleaned_data[field_name])


class MongoSearchForm(forms.Form):
    search = forms.CharField(max_length=255, label=_(u'Search skill'), required=False)
