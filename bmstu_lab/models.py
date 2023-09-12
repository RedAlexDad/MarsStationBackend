import psycopg2
from django.db import models

class geografic_object(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.TextField()
    type_locality = models.TextField()
    describe = models.TextField()

    class Meta:
        managed = False
        db_table = 'geografic_object'


