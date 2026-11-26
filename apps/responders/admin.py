from django.contrib import admin

from .models import ResponderProfile


@admin.register(ResponderProfile)
class ResponderProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'specialization',
        'contact_number',
        'availability',
        'assigned_area',
    )
    list_filter = ('specialization', 'availability')
    search_fields = ('contact_number', 'assigned_area')
