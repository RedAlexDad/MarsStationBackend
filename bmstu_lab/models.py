from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin, BaseUserManager


# Пользователь
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        username = self.normalize_email(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_moderator', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


# class Users(AbstractUser):
class Users(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    username = models.CharField(max_length=255, unique=True, verbose_name="Никнейм")
    password = models.CharField(max_length=255, verbose_name="Пароль")
    is_moderator = models.BooleanField(default=False, verbose_name="Является ли пользователь модератором?")

    # Necessary fields for django
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    # is_staff = models.BooleanField(default=False, verbose_name="Является ли пользователь менеджером?")
    # is_superuser = models.BooleanField(default=False, verbose_name="Является ли пользователь админом?")

    def str(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.username}"

    class Meta:
        db_table = 'users'
        verbose_name = "Пользователь"


# Начальник (ПРИНМАЮЩИЙ ЗАКАЗЧИКА) и Ученые (ЗАКАЗЧИК)
class Employee(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    post = models.CharField(max_length=255, verbose_name="Должность")
    name_organization = models.CharField(max_length=255, verbose_name="Название организации")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="Адрес")
    # Добавляем внешний ключ к другой модели
    id_user = models.ForeignKey(
        Users,
        on_delete=models.CASCADE,
        db_column='id_user',
        verbose_name="ID пользователя",
    )

    class Meta:
        managed = False
        db_table = 'employee'
        verbose_name = "Сотрудник"


# Географический объект (услуга)
class GeographicalObject(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    feature = models.CharField(max_length=255, verbose_name="Название")
    type = models.CharField(max_length=255, verbose_name="Тип")
    size = models.IntegerField(null=True, blank=True, verbose_name="Площадь")
    describe = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Описание")
    photo = models.BinaryField(null=True, blank=True, verbose_name="Изображение")
    status = models.BooleanField(verbose_name="Статус объекта: доступен / недоступен")

    class Meta:
        managed = False
        db_table = 'geographical_object'
        verbose_name = "Географический объект"


# Транспорт (доп. информация для услуги)
class Transport(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name="Название")
    type = models.CharField(max_length=255, verbose_name="Тип")
    describe = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Описание")
    photo = models.BinaryField(max_length=1000, null=True, blank=True, verbose_name="Изображение")

    class Meta:
        managed = False
        db_table = 'transport'
        verbose_name = "Транспорт"


# Марсианская станция (заявка)
class MarsStation(models.Model):
    id = models.BigAutoField(primary_key=True, serialize=False, verbose_name="ID")
    type_status = models.CharField(max_length=255, verbose_name="Тип заявки")
    date_create = models.DateField(verbose_name="Дата создания")
    date_form = models.DateField(null=True, blank=True, verbose_name="Дата формирования")
    date_close = models.DateField(null=True, blank=True, verbose_name="Дата закрытия")
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
        verbose_name="ID модератора",
        null=True, blank=True
    )
    id_transport = models.ForeignKey(
        Transport,
        on_delete=models.CASCADE,  # Это действие, которое будет выполнено при удалении связанной записи
        db_column='id_transport',  # Имя поля в базе данных
        verbose_name="ID транспорта",
        null=True, blank=True
    )
    STATUS_TASK = (
        (1, 'Черновик'),
        (2, 'В работе'),
        (3, 'Завершена'),
        (4, 'Отменена'),
        (5, 'Удалена'),
    )

    STATUS_MISSION = (
        (0, 'Не удалось обратиться к асинхронному сервису'),
        (1, 'В работе'),
        (2, 'Успех'),
        (3, 'Потеря'),
    )

    status_task = models.IntegerField(choices=STATUS_TASK, default=1, verbose_name="Статус заявки")
    status_mission = models.IntegerField(choices=STATUS_MISSION, default=2, verbose_name="Статус миссии")

    # Метод, который будет преобразовать код в слова
    def get_status_task_display_word(self):
        status_task_dict = dict(self.STATUS_TASK)
        return status_task_dict.get(self.status_task, 'Unknown')

    def get_status_mission_display_word(self):
        status_mission_dict = dict(self.STATUS_MISSION)
        return status_mission_dict.get(self.status_mission, 'Unknown')

    # Метод, который будет преобразовывать строку в число
    def convert_status_task_string_to_number(self, status_string):
        status_task_dict = {v: k for k, v in dict(self.STATUS_TASK).items()}
        return status_task_dict.get(status_string, None)

    def convert_status_mission_string_to_number(self, status_string):
        status_mission_dict = {v: k for k, v in dict(self.STATUS_MISSION).items()}
        return status_mission_dict.get(status_string, None)

    class Meta:
        managed = False
        db_table = 'mars_station'
        verbose_name = "Марсианская станция"


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
    sequence_number = models.IntegerField(verbose_name="Порядковый номер")

    class Meta:
        managed = False
        db_table = 'location'
        verbose_name = "Местоположение"
