"""MQTT mesaj işleme — telemetri, durum ve provisioning."""

from __future__ import annotations

import json
import logging
import uuid
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.iot.models import Sensor, SensorReading
from apps.iot.schemas import (
    PayloadValidationError,
    parse_measured_at,
    parse_message_id,
    validate_birth,
    validate_status,
    validate_telemetry,
)
from apps.iot.services.mqtt_topics import ParsedTopic, parse_topic

logger = logging.getLogger(__name__)


class IngestService:
    """Broker'dan gelen MQTT mesajlarını veritabanına yazar."""

    @classmethod
    def handle_message(cls, topic: str, payload: bytes) -> bool:
        """
        Topic ve payload'ı işler.

        Returns:
            True ise mesaj işlendi; False ise topic tanınmadı veya atlandı.
        """
        parsed = parse_topic(topic)
        if parsed is None:
            logger.debug('Tanınmayan topic: %s', topic)
            return False

        try:
            data = json.loads(payload.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            logger.warning('Geçersiz JSON topic=%s: %s', topic, exc)
            return True

        handlers = {
            'telemetry': cls._handle_telemetry,
            'status': cls._handle_status,
            'birth': cls._handle_birth,
        }
        handler = handlers.get(parsed.message_type)
        if handler is None:
            logger.debug('İşlenmeyen mesaj tipi: %s', parsed.message_type)
            return True

        handler(parsed, data)
        return True

    @classmethod
    def _get_sensor(cls, parsed: ParsedTopic, payload_sensor_id: str | None = None) -> Sensor | None:
        sensor_id = payload_sensor_id or parsed.sensor_id
        try:
            sensor_uuid = uuid.UUID(sensor_id)
        except ValueError:
            logger.warning('Geçersiz sensor_id: %s', sensor_id)
            return None

        try:
            return Sensor.objects.select_related('field', 'field__user').get(
                id=sensor_uuid,
                field_id=parsed.field_id,
                field__user_id=parsed.user_id,
            )
        except Sensor.DoesNotExist:
            logger.warning(
                'Sensör bulunamadı sensor=%s field=%s user=%s',
                sensor_id,
                parsed.field_id,
                parsed.user_id,
            )
            return None

    @classmethod
    def _handle_telemetry(cls, parsed: ParsedTopic, data: dict[str, Any]) -> None:
        try:
            validate_telemetry(data)
        except PayloadValidationError as exc:
            logger.warning('Telemetri şema hatası: %s', exc)
            return

        sensor = cls._get_sensor(parsed, str(data['sensor_id']))
        if sensor is None:
            return

        if data.get('tip') and data['tip'] != sensor.sensor_type:
            logger.warning(
                'Tip uyuşmazlığı sensor=%s beklenen=%s gelen=%s',
                sensor.id,
                sensor.sensor_type,
                data['tip'],
            )

        message_id = parse_message_id(data['message_id'])
        measured_at = parse_measured_at(data['olcum_zamani'])

        try:
            with transaction.atomic():
                _, created = SensorReading.objects.get_or_create(
                    message_id=message_id,
                    defaults={
                        'sensor': sensor,
                        'field_id': sensor.field_id,
                        'value': Decimal(str(data['deger'])),
                        'unit': data['birim'],
                        'raw_payload': data,
                        'measured_at': measured_at,
                    },
                )
                if not created:
                    logger.debug('Duplicate message_id=%s atlandı', message_id)
                    return

                sensor.last_reading_at = measured_at
                if sensor.status != 'aktif':
                    sensor.status = 'aktif'
                sensor.save(update_fields=['last_reading_at', 'status', 'updated_at'])
        except IntegrityError:
            logger.debug('Duplicate message_id (race)=%s', message_id)

    @classmethod
    def _handle_status(cls, parsed: ParsedTopic, data: dict[str, Any]) -> None:
        try:
            validate_status(data)
        except PayloadValidationError as exc:
            logger.warning('Status şema hatası: %s', exc)
            return

        sensor = cls._get_sensor(parsed, str(data['sensor_id']))
        if sensor is None:
            return

        state = data['state']
        if state == 'online':
            sensor.status = 'aktif'
        else:
            sensor.status = 'baglanti_yok'

        if data.get('firmware') or data.get('meta', {}).get('firmware'):
            sensor.firmware_version = data.get('firmware') or data['meta']['firmware']

        sensor.last_reading_at = timezone.now()
        sensor.save(update_fields=['status', 'firmware_version', 'last_reading_at', 'updated_at'])

    @classmethod
    def _handle_birth(cls, parsed: ParsedTopic, data: dict[str, Any]) -> None:
        try:
            validate_birth(data)
        except PayloadValidationError as exc:
            logger.warning('Birth şema hatası: %s', exc)
            return

        token = data['provisioning_token']
        try:
            sensor = Sensor.objects.select_related('field').get(
                id=uuid.UUID(parsed.sensor_id),
                field_id=parsed.field_id,
                provisioning_token=token,
            )
        except Sensor.DoesNotExist:
            logger.warning('Provisioning başarısız sensor=%s', parsed.sensor_id)
            return

        sensor.mac_address = data['mac_adresi']
        sensor.sensor_type = data['tip']
        if data.get('firmware'):
            sensor.firmware_version = data['firmware']
        sensor.status = 'aktif'
        sensor.provisioning_token = None
        sensor.save(
            update_fields=[
                'mac_address',
                'sensor_type',
                'firmware_version',
                'status',
                'provisioning_token',
                'updated_at',
            ],
        )
        logger.info('Sensör provisioned: %s', sensor.id)
