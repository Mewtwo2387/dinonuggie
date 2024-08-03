from django.urls import path
from . import views

urlpatterns = [
    path('', views.index , name='index'),
    path('login/', views.google_login, name='login'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
    path('logout/', views.logout, name='logout'),
    path('claim/', views.claim, name='claim'),
]