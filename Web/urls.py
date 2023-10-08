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
from django.contrib import admin
from django.urls import path, include

from bmstu_lab import views
from rest_framework import routers

router = routers.DefaultRouter()

# Если выводит ошибку о использованном другим сервером, то выполните следующее:
# Найти нужные PID, чтобы убить их
# lsof -i :8000
# Затем
# kill -9 <PID>

urlpatterns = [
    # Панель админа
    path('admin/', admin.site.urls),

    # Включим URL-пути для вашего API через include
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # УСЛУГА (ГЕОГРАФИЧЕСКИЙ ОБЪЕКТ)
    # Услуги - список, одна запись, добавление, изменение, удаление, добавление в заявку
    path(r'api/geographical_objects/', views.GET_GeographicalObjectsList),
    path(r'api/geographical_objects/<int:pk>/', views.GET_GeographicalObject),
    path(r'api/geographical_objects/create/', views.POST_GeograficObject),
    path(r'api/geographical_objects/<int:pk>/update/', views.PUT_GeograficObject),
    path(r'api/geographical_objects/<int:pk>/delete/', views.DELETE_GeograficObject),
    path(r'api/geographical_objects/<int:pk>/create_service_in_task/', views.POST_GeograficObject_IN_MarsStation),
    path(r'api/geographical_objects/filtration/', views.GET_GeographicalObjectFiltration),

    # ЗАЯВКА (МАРСИАНСКАЯ СТАНЦИЯ)
    # Заявки - список, одна запись, изменение, статусы создателя, статусы модератора, удаление
    path(r'api/mars_station/', views.GET_MarsStationList),
    path(r'api/mars_station/<int:pk>/', views.GET_MarsStation),
    # path(r'api/mars_station/create/', views.POST_MarsStation),
    path(r'api/mars_station/<int:pk>/update/', views.PUT_MarsStation),
    path(r'api/mars_station/<int:pk>/update_by_user/', views.PUT_MarsStation_BY_USER),
    path(r'api/mars_station/<int:pk>/update_by_admin/', views.PUT_MarsStation_BY_ADMIN),
    path(r'api/mars_station/<int:pk>/delete/', views.DELETE_MarsStation),
    path(r'api/mars_station/filtration/', views.GET_MarsStationFiltration),

    # М-М (МЕСТОПОЛОЖЕНИЕ)
    # м-м - удаление из заявки, изменение количества/значения в м-м
    path(r'api/location/<int:pk>/delete/', views.DELETE_Location),
    path(r'api/location/<int:pk>/update/', views.PUT_Location),

]
