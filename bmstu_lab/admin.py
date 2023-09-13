from django.contrib import admin
from .models import geografic_object, transport, history_movement, location

admin.site.register(geografic_object)
admin.site.register(transport)
admin.site.register(history_movement)
admin.site.register(location)