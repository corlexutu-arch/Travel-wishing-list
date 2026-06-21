from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name='home'),
    path('lista/', views.thelist, name='the_list'),
]