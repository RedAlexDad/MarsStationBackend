# import psycopg2
from django.db import models

# Модель для географических объектов
class GeograficObject(models.Model):
    feature = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    size = models.IntegerField()
    named_in_year = models.IntegerField()
    named_for = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'geografic_object'

# Модель для транспорта
class Transport(models.Model):
    name = models.CharField(max_length=255)
    type_transport = models.CharField(max_length=255)
    feature = models.CharField(max_length=255, null=True, blank=True)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'transport'

# Модель для точных местоположений
class Location(models.Model):
    geografic_object = models.ForeignKey(GeograficObject, on_delete=models.CASCADE)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    describe = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'location'

# Модель для истории передвижения
class HistoryMovement(models.Model):
    begin_location = models.ForeignKey(Location, related_name='history_begin_location', on_delete=models.CASCADE)
    end_location = models.ForeignKey(Location, related_name='history_end_location', on_delete=models.CASCADE)
    begin_data_movement = models.DateField()
    end_data_movement = models.DateField()
    distance_traveled = models.FloatField()
    purpose = models.CharField(max_length=255)
    results = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'history_movement'

