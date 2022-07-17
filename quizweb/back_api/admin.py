from django.utils.http import urlencode
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from back_api import models
from back_api import forms


"""USER ADMIN"""
@admin.register(models.QuizUser)
class QuizUserAdmin(UserAdmin):
  fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": (
          "first_name", "last_name", "email",
          "balance", "bg_color", "border_color"
          )}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
  form = forms.QuizUserChangeForm
  add_form = forms.QuizUserAddForm


"""MODEL ADMINS"""

@admin.register(models.QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
  pass


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
  pass

@admin.register(models.QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
  pass


"""OTHER ADMINS"""
@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
  pass


@admin.register(models.Answer)
class UserAnswers(admin.ModelAdmin):
  pass  


@admin.register(models.QuizSelect)
class QuizSelectAdmin(admin.ModelAdmin):
  list_display = ('create_name',)

  def create_name(self, obj):
    url = (
      reverse("admin:back_api_answer_add")
      + "?"
      + urlencode({
        'quiz':f"{obj.id}",
        })
    )
    name = obj.name
    return format_html('<a href="{}">{}</a>', url, name)
  
  create_name.short_description = "Name"