from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http.request import HttpRequest
from back_api import forms

# Create your views here.

def is_anonimus(func, to='index'):
  def mfunc(request:HttpRequest, *args, **kwargs):
    if request.user.is_anonymous:
      return func(request, *args, **kwargs)
    return redirect(to)
  return mfunc


def index(request):
  return render(request, 'quizweb/index.html')

@is_anonimus
def login_view(request: HttpRequest):
  if request.method == 'POST':
    form = forms.LoginForm(data=request.POST)
    a = form.is_valid()
    if a:
      user = form.get_user()
      login(request, user)
      return redirect('index')
  form = forms.LoginForm()
  return render(request, 'quizweb/auth/login.html', {'form':form})

@is_anonimus
def register_view(request: HttpRequest):
  if request.method == 'POST':
    form = forms.RegisterFrom(data=request.POST)

    if form.is_valid():
      user = form.save()
      return redirect('login')
  form = forms.RegisterFrom()
  return render(request, 'quizweb/auth/register.html', {'form':form})

def logout_view(request: HttpRequest):
  logout(request)
  return redirect('index')