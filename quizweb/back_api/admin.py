from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.urls import path
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

@admin.register(models.QuizAnswerVariant)
class QuizAnswerVariantAdmin(admin.ModelAdmin):
  pass

@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
  pass

@admin.register(models.Answer)
class UserAnswers(admin.ModelAdmin):
  pass  
