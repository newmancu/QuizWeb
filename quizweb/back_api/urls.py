from django.urls import path, include
from back_api import views

urlpatterns = [
    path('', views.index, name='index'),
    path('auth/', include([
        path('login', views.login_view, name='login'),
        path('register', views.register_view, name='register'),
        path('logout', views.logout_view, name='logout'),
    ])),
    path('quizzes/', include([
        path('', views.quiz_list, name='quiz_list'),
        path('<int:page>/', views.quiz_list, name='quiz_list_page'),
    ])),
    path('quiz/<int:id>', views.quiz_answer, name='quiz_answer'),
    path('leaderboard/', include([
        path('', views.leaderboard, name='leaderboard'),
        path('<int:page>', views.leaderboard, name='leaderboard_page'),
    ])),
    path('profile', views.profile, name='profile')
]
