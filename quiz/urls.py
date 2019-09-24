from django.urls import path, include
from django.conf import settings
from django.contrib.auth import views as auth_views

from . import views
from . import api

app_name = 'quiz'
urlpatterns = [
    path('', views.index, name='index'),
    path('question', views.question_home, name='question_home'),
    path('question/<int:question_id>/reservation',
         views.reservation,
         name='reservation'),
    path('question/<int:question_id>/reservation/steer',
         views.reservation_steer,
         name='reservation_steer'),
    path('question/<int:question_id>/reservation/lost/<str:approved_player>',
         views.reservation_lost,
         name='reservation_lost'),
    path('question/<int:question_id>/reservation/<int:reservation_id>/answer/',
         views.provide_answer,
         name='provide_answer'),
    path('question/<int:question_id>/answer/<int:answer_id>/steer',
         views.answer_steer,
         name='answer_steer'),
    # Signup, login, logout
    path('signup', views.signup, name='signup'),
    path('login',
         auth_views.LoginView.as_view(
             template_name='quiz/account/login.html'
         ),
         {'next_page': settings.LOGIN_REDIRECT_URL},
         name='login'),
    path('logout',
         auth_views.LogoutView.as_view(),
         {'next_page': settings.LOGOUT_REDIRECT_URL},
         name='logout'),
    # APIs
    path('api/check_question_reservation/<int:question_id>',
         api.api_check_question_reservation,
         name='api_check_question_reservation'),
    path('api/check_answer_status/<int:answer_id>',
         api.api_check_answer_status,
         name='api_check_answer_status'),
]