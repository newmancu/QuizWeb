from django.core.management.base import BaseCommand
from back_api.models import QuizUser


class Command(BaseCommand):
  """
  Команда, добавляющая стандартного суперпользователя
  """
  help = 'startup command'

  def handle(self, *args, **options):
    
    if not QuizUser.objects.filter(username='admin').exists():
      QuizUser.objects.create_superuser(
        username='admin',
        password='admin',
        email='admin@asdfa.as'
      )