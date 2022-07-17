from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http.request import HttpRequest
from django.urls import reverse
from django.db.models import Count
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
    context = {
      'questions':questions,
      'quiz':quiz,
    }
    return render(request, 'quizweb/pages/quiz_answer.html', context=context)
  except Exception as ex:
    raise Http404

def leaderboard(request, page=1):
  offset = settings.PAGE_OFFSET
  _prev, _next = None, None

  # quizzes = models.QuizAnswer.objects.all().annotate(
  #   num_quizzes=Count('quiz', distinct=True))
  users = models.QuizUser.objects.all().order_by(
    '-username')[offset*(page-1):offset*(page)].annotate(
      num_quizzes=Count(('qa_user__quiz'), distinct=True))
  if page > 1:
    _prev = reverse('leaderboard') + f'{page-1}'
  if len(users) >= offset:
    _next = reverse('leaderboard') + f'{page+1}'
  context = {
    'users':users,
    'next': _next,
    'prev': _prev
    }
  return render(request, 'quizweb/pages/leaderboard.html', context=context)

def profile(request):
  cost = settings.COLOR_CHANGE_COST
  user = request.user
  if request.method == 'POST':
    form = forms.QuizUserChangeColorForm(data=request.POST)
    if form.is_valid() \
      and (form.cleaned_data['bg_color'] != user.bg_color \
        or form.cleaned_data['border_color'] != user.border_color) \
      and user.balance >= cost:
      user.bg_color = form.cleaned_data['bg_color']
      user.border_color = form.cleaned_data['border_color']
      user.balance -= cost
      print(user, type(user))
      user.save()
      return redirect('leaderboard')
  form = forms.QuizUserChangeColorForm(instance=user)
  context = {
    'user': user,
    'form': form,
    'cost': cost
  }
  return render(request, 'quizweb/pages/profile.html', context=context)