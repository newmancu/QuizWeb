from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http.request import HttpRequest
from django.urls import reverse
from back_api import forms
from back_api import models

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

def quiz_list(request: HttpRequest, page=1):
  offset = settings.PAGE_OFFSET
  _prev, _next = None, None
  quizzes = models.Quiz.objects.all()[offset*(page-1):offset*(page)].values()
  if page > 1:
    _prev = reverse('quiz_list') + f'{page-1}'
  if len(quizzes) >= offset:
    _next = reverse('quiz_list') + f'{page+1}'
  context = {
    'quizzes':quizzes,
    'next': _next,
    'prev': _prev
    }
  return render(request, 'quizweb/pages/quiz_list.html', context=context)

def quiz_answer(request: HttpRequest, id: int):
  try:
    quiz = models.Quiz.objects.get(id=id)
    questions = quiz.questions.all()
    print(questions)
    context = {
      'questions':questions,
      'quiz':quiz,
    }
    return render(request, 'quizweb/pages/quiz_answer.html', context=context)
  except Exception as ex:
    print(ex)
    raise Http404