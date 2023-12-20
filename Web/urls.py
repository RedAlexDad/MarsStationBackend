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
from bmstu_lab.views import mars_station, geographical_object, location, other_func, account
from rest_framework import routers, permissions
# SWAGGER
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

router = routers.DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Запуск сервер Redis
# redis-server
# Можно остановить или перезагрузить командой
# redis-server stop/restart

# Панель администратора
urlpatterns = [
    # Панель админа
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    # Включим URL-пути для вашего API через include
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Авторизация, аутентификация, регистрация, выход с учетной записи
urlpatterns += [
    # Список аккаунтов
    path(r'api/users/', account.UsersGET.as_view()),
    # Обновление аккаунта
    path(r'api/users/<int:pk>/update/', account.UsersPUT.as_view()),
    # Удаление аккаунта
    path(r'api/users/<int:pk>/delete/', account.UsersDELETE.as_view()),

    # Регистрация
    path('api/register/', account.RegisterView.as_view()),
    # Аутентификация
    path('api/authentication/', account.LoginView.as_view()),
    # Получение токена
    path('api/get_token/', account.GetToken.as_view()),
    # Выход с учетной записи
    path('api/logout/', account.LogoutView.as_view()),

    # Список сотрудников
    path(r'api/employee/', account.EmployeeClass.as_view()),
]

# Другие функции
urlpatterns += [
    # УСЛУГА (ГЕОГРАФИЧЕСКИЙ ОБЪЕКТ)
    # Услуги - список, одна запись, добавление, изменение, удаление, добавление в заявку
    path(r'api/geographical_object/', geographical_object.GET_GeographicalObjects),
    path(r'api/geographical_object/<int:pk>/', geographical_object.GET_GeographicalObject),
    path(r'api/geographical_object/create/', geographical_object.POST_GeograficObject),
    path('api/geographical_object/<int:pk>/image/', geographical_object.GET_GeograficObject_IMAGE),
    path('api/geographical_object/<int:pk>/update_image/', geographical_object.PUT_GeograficObject_IMAGE),
    path(r'api/geographical_object/<int:pk>/update/', geographical_object.PUT_GeograficObject),
    path(r'api/geographical_object/<int:pk>/delete/', geographical_object.DELETE_GeograficObject),
    path(r'api/geographical_object/<int:pk_service>/create_service_in_task/', geographical_object.POST_GeograficObject_IN_MarsStation),

    # ЗАЯВКА (МАРСИАНСКАЯ СТАНЦИЯ)
    # Заявки - список, одна запись, изменение, статусы создателя, статусы модератора, удаление
    path(r'api/mars_station/', mars_station.GET_MarsStationList),
    path(r'api/mars_station/<int:pk>/', mars_station.GET_MarsStation),
    path(r'api/mars_station/<int:pk>/update/', mars_station.PUT_MarsStation),
    path(r'api/mars_station/<int:pk>/update_by_user/', mars_station.PUT_MarsStation_BY_USER),
    path(r'api/mars_station/<int:pk>/update_by_admin/', mars_station.PUT_MarsStation_BY_ADMIN),
    path(r'api/mars_station/<int:pk>/delete/', mars_station.DELETE_MarsStation),

    # М-М (МЕСТОПОЛОЖЕНИЕ)
    # м-м - удаление из заявки, изменение количества/значения в м-м
    path(r'api/location/<int:pk_location>/mars_station/<int:pk_mars_station>/delete/', location.DELETE_Location),
    path(r'api/location/<int:pk_location>/mars_station/<int:pk_mars_station>/update/', location.PUT_Location),

    # Транспорт
    path(r'api/transport/', other_func.GET_Transport),

    # Асинхронный веб-сервис
    path(r'api/async_result/', other_func.PUT_async_result),
]
