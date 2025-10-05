"""
Communication Gateway Module - Week 4 Implementation  
Authenticated messaging with privacy-first routing and personal log integration

Features:
- Multi-protocol message routing (Telegram, Email, Webhook)
- GPG-encrypted message transport using Week 1 GPG module
- Authenticated messaging using Week 3 auth system
- Personal log server integration for message audit trails
- Real-time notification system with user preferences
- Privacy-first message handling with zero retention
"""

from .service import CommunicationService
from .schemas import (
    MessageRequest,
    MessageResponse, 
    NotificationRequest,
    NotificationResponse,
    MessageRoute,
    CommunicationChannel,
    MessagePriority,
    DeliveryStatus
)

__all__ = [
    "CommunicationService",
    "MessageRequest",
    "MessageResponse", 
    "NotificationRequest",
    "NotificationResponse",
    "MessageRoute",
    "CommunicationChannel", 
    "MessagePriority",
    "DeliveryStatus"
]