from django.contrib import admin
from .models import Viewer, Users, Employee, GeographicalObject, Status, Location, PositionOfLocations, Transport

admin.site.register(GeographicalObject)
admin.site.register(Transport)
admin.site.register(PositionOfLocations)
admin.site.register(Location)
admin.site.register(Status)
admin.site.register(Employee)
admin.site.register(Viewer)
admin.site.register(Users)