# import psycopg2
from django.db import models

# Пользователь
class Users(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'users'

# Начальник (ПРИНМАЮЩИЙ ЗАКАЗЧИКА) и Ученые (ЗАКАЗЧИК)
class Employee(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    full_name = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    name_organization = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
    )
    class Meta:
        managed = False
        db_table = 'employee'

# Географический объект (услуга)
class GeographicalObject(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    feature = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    size = models.IntegerField(null=True, blank=True)
    describe = models.CharField(max_length=1000, null=True, blank=True)
    url_photo = models.CharField(max_length=1000, null=True, blank=True)
    status = models.BooleanField()
    class Meta:
        managed = False
        db_table = 'geographical_object'

# Транспорт (доп. информация для услуги)
class Transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    describe = models.CharField(max_length=1000, null=True, blank=True)
    url_photo = models.CharField(max_length=1000, null=True, blank=True)
    class Meta:
        managed = False
        db_table = 'transport'

# Марсианская станция (заявка)
class MarsStation(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    type_status = models.CharField(max_length=255)
    date_create = models.DateField()
    date_form = models.DateField()
    date_close = models.DateField()
    # Добавляем внешний ключ к другой модели
    id_employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_employee',  # Имя поля в базе данных
        related_name='id_employee_by_table_employee'
    )
    id_moderator = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_moderator',  # Имя поля в базе данных
        related_name='id_moderator_by_table_employee'
    )
    id_transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
    )
    status_task = models.IntegerField()
    status_mission = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'mars_station'


# Местоположение (вспомогательная таблица)
class Location(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    # Добавляем внешний ключ к другой модели
    id_geographical_object = models.ForeignKey(
        GeographicalObject,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_geographical_object',  # Имя поля в базе данных
    )

    id_mars_station = models.ForeignKey(
        MarsStation,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_mars_station',  # Имя поля в базе данных
        related_name='id_mars_station_location',  # Пользовательское имя
    )
    sequence_number = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'location'