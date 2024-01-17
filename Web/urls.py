"""Web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# urls.py - соответствие урлам обработчиков(views)
from django.contrib import admin
from django.urls import path
from bmstu_lab import views

urlpatterns = [
    # Панель администратора
    path('admin/', admin.site.urls),
    # Начальное меню
    path('', views.MainPage, name='main'),
    # Список географических объектов
    path('geographical_objects/', views.GetGeographicalObjects, name='geographical_objects'),
    # Сведения о географических объектов
    path('geographical_object/<int:id>/', views.GetGeographicalObject, name='about_geographical_object'),
    # Фильтрация
    path('geographical_object/', views.Filter, name='filter'),
    # Удаление объекта
    path('delete_geographical_object/', views.DeleteObjectByID, name='delete_geographical_object'),
]
