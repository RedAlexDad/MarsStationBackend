# import psycopg2
from django.db import models

# Модель для пользователей
class Users(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    login = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    admin = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users'

# Модель для сотрудника
class Employee(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    full_name = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'employee'

# Модель для зрителя
class Viewer(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    full_name = models.CharField(max_length=255)
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'viewer'

# Модель для статуса
class Status(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    status_task = models.CharField(max_length=255)
    status_mission = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'status'

# Модель для географических объектов
class GeographicalObject(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    type = models.CharField(max_length=255)
    feature = models.CharField(max_length=255)
    size = models.IntegerField()
    named_in = models.IntegerField()
    named_for = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'geographical_object'

# Модель для транспорта
class Transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'transport'

# Модель для точных местоположений
class Location(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    landing_date = models.DateField()
    location = models.CharField(max_length=255)

    # Добавляем внешний ключ к другой модели
    id_viewer = models.ForeignKey(
        Viewer,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_viewer',  # Имя поля в базе данных
    )

    id_employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_employee',  # Имя поля в базе данных
    )

    id_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_status',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'location'


# Модель для позиций местоположений
class PositionOfLocations(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    # Добавляем внешний ключ к другой модели
    id_geographical_object = models.ForeignKey(
        GeographicalObject,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_geographical_object',  # Имя поля в базе данных
    )
    id_location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_location',  # Имя поля в базе данных
    )
    id_transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
    )
    data_begin_movement = models.DateField()
    data_end_movement = models.DateField()
    purpose = models.CharField(max_length=255)
    results = models.CharField(max_length=255)
    distance_traveled = models.FloatField()
    class Meta:
        managed = False
        db_table = 'position_of_locations'