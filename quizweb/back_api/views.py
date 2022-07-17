from django.conf import settings
from django.http import Http404
from django.db import IntegrityError 
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.http.request import HttpRequest
from django.urls import reverse
from django.db.models import Count
from back_api import forms
from back_api import models

# Create your views here.

def is_anonimus(func, to='index'):
  """
  Декоратор для проверки анонимных пользователей
  """
  def mfunc(request:HttpRequest, *args, **kwargs):
    if request.user.is_anonymous:
      return func(request, *args, **kwargs)
    return redirect(to)
  return mfunc

def paggination(page, view_name, query, offset):
  _prev, _next = None, None
  if page > 1:
    _prev = reverse(view_name) + f'{page-1}'
  if len(query) >= offset:
    _next = reverse(view_name) + f'{page+1}'
  return _prev, _next


def index(request):
  """
  Главная страница сайта
  """
  return render(request, 'quizweb/index.html')

@is_anonimus
def login_view(request: HttpRequest):
  """
  Страница для авторизации пользователя
  """
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
  """
  Страница для регистрации пользователя
  """
  if request.method == 'POST':
    form = forms.RegisterFrom(data=request.POST)

    if form.is_valid():
      user = form.save()
      return redirect('login')
  form = forms.RegisterFrom()
  return render(request, 'quizweb/auth/register.html', {'form':form})

def logout_view(request: HttpRequest):
  """
  Страница для разлогинивания пользователя
  """
  logout(request)
  return redirect('index')

def quiz_list(request: HttpRequest, page=1):
  """
  Страница со списком всех доступных опросников
  """
  if page <= 0:
    return redirect('quiz_list')
  offset = settings.PAGE_OFFSET
  quizzes = models.Quiz.objects.all()[offset*(page-1):offset*(page)].values()
  _prev, _next = paggination(page, 'quiz_list', quizzes, offset)  
  context = {
    'quizzes':quizzes,
    'next': _next,
    'prev': _prev
    }
  return render(request, 'quizweb/pages/quiz_list.html', context=context)

def quiz_answer(request: HttpRequest, id: int):
  """
  Страница для прохождения опросника с заданным id
  """
  context = {
    'form': None,
    'is_anonymus':True,
    'full_fields':False,
  }
  if request.user.is_anonymous:
    return render(request, 'quizweb/pages/quiz_answer.html', context=context)

  try:
    qa_variant = models.QuizAnswerVariant.objects.filter(
      user=request.user, quiz_id=id, completed=False).select_related('quiz').first()
    if qa_variant is None:
      qa_variant = models.QuizAnswerVariant.objects.create(
        user=request.user, quiz_id=id, completed=False
      )
    quiz = qa_variant.quiz

    if request.method == 'POST':
      form = forms.QuizAnswerForm(qa_variant=qa_variant, data=request.POST)
      if form.is_valid():
        form.save()
        request.user.balance += quiz.payment
        request.user.save()
        return redirect('leaderboard')
      context['full_fields'] = True
    else:
      form = forms.QuizAnswerForm(qa_variant=qa_variant)
    context['form'] = form
    context['is_anonymus'] = False

    return render(request, 'quizweb/pages/quiz_answer.html', context=context)
  except IntegrityError:
    raise Http404("Нет опросника с таки id")

def leaderboard(request, page=1):
  """
  Страница со списком всех пользователей и
  количеством пройденных ими тестов
  """
  if page <= 0:
    return redirect('leaderboard')
  offset = settings.PAGE_OFFSET
  users = models.QuizUser.objects.annotate(
        num_quizzes=Count('qav_user_q__quiz')
      ).order_by('-num_quizzes', '-username')[offset*(page-1):offset*(page)]
  _prev, _next = paggination(page, 'leaderboard', users, offset)  

  context = {
    'users':users,
    'next': _next,
    'prev': _prev
    }
  return render(request, 'quizweb/pages/leaderboard.html', context=context)

def profile(request):
  """
  Страница профиля пользователя
  """
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
      user.save()
      return redirect('leaderboard')
  form = forms.QuizUserChangeColorForm(instance=user)
  context = {
    'user': user,
    'form': form,
    'cost': cost
  }
  return render(request, 'quizweb/pages/profile.html', context=context)