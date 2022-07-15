from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class QuizBlock(models.Model):
  
  name = models.CharField(
    "Название теста",
    max_length=256,
  )

  def __str__(self):
    return f"{self.name}"


class QuizQuestionBase(models.Model):

  quiestion = models.CharField(
    'Вопрос',
    max_length=256,
  )

  def __str__(self):
    return f"{self.quiestion}"

  class Meta:
    abstract = True


class QuizQuestionText(QuizQuestionBase):

  quiz = models.ForeignKey(
    'QuizBlock',
    on_delete=models.CASCADE,
  )

  answer = models.TextField(
    'Пользовательский ответ',
    max_length=1028
  )


class QuizQuestionSelect(QuizQuestionBase):

  quiz = models.ForeignKey(
    'QuizBlock',
    on_delete=models.CASCADE,
  )

  answers = models.ManyToManyField(
    'QuizTest',
    verbose_name='Варианты ответов'
  )

  is_multiple = models.BooleanField(
    'Множественный ответ'
  )


class QuizTest(models.Model):

  answer = models.CharField(
    'Ответ',
    max_length=256,
  )

  def __str__(self):
    return f"{self.answer}"


class QuizAnswers(models.Model):

  user = models.ForeignKey(
    'auth.User',
    on_delete=models.CASCADE,
    verbose_name='Ответчик'
  )

  quiz = models.ForeignKey(
    'QuizBlock',
    on_delete=models.CASCADE,
    verbose_name='Вопросник'
  )