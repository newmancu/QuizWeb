from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.conf import settings
from django.utils.regex_helper import _lazy_re_compile



"""VALIDATORS"""
color_validator = RegexValidator(
    # _lazy_re_compile(r"^#([0-9a-f]{3}|[0-9a-f]{6})\Z"),
    _lazy_re_compile(r"^#([0-9a-f]{6})\Z"),
    message="Введите корректное значение цвета в 16-разрдном формате RGB (#ffffff).",
    code="invalid",
)

def validate_color(value):
  return color_validator(value)


"""FIELDS"""
class ColorField(models.CharField):
  """
  Поле для хранения информации о цвете в 16-разрдном 
  формате RGB
  """
  def __init__(self, *args, **kwargs):
    kwargs['max_length'] = 7
    super().__init__(*args,**kwargs)
    self.validators.append(validate_color)



"""CUSTOM USER CLASS"""
class QuizUser(AbstractUser):
  """
  Расширенный стандартный пользовательский класс,
  который хранит информацию о балансе пользователя,
  цвете фона и цвете рамки
  """
  balance = models.BigIntegerField(
    'Баланс пользователя',
    validators=[MinValueValidator(0)],
    default=0
  )
  
  bg_color = ColorField(
    'Цвет заднего фона профиля пользователя',
    default="#ffffff"
  )

  border_color = ColorField(
    'Цвет рамки профиля пользователя',
    default="#000000"
  )

  def bg_invert(self):
    """
    Функция инвертации bg_color
    """
    a = map(lambda x: int(x, 16) ^ 0xff, [self.bg_color[i:i+2] for i in range(1,len(self.bg_color), 2)])
    res = '#' + ''.join(map(lambda x: f"{x:02x}", a))
    return res


class Quiz(models.Model):
  """
  Опросник. Модель в БД.
  """
  name = models.CharField(
    'Название опроса',
    max_length=256
  )

  description = models.CharField(
    'Описание опроса',
    max_length=256
  )

  questions = models.ManyToManyField(
    'Question',
    verbose_name="Вопросы в опросе"
  )

  payment = models.IntegerField(
    'Вознаграждение за прохождение опроса',
    validators=[MinValueValidator]
  )

  def __str__(self):
    return f"{self.name}"


class Question(models.Model):
  """
  Вопрос. Модель в БД.
  """

  question = models.CharField(
    'Вопрос',
    max_length=256
  )

  choices = models.ManyToManyField(
    'QuestionChoice',
    verbose_name='Варианты ответа на вопрос'
  )

  multiple = models.BooleanField(
    'Возможность множественного ответа на вопрос',
  )

  def __str__(self):
    return f"{self.question}"


class QuestionChoice(models.Model):
  """
  Варианты ответов. Модель в БД.
  """

  choice = models.CharField(
    'Варианты ответа на вопрос',
    max_length=256
  )

  def __str__(self):
    return f"{self.choice}"


class QuizAnswerVariant(models.Model):
  """
  Вариант ответа пользователя на опросник. Модель в БД.
  """

  user = models.ForeignKey(
    QuizUser,
    on_delete=models.CASCADE,
    verbose_name='Пользователь, заполняющий опросник',
    related_name='qav_user',
    related_query_name='qav_user_q',
  )

  quiz = models.ForeignKey(
    Quiz,
    on_delete=models.CASCADE,
    verbose_name='Шаблон Опросника',
    related_name='qav_quiz'
  )

  completed = models.BooleanField(
    'Заполнен ли опросник',
  )

  def __str__(self):
    return f"{self.pk}-{self.user}.{self.quiz}"


class QuizAnswer(models.Model):
  """
  Ответ на конкретный вопрос из QuizAnswerVariant. Модель в БД.
  """

  qa_variant = models.ForeignKey(
    'QuizAnswerVariant',
    on_delete=models.CASCADE,
    verbose_name="Опросник, на который отвечает пользовател",
  )

  answer = models.ForeignKey(
    'Answer',
    on_delete=models.CASCADE,
    verbose_name='Ответ пользователя на опросник'
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
  """
  Ответ на вопрос. Модель в БД.
  """

  answer = models.ManyToManyField(
    QuestionChoice,
    verbose_name="Вариант ответа на вопрос"
  )

  question = models.ForeignKey(
    Question,
    on_delete=models.CASCADE,
    verbose_name="Вопрос из опросника"
  )

  def __str__(self):
    ans = '; '.join(map(lambda x: x.choice, self.answer.all()))
    return f"{self.question}---{ans}"
