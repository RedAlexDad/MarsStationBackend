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
# templates - папка для шаблонов (html-файлы)
from django.contrib import admin
from django.urls import path, include
from bmstu_lab import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'geografic_objects', views.GeographicalObjectViewSet)
router.register(r'transports', views.TransportViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Начальное меню
    path('', views.MainPage, name='main'),
    # Начальное меню карты
    path('select_geografic_object/', views.SelectGeograficObject, name='select_geografic_object'),
    # path('select_geografic_object/', include(router.urls)),
    # path('', include(router.urls), name='select_geografic_object'),
    # Список географических объектов
    path('geografic_objects/', views.GetGeograficObjects, name='geografic_objects'),
    # Сведения о географических объектов
    path('geografic_object/<int:id>/', views.GetGeograficObject, name='about_geografic_object'),
    # Фильтрация
    path('filter/', views.Filter, name='filter'),
    path('delete_geografic_object/', views.DeleteObjectByID, name='delete_geografic_object'),

    # path('geografic_objects/', views.DeleteObjectByID, name='delete_object'),

    # Включите URL-пути для вашего API через include
    path('api/', include(router.urls)),
]
