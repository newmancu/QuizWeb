from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class LoginForm(AuthenticationForm):

  class Meta:
    model = User
    fields = ['username', 'password']

class RegisterFrom(UserCreationForm):

  class Meta:
    model = User
    fields = ['username', 'password1', 'password2']