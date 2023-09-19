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

# Сотрудник космического агенства
class EmployeeSpaceAgency(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    full_name = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    name_space_agency = models.CharField(max_length=255)
    address_space_agency = models.CharField(max_length=255)
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'employee_space_agency'

# Сотрудник организации
class EmployeeOrganization(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    full_name = models.CharField(max_length=255)
    post = models.CharField(max_length=255)
    name_organization = models.CharField(max_length=255)
    address_organization = models.CharField(max_length=255)
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_user',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'employee_organization'

# Статус
class Status(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    status_task = models.CharField(max_length=255)
    status_mission = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'status'

# Географический объект (услуга)
class GeographicalObject(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    type = models.CharField(max_length=255)
    feature = models.CharField(max_length=255)
    size = models.IntegerField(null=True, blank=True)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'geographical_object'

# Транспорт (доп. информация для услуги)
class Transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'transport'

# Марсианская станция (заявка)
class MarsStation(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    landing_date = models.IntegerField()
    location = models.CharField(max_length=255)

    # Добавляем внешний ключ к другой модели
    id_employee_organization = models.ForeignKey(
        EmployeeOrganization,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_employee_organization',  # Имя поля в базе данных
    )

    id_employee_space_agency = models.ForeignKey(
        EmployeeSpaceAgency,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_employee_space_agency',  # Имя поля в базе данных
    )

    id_status = models.ForeignKey(
        Status,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_status',  # Имя поля в базе данных
    )

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
    id_transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
    )
    id_mars_station = models.ForeignKey(
        MarsStation,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_mars_station',  # Имя поля в базе данных
        related_name='id_mars_station_location',  # Пользовательское имя
    )
    purpose = models.CharField(max_length=255)
    results = models.CharField(max_length=255)
    class Meta:
        managed = False
        db_table = 'location'