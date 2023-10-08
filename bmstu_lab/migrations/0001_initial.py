# Generated by Django 4.1 on 2023-09-25 11:59

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("full_name", models.CharField(max_length=255)),
                ("post", models.CharField(max_length=255)),
                ("name_organization", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
            ],
            options={
                "db_table": "employee",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="GeographicalObject",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("feature", models.CharField(max_length=255)),
                ("type", models.CharField(max_length=255)),
                ("size", models.IntegerField(blank=True, null=True)),
                ("describe", models.CharField(blank=True, max_length=1000, null=True)),
                ("url_photo", models.CharField(blank=True, max_length=1000, null=True)),
                ("status", models.BooleanField()),
            ],
            options={
                "db_table": "geographical_object",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("sequence_number", models.IntegerField()),
            ],
            options={
                "db_table": "location",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="MarsStation",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("type_status", models.CharField(max_length=255)),
                ("data_create", models.DateField()),
                ("data_from", models.DateField()),
                ("data_close", models.DateField()),
                ("status_task", models.IntegerField()),
                ("status_mission", models.IntegerField()),
            ],
            options={
                "db_table": "mars_station",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Transport",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=255)),
                ("type", models.CharField(max_length=255)),
                ("describe", models.CharField(blank=True, max_length=1000, null=True)),
                ("url_photo", models.CharField(blank=True, max_length=1000, null=True)),
            ],
            options={
                "db_table": "transport",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Users",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("login", models.CharField(max_length=255)),
                ("password", models.CharField(max_length=255)),
                ("admin", models.BooleanField()),
            ],
            options={
                "db_table": "users",
                "managed": False,
            },
        ),
        migrations.RunSQL(
            """
                                        -- СВЯЗЫВАНИЕ БД ВНЕШНИМИ КЛЮЧАМИ --
                ALTER TABLE location
                ADD CONSTRAINT FR_location_of_geographical_object
                    FOREIGN KEY (id_geographical_object) REFERENCES geographical_object (id);

                ALTER TABLE location
                ADD CONSTRAINT FR_location_of_mars_station
                    FOREIGN KEY (id_mars_station) REFERENCES mars_station (id);

                ALTER TABLE mars_station
                ADD CONSTRAINT FR_mars_station_of_transport
                    FOREIGN KEY (id_transport) REFERENCES transport (id);

                ALTER TABLE mars_station
                ADD CONSTRAINT FR_mars_station_of_scientist
                    FOREIGN KEY (id_employee) REFERENCES employee (id);

                ALTER TABLE employee
                ADD CONSTRAINT FR_employee_organization_of_users
                    FOREIGN KEY (id_user) REFERENCES users (id);
             """),
    ]
