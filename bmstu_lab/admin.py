from django.contrib import admin
from .models import MarsStation, EmployeeSpaceAgency, EmployeeOrganization, Location, GeographicalObject, Status, Users, Transport

admin.site.register(MarsStation)
admin.site.register(EmployeeSpaceAgency)
admin.site.register(EmployeeOrganization)
admin.site.register(Location)
admin.site.register(GeographicalObject)
admin.site.register(Status)
admin.site.register(Users)
admin.site.register(Transport)