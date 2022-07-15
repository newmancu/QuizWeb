from django.db import models
from django.contrib.auth.models import User


class AbsChoice(models.Model):

  choice = models.CharField(
    'Choice',
    max_length=256
  )

  class Meta:
    abstract = True


class Quiz(models.Model):

  name = models.CharField(
    'Quiz',
    max_length=256
  )

  def __str__(self):
    return f"{self.name}"


class Question(models.Model):

  question = models.CharField(
    'Question',
    max_length=256
  )

  choices = models.ManyToManyField(
    'QuestionChoice',
    verbose_name='Choices for the question'
  )

  multiple = models.BooleanField(
    'multiple choices',
  )

  def __str__(self):
    return f"{self.question}"


class QuestionChoice(AbsChoice):

  def __str__(self):
    return f"{self.choice}"


class QuizAnswer(models.Model):

  user = models.ForeignKey(
    'auth.User',
    on_delete=models.CASCADE,
    verbose_name='User'
  )

  quiz = models.ForeignKey(
    Quiz,
    on_delete=models.CASCADE,
    verbose_name='Quiz'
  )

  def __str__(self):
    return f"{self.quiz}-{self.user}"


class Answer(models.Model):
  
  quiz_answer = models.ForeignKey(
    QuizAnswer,
    on_delete=models.CASCADE,
    verbose_name="User answer to quiz's quiestion"
  )

  answer = models.ManyToManyField(
    QuestionChoice,
    verbose_name="Answer value"
  )

  def __str__(self):
    ans = '; '.join(map(lambda x: x.choice, self.answer.all()))
    return f"{self.quiz_answer}---{ans}"

