from django.contrib import admin
from back_api import models

# Register your models here.


class QuizAdmin(admin.ModelAdmin):
  pass


class QuestionAdmin(admin.ModelAdmin):
  pass


class QuestionChoiceAdmin(admin.ModelAdmin):
  pass


class QuizAnswerAdmin(admin.ModelAdmin):
  pass


class AnswerAdmin(admin.ModelAdmin):
  pass


admin.site.register(models.Quiz, QuizAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.QuestionChoice, QuestionChoiceAdmin)
admin.site.register(models.QuizAnswer, QuizAnswerAdmin)
admin.site.register(models.Answer, AnswerAdmin)
