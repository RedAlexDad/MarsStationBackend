# import psycopg2
from django.db import models

# Модель для географических объектов
class geografic_object(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    feature = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    size = models.IntegerField()
    named_in_year = models.IntegerField()
    named_for = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'geografic_object'

# Модель для транспорта
class transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    name = models.CharField(max_length=255)
    type_transport = models.CharField(max_length=255)
    feature = models.CharField(max_length=255, null=True, blank=True)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'transport'

# Модель для точных местоположений
class location(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    # id_geografic_object = models.ForeignKey(geografic_object, related_name='id_geografic_object', on_delete=models.PROTECT)
    # id_transport = models.ForeignKey(transport, related_name='id_transport', on_delete=models.PROTECT)
    location = models.CharField(max_length=255)
    describe = models.CharField(max_length=255, blank=True, null=True)

    # Добавляем внешний ключ к другой модели
    id_geografic_object = models.ForeignKey(
        geografic_object,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_geografic_object',  # Имя поля в базе данных
    )

    # Добавляем внешний ключ к другой модели (замените "YourModel" и "your_field" на реальные значения)
    id_transport = models.ForeignKey(
        transport,  # Замените "YourModel" на модель, к которой вы хотите создать внешний ключ
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
    )

    class Meta:
        managed = False
        db_table = 'location'

# Модель для истории передвижения
class history_movement(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False)
    begin_data_movement = models.DateField()
    end_data_movement = models.DateField()
    distance_traveled = models.FloatField()
    purpose = models.CharField(max_length=255)
    results = models.CharField(max_length=255)

    id_begin_location = models.ForeignKey(
        location,
        on_delete=models.CASCADE,
        db_column='id_begin_location',
        related_name='begin_location_movements',  # Установите свое собственное имя
    )

    id_end_location = models.ForeignKey(
        location,
        on_delete=models.CASCADE,
        db_column='id_end_location',
        related_name='end_location_movements',  # Установите свое собственное имя
    )

    class Meta:
        managed = False
        db_table = 'history_movement'

