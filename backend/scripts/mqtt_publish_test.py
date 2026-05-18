#!/usr/bin/env python
"""
Geliştirme: örnek telemetri mesajı yayınlar.

Kullanım (broker ayaktayken):
  cd backend
  python scripts/mqtt_publish_test.py --sensor-id <uuid> --field-id 1 --user-id 1
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

import django

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import paho.mqtt.client as mqtt

from apps.iot.constants import telemetry_topic


def main() -> None:
    parser = argparse.ArgumentParser(description='Örnek MQTT telemetri yayını')
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=1883)
    parser.add_argument('--user-id', type=int, required=True)
    parser.add_argument('--field-id', type=int, required=True)
    parser.add_argument('--sensor-id', required=True)
    parser.add_argument('--value', type=float, default=42.5)
    args = parser.parse_args()

    topic = telemetry_topic(args.user_id, args.field_id, args.sensor_id)
    payload = {
        'schema_version': '1.0',
        'message_id': str(uuid.uuid4()),
        'sensor_id': args.sensor_id,
        'tarla_id': str(args.field_id),
        'tip': 'toprak_nemi',
        'deger': args.value,
        'birim': '%',
        'olcum_zamani': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
    }

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        protocol=mqtt.MQTTv311,
    )
    client.connect(args.host, args.port, 60)
    client.publish(topic, json.dumps(payload), qos=1)
    client.disconnect()
    print(f'Published to {topic}')


if __name__ == '__main__':
    main()
