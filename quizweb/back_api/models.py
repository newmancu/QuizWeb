from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.conf import settings
from django.utils.regex_helper import _lazy_re_compile



"""VALIDATORS"""
color_validator = RegexValidator(
    # _lazy_re_compile(r"^#([0-9a-f]{3}|[0-9a-f]{6})\Z"),
    _lazy_re_compile(r"^#([0-9a-f]{6})\Z"),
    message="Enter a valid color.",
    code="invalid",
)

def validate_color(value):
    return color_validator(value)


"""Fields"""
class ColorField(models.CharField):
  def __init__(self, *args, **kwargs):
    kwargs['max_length'] = 7
    super().__init__(*args,**kwargs)
    self.validators.append(validate_color)


"""CUSTOM USER CLASS"""

class QuizUser(AbstractUser):
  balance = models.BigIntegerField(
    'Balance',
    validators=[MinValueValidator(0)],
    default=0
  )
  
  bg_color = ColorField(
    'Background color',
    default="#ffffff"
  )

  border_color = ColorField(
    'Border color',
    default="#000000"
  )

  def bg_invert(self):
    a = map(lambda x: int(x, 16) ^ 0xff, [self.bg_color[i:i+2] for i in range(1,len(self.bg_color), 2)])
    res = '#' + ''.join(map(lambda x: f"{x:02x}", a))
    return res


class Quiz(models.Model):

  name = models.CharField(
    'Quiz',
    max_length=256
  )

  description = models.CharField(
    'Quiz description',
    max_length=256
  )

  questions = models.ManyToManyField(
    'Question',
    verbose_name="Quizs' questions"
  )

  payment = models.IntegerField(
    'Payment',
    validators=[MinValueValidator]
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


class QuestionChoice(models.Model):

  choice = models.CharField(
    'Choice',
    max_length=256
  )

  def __str__(self):
    return f"{self.choice}"


class QuizAnswerVariant(models.Model):

  user = models.ForeignKey(
    QuizUser,
    on_delete=models.CASCADE,
    verbose_name='User',
    related_name='qav_user',
    related_query_name='qav_user_q',
  )

  quiz = models.ForeignKey(
    Quiz,
    on_delete=models.CASCADE,
    verbose_name='Quiz',
    related_name='qav_quiz'
  )

  completed = models.BooleanField(
    'Completed quiz answer',
  )

  def __str__(self):
    return f"{self.pk}-{self.user}.{self.quiz}"


class QuizAnswer(models.Model):

  qa_variant = models.ForeignKey(
    'QuizAnswerVariant',
    on_delete=models.CASCADE,
    verbose_name="Quiz answer variant",
  )

  answer = models.ForeignKey(
    'Answer',
    on_delete=models.CASCADE,
    verbose_name='Answer'
  )

  class Meta:
    constraints = [
      models.UniqueConstraint(
        fields=['qa_variant','answer'], name='unique_user_quiz_answer'
      )
    ]

  def __str__(self):
    return f"<{self.qa_variant.pk}> {self.answer}"


class Answer(models.Model):

  answer = models.ManyToManyField(
    QuestionChoice,
    verbose_name="Answer value"
  )

  question = models.ForeignKey(
    Question,
    on_delete=models.CASCADE,
    verbose_name="Anwer fot Question"
  )

  def __str__(self):
    ans = '; '.join(map(lambda x: x.choice, self.answer.all()))
    return f"{self.question}---{ans}"




class QuizSelect(Quiz):
  class Meta:
    proxy = True