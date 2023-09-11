import psycopg2
from django.db import models

class GeograficObject(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'web_mars'

#
# class Database():
#     # Подключение к БД
#     def connect(self):
#         try:
#             # Подключение к базе данных
#             self.connection = psycopg2.connect(
#                 host=5432,
#                 user='postgresql',
#                 password='postgresql',
#                 database='web_mars'
#             )
#
#             print("[INFO] Успешное подключение к базе данных")
#
#         except Exception as ex:
#             print("[INFO] Ошибка при работе с PostgreSQL:", ex)
#
#     # Удаление БД
#     def drop_table(self):
#         try:
#             with self.connection.cursor() as cursor:
#                 cursor.execute("""
#                 DROP TABLE Geografic_object CASCADE;
#                 DROP TABLE Transport CASCADE;
#                 DROP TABLE Location CASCADE;
#                 """)
#
#             # Подтверждение изменений
#             self.connection.commit()
#             print("[INFO] Успешно удалены таблицы в базе данных")
#
#         except Exception as ex:
#             print("[INFO] Ошибка при работе с PostgreSQL:", ex)