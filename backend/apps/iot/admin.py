"""IoT admin configuration."""

from django.contrib import admin

from .models import Sensor, SensorReading


class SensorReadingInline(admin.TabularInline):
    """Sensör okumaları inline listesi."""

    model = SensorReading
    extra = 0
    readonly_fields = ('message_id', 'value', 'unit', 'measured_at', 'received_at')
    can_delete = False
    max_num = 10
    ordering = ('-measured_at',)


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    """Sensör admin paneli."""

    list_display = (
        'name',
        'field',
        'sensor_type',
        'status',
        'connection_protocol',
        'last_reading_at',
    )
    list_filter = ('status', 'sensor_type', 'connection_protocol')
    search_fields = ('name', 'mac_address', 'field__name')
    readonly_fields = ('id', 'mqtt_client_id', 'created_at', 'updated_at')
    inlines = [SensorReadingInline]
    actions = ['issue_tokens']

    @admin.action(description='Yeni provisioning token üret')
    def issue_tokens(self, request, queryset) -> None:
        """Seçili sensörlere provisioning token atar."""
        for sensor in queryset:
            sensor.issue_provisioning_token()


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    """Sensör okuması admin paneli."""

    list_display = ('sensor', 'value', 'unit', 'measured_at', 'received_at')
    list_filter = ('unit',)
    search_fields = ('sensor__name', 'message_id')
    readonly_fields = ('message_id', 'raw_payload', 'received_at')
    date_hierarchy = 'measured_at'
