from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('player/<int:pk>/', views.player_selected, name='player_selected'),
    path('player_list/', views.player_list, name='player_list'),
    path('match/<str:pk>/', views.match_selected, name='match_selected'),
    path('tournament_list/', views.tournament_list, name='tournament_list'),
    path('tournament/<str:pk>/', views.tournament_selected, name='tournament_selected'),
    path('compare/<int:p1>/<int:p2>/', views.compare_stats, name='compare_stats'),
    path('login/', views.login_to, name='login'),
    path('logout/', views.logout_my, name='logout'),
    path('register/', views.signup, name='register'),
    path('register/done', views.signup_complete, name='register_complete'),
    path('profile/<int:pk>/', views.remove, name='remove'),
    path('profile/', views.profile_my, name='profile'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='tenis/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="tenis/password_reset_confirm.html"), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='tenis/password_reset_complete.html'), name='password_reset_complete'),
    path('password_reset', views.password_reset_request, name='password_reset'),

    path('acc_active_email/(?P<uidb64>[0-9A-Za-z_\\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/', views.activate
         , name='activate'),
]