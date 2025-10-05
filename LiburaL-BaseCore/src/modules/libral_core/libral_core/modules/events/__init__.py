"""
Event Management Module - Week 5 Implementation
Real-time event processing with personal log server integration

Features:
- Real-time event bus with Redis pub/sub
- Event categorization and filtering system
- Personal log server event logging with topics/hashtags
- System health monitoring and metrics collection
- Plugin event integration and lifecycle management
- Webhook-based external event processing
- User-controlled event preferences and privacy
"""

from .service import EventService
from .schemas import (
    Event,
    EventCreate,
    EventResponse,
    EventCategory,
    EventPriority,
    EventFilter,
    SystemMetric,
    HealthCheck,
    RealTimeEventStream
)

__all__ = [
    "EventService",
    "Event",
    "EventCreate", 
    "EventResponse",
    "EventCategory",
    "EventPriority",
    "EventFilter",
    "SystemMetric",
    "HealthCheck",
    "RealTimeEventStream"
]