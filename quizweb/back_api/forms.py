from django import forms
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.forms import (
  UserCreationForm, AuthenticationForm, UserChangeForm,
  ReadOnlyPasswordHashField, UsernameField
)
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from back_api import models




"""AUTH FORMS"""
class QuizUserChangeForm(UserChangeForm):

  class Meta:
    model = models.QuizUser
    fields = "__all__"
    field_classes = {"username": UsernameField}


class QuizUserAddForm(UserCreationForm):
  class Meta:
    model = models.QuizUser
    fields = "__all__"
    field_classes = {"username": UsernameField}

class LoginForm(AuthenticationForm):

  class Meta:
    model = models.QuizUser
    fields = ['username', 'password']

class RegisterFrom(UserCreationForm):

  class Meta:
    model = models.QuizUser
    fields = ['username', 'password1', 'password2']


"""ADMIN FORMS"""


class RadioBoxForm(forms.ModelForm):

  mchoices = forms.Field()

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    variants = self.instance.question.choices.all()
    choices = [(it.pk, it.choice) for it in variants]
    if self.instance.question.multiple:
      self.fields['mchoices'] = forms.MultipleChoiceField(
        choices=choices,
        widget=forms.CheckboxSelectMultiple
      )
    else:
      self.fields['mchoices'] = forms.ChoiceField(
        choices=choices,
        widget=forms.RadioSelect
      )

  def save(self, commit: bool = ...):
    self.instance.answer.clear()
    self.instance.answer.set(self.cleaned_data['mchoices'])
    self.instance.save(commit)

  class Meta:
    model = models.Answer
    fields = ('question', 'mchoices')
    readonly_fields = ('question',)


class QuizUserChangeColorForm(forms.ModelForm):

  class Meta:
    model = models.QuizUser
    fields = ('bg_color', 'border_color')