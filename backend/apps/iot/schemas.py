"""MQTT JSON payload doğrulama."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from django.utils.dateparse import parse_datetime

from jsonschema import Draft7Validator

TELEMETRY_SCHEMA = {
    'type': 'object',
    'required': ['schema_version', 'message_id', 'sensor_id', 'tip', 'deger', 'birim', 'olcum_zamani'],
    'properties': {
        'schema_version': {'type': 'string'},
        'message_id': {'type': 'string', 'format': 'uuid'},
        'sensor_id': {'type': 'string', 'format': 'uuid'},
        'tarla_id': {'type': ['string', 'integer']},
        'tip': {'type': 'string'},
        'deger': {'type': 'number'},
        'birim': {'type': 'string', 'minLength': 1},
        'olcum_zamani': {'type': 'string'},
        'kalite': {'type': 'object'},
        'meta': {'type': 'object'},
    },
    'additionalProperties': True,
}

STATUS_SCHEMA = {
    'type': 'object',
    'required': ['schema_version', 'sensor_id', 'state'],
    'properties': {
        'schema_version': {'type': 'string'},
        'sensor_id': {'type': 'string', 'format': 'uuid'},
        'state': {'type': 'string', 'enum': ['online', 'offline']},
        'battery_v': {'type': 'number'},
        'rssi_dbm': {'type': 'integer'},
        'uptime_s': {'type': 'integer'},
        'errors': {'type': 'array'},
        'reason': {'type': 'string'},
    },
    'additionalProperties': True,
}

BIRTH_SCHEMA = {
    'type': 'object',
    'required': ['schema_version', 'mac_adresi', 'tip', 'provisioning_token'],
    'properties': {
        'schema_version': {'type': 'string'},
        'mac_adresi': {'type': 'string', 'minLength': 11},
        'tip': {'type': 'string'},
        'firmware': {'type': 'string'},
        'provisioning_token': {'type': 'string', 'minLength': 8},
    },
    'additionalProperties': True,
}

_telemetry_validator = Draft7Validator(TELEMETRY_SCHEMA)
_status_validator = Draft7Validator(STATUS_SCHEMA)
_birth_validator = Draft7Validator(BIRTH_SCHEMA)


class PayloadValidationError(ValueError):
    """Geçersiz MQTT JSON payload."""


def _validate(validator: Draft7Validator, data: dict[str, Any]) -> dict[str, Any]:
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    if errors:
        messages = '; '.join(e.message for e in errors)
        raise PayloadValidationError(messages)
    return data


def validate_telemetry(data: dict[str, Any]) -> dict[str, Any]:
    """Telemetri payload doğrulaması."""
    return _validate(_telemetry_validator, data)


def validate_status(data: dict[str, Any]) -> dict[str, Any]:
    """Durum payload doğrulaması."""
    return _validate(_status_validator, data)


def validate_birth(data: dict[str, Any]) -> dict[str, Any]:
    """Birth / provisioning payload doğrulaması."""
    return _validate(_birth_validator, data)


def parse_message_id(value: str) -> uuid.UUID:
    """message_id alanını UUID'ye çevirir."""
    try:
        return uuid.UUID(str(value))
    except (ValueError, AttributeError) as exc:
        raise PayloadValidationError('Geçersiz message_id') from exc


def parse_measured_at(value: str) -> datetime:
    """ISO 8601 ölçüm zamanını parse eder."""
    parsed = parse_datetime(value)
    if parsed is None:
        raise PayloadValidationError('Geçersiz olcum_zamani')
    return parsed
