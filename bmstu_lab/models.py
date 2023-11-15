from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin


# Пользователь
class Users(AbstractUser):
    username = models.CharField(max_length=255, unique=True, verbose_name="Никнейм")
    password = models.CharField(max_length=255, verbose_name="Пароль")

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    def str(self):
        return self.username


# Начальник (ПРИНМАЮЩИЙ ЗАКАЗЧИКА) и Ученые (ЗАКАЗЧИК)
class Employee(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    post = models.CharField(max_length=255, verbose_name="Должность")
    name_organization = models.CharField(max_length=255, verbose_name="Название организации")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
        verbose_name="ID пользователя"
    )

    class Meta:
        managed = False
        db_table = 'employee'


# Географический объект (услуга)
class GeographicalObject(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    feature = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(max_length=255, verbose_name="Тип")
    size = models.IntegerField(null=True, blank=True, verbose_name="Площадь")
    describe = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Описание")
    photo = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Ссылка на изображение Minio")
    status = models.BooleanField(verbose_name="Статус объекта: доступен / недоступен")

    class Meta:
        managed = False
        db_table = 'geographical_object'


# Транспорт (доп. информация для услуги)
class Transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    name = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(max_length=255, verbose_name="Тип")
    describe = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Описание")
    photo = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Ссылка на изображение Minio")

    class Meta:
        managed = False
        db_table = 'transport'


# Марсианская станция (заявка)
class MarsStation(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    type_status = models.CharField(max_length=255, verbose_name="Тип заявки")
    date_create = models.DateField(verbose_name="Дата создания")
    date_form = models.DateField(verbose_name="Дата формирования")
    date_close = models.DateField(verbose_name="Дата закрытия")
    # Добавляем внешний ключ к другой модели
    id_employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_employee',  # Имя поля в базе данных
        related_name='id_employee_by_table_employee',
        verbose_name="ID сотрудника"
    )
    id_moderator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_moderator',  # Имя поля в базе данных
        related_name='id_moderator_by_table_employee',
        verbose_name="ID модератора"
    )
    id_transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
        verbose_name="ID транспорта"
    )
    status_task = models.IntegerField(verbose_name="Статус заявки")
    status_mission = models.IntegerField(verbose_name="Статус миссии")

    class Meta:
        managed = False
        db_table = 'mars_station'


# Местоположение (вспомогательная таблица)
class Location(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    # Добавляем внешний ключ к другой модели
    id_geographical_object = models.ForeignKey(
        GeographicalObject,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_geographical_object',  # Имя поля в базе данных
        verbose_name="ID географического объекта"
    )

    id_mars_station = models.ForeignKey(
        MarsStation,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_mars_station',  # Имя поля в базе данных
        related_name='id_mars_station_location',  # Пользовательское имя
        verbose_name="ID марсианской станции"
    )

    class Meta:
        managed = False
        db_table = 'location'
