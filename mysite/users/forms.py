# -*- encoding: utf-8 -*-

import string

from django import forms
from django.utils.translation import ugettext as _

from mysite.users import models
from mysite.users import tasks


class UserProfileAdminForm(forms.ModelForm):
    class Meta:
        model = models.UserProfile
        fields = ['username', 'last_name', 'first_name', 'surname', 'myemail',
                  'mob_tel', 'work_tel', 'department', 'position', 'is_superuser']

    skills = forms.CharField(max_length=255, label=_(u'MadSkillz'), widget=forms.Textarea(), required=False, help_text=_(u'Each skill from new line'))


    def __init__(self, *args, **kwargs):
        super(UserProfileAdminForm, self).__init__(*args, **kwargs)
        self.initial[u'skills'] = u'\n'.join(self.instance.skills)


    def save(self, *args, **kwargs):

        self.send_notifications()

        self.instance.skills = self.parse_skills()

        return super(UserProfileAdminForm, self).save(*args, **kwargs)


    def parse_skills(self):
        return [
            parsed_skills_with_empty_lines for parsed_skills_with_empty_lines in
                parse_string_splitting_by_symbol_and_removing_whitespaces(self.cleaned_data['skills'], u'\n')
            if parsed_skills_with_empty_lines!=u''
        ]

    def send_notifications(self):
        changed_user_reference = self.get_changed_user_reference()
        const_message_part = self.make_message(changed_user_reference)

        tasks.make_sending.delay(
            const_message_part=const_message_part,
            changed_user_department=self.instance.department,
            title=u'Данные сотрудника %s на Mysite были изменены' % changed_user_reference)


    #noinspection PyCallByClass
    def get_changed_user_reference(self):
        if self.is_bound:
            return models.form_reference(
                self.instance.last_name,
                self.instance.first_name,
                self.instance.surname,
                self.instance.username)
        else:
            model = self.Meta.model
            return models.form_reference(
                model.get_model_field_by_name('last_name'),
                model.get_model_field_by_name('first_name'),
                model.get_model_field_by_name('surname'),
                model.get_model_field_by_name('username'))


    def make_message(self, changed_user):
        changed_data = self.changed_data
        message = _(u'the following data of User %s has been changed:\n') % changed_user
        for field_name in changed_data:
            if not (field_name == u'skills'):
                message += get_model_field_change(self, field_name)
        if u'skills' in changed_data:
            message += get_skills_changes(self.instance.skills, self.parse_skills())
        return message


def parse_string_splitting_by_symbol_and_removing_whitespaces(str,symbol):
    return [parsed_strs_with_whitespaces.strip(string.whitespace) for parsed_strs_with_whitespaces in str.split(symbol)]

def get_skills_changes(skills_before, skills_after):
    new_skills = get_skills_difference(skills_after, skills_before)
    deleted_skills = get_skills_difference(skills_before, skills_after)
    message = get_deleted_skills_message(deleted_skills)
    message += get_final_skills_message_with_new(new_skills, skills_after)
    return message


def get_deleted_skills_message(deleted_skills):
    message = u''
    if len(deleted_skills) > 0:
        message = _(u'The following skills were deleted:\n')
        for skill in deleted_skills:
            message += u'\t' + skill + u'\n'
    return message


def get_final_skills_message_with_new(new_skills, skills_after):
    message = u''
    if len(new_skills) > 0:
        message = _(u'Final list of skills is:\n')
        for skill in skills_after:
            message += u'\t' + skill
            if skill in new_skills:
                message += _(u' (added!)')
            message += u'\n'
    return message


def get_skills_difference (skills1, skills2):
    return set(skills1) - set(skills2)


def get_model_field_change(form, field_name):
    return u'\t%s: %s\n' \
        % (form.instance.get_model_field_by_name(field_name).verbose_name,
           form.cleaned_data[field_name])


class MongoSearchForm(forms.Form):
    search = forms.CharField(max_length=255, label=_(u'Search skill'))
