"""MQTT topic parse yardımcıları."""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..constants import MESSAGE_TYPES, TOPIC_PATTERN

_TOPIC_RE = re.compile(TOPIC_PATTERN)


@dataclass(frozen=True)
class ParsedTopic:
    """Parse edilmiş MQTT topic bileşenleri."""

    env: str
    version: str
    user_id: int
    field_id: int
    sensor_id: str
    message_type: str


def parse_topic(topic: str) -> ParsedTopic | None:
    """Topic string'ini bileşenlere ayırır; eşleşmezse None."""
    match = _TOPIC_RE.match(topic.strip())
    if not match:
        return None
    message_type = match.group('message_type')
    if message_type not in MESSAGE_TYPES:
        return None
    return ParsedTopic(
        env=match.group('env'),
        version=match.group('version'),
        user_id=int(match.group('user_id')),
        field_id=int(match.group('field_id')),
        sensor_id=match.group('sensor_id'),
        message_type=message_type,
    )
