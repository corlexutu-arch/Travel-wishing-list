from django.urls import path
from . import views


urlpatterns = [
    path('', views.homepage, name='home'),
    path('lista/', views.thelist, name='the_list'),
    path('delete/<int:pk>/', views.delete_entry, name='delete_entry'),
]