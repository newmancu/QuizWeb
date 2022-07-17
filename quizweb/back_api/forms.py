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


class QuestionRadioBoxForm(forms.ModelForm):

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


class QuizQuestionForm(forms.Form):

  def __init__(self, *args, **kwargs):
    self.question = kwargs.pop('initial',{}).pop('question', None)
    super().__init__(*args, **kwargs)
    if self.question is not None:
      self.fields['mchoices'] = self._add_choice_field()

  def clean(self):
    return super().clean()

  def _add_choice_field(self):
    choices = [(it.pk, it.choice) for it in self.question.choices.all()]
    options = {
      'choices':choices,
      'label':self.question.question
    }
    if self.question.multiple:
      return forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        **options
      )
    return forms.ChoiceField(
        widget=forms.RadioSelect,
        **options
      )
    
SuperFormSet = forms.formset_factory(QuizQuestionForm, min_num=0, max_num=30)

from django.db import connection, reset_queries
class QuizAnswerForm(forms.Form):

  def __init__(self, qa_variant, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # reset_queries()
    # start = len(connection.queries)
    self.qa_variant = qa_variant
    self.quiz = models.Quiz.objects.filter(
      id=qa_variant.quiz.id).prefetch_related('questions__choices')[0]

    # print(len(connection.queries) - start)

    self.questions = SuperFormSet(initial=[
      {'question':it} for it in self.quiz.questions.all()
    ], **kwargs)
    # print(len(connection.queries) - start)


  def is_valid(self) -> bool:
    return forms.all_valid(self.questions) and super().is_valid()

  def clean(self):
    self.cleaned_data['questions'] = self.questions.cleaned_data
    return self.cleaned_data

  def save(self, commit: bool = ...):

    reset_queries()
    start = len(connection.queries)
    answers = []
    ans_ans = []
    quiz_answers = []
    for q in self.questions:
      if len(q.changed_data) > 0:
        answers.append(models.Answer(
          question_id=q.question.id
        ))
    answers = models.Answer.objects.bulk_create(answers)
    for q, ans in zip(self.questions, answers):
      cds = q.cleaned_data.get('mchoices', [])
      if isinstance(cds, str):
        ans_ans.append(models.Answer.answer.through(
            answer_id=ans.id, questionchoice_id=cds
          ))
      elif isinstance(cds, list):
        for cd in cds:
          ans_ans.append(models.Answer.answer.through(
            answer_id=ans.id, questionchoice_id=cd
          ))
      quiz_answers.append(models.QuizAnswer(
        answer=ans,
        qa_variant=self.qa_variant
      ))

    # print(f"ans_ans = {ans_ans}")
    # print(f"quiz_answers = {quiz_answers}")
    models.Answer.answer.through.objects.bulk_create(ans_ans)
    models.QuizAnswer.objects.bulk_create(quiz_answers)
    self.qa_variant.completed = True
    self.qa_variant.save()
    print(len(connection.queries) - start)

    # print(q.cleaned_data, q.question)