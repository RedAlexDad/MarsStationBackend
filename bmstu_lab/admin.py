from django.contrib import admin
from .models import MarsStation, Employee, Location, GeographicalObject, Status, Users, Transport

admin.site.register(Users)
admin.site.register(Employee)
admin.site.register(Transport)
admin.site.register(MarsStation)
admin.site.register(Status)
admin.site.register(Location)
admin.site.register(GeographicalObject)