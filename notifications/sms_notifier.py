"""
Twilio SMS Notification System for LICS
Production-ready SMS notifications with real Twilio integration
"""

import os
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """SMS notification types for different events"""
    SHIPMENT_CREATED = "shipment_created"
    DISPATCH_READY = "dispatch_ready"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    EXCEPTION = "exception"
    WEATHER_ALERT = "weather_alert"
    ROUTE_OPTIMIZATION = "route_optimization"
    EMERGENCY = "emergency"

class Priority(Enum):
    """Notification priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SMSNotification:
    """Data structure for SMS notifications"""
    recipient_phone: str
    message: str
    notification_type: NotificationType
    priority: Priority
    shipment_id: Optional[str] = None
    customer_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    scheduled_time: Optional[datetime] = None

class TwilioSMSService:
    """Production Twilio SMS service with comprehensive notification management"""
    
    def __init__(self):
        """Initialize Twilio client with production credentials"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        # Prioritize TWILIO_FROM_PHONE over TWILIO_PHONE_NUMBER for consistency
        self.from_phone = os.getenv('TWILIO_FROM_PHONE') or os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.account_sid, self.auth_token, self.from_phone]):
            raise ValueError("Missing required Twilio credentials in environment")
        
        self.client = Client(self.account_sid, self.auth_token)
        self.notification_history: List[Dict] = []
        self.rate_limit_cache: Dict[str, List[datetime]] = {}
        
        logger.info(f"Twilio SMS service initialized successfully with FROM phone: {self.from_phone}")
    
    def _check_rate_limit(self, phone: str, max_per_hour: int = 10) -> bool:
        """Check if phone number has exceeded rate limit"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        if phone not in self.rate_limit_cache:
            self.rate_limit_cache[phone] = []
        
        # Clean old timestamps
        self.rate_limit_cache[phone] = [
            timestamp for timestamp in self.rate_limit_cache[phone]
            if timestamp > hour_ago
        ]
        
        return len(self.rate_limit_cache[phone]) < max_per_hour
    
    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Twilio (E.164 format)"""
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))
        
        # Add country code if missing (assuming US/India)
        if len(digits) == 10:
            digits = '1' + digits  # US default
        elif len(digits) == 10 and phone.startswith('9'):
            digits = '91' + digits  # India default
        
        return '+' + digits
    
    async def send_sms(self, notification: SMSNotification) -> Dict[str, Any]:
        """Send SMS notification with comprehensive error handling"""
        try:
            # Format phone number
            formatted_phone = self._format_phone_number(notification.recipient_phone)
            
            # Check rate limit
            if not self._check_rate_limit(formatted_phone):
                logger.warning(f"Rate limit exceeded for {formatted_phone}")
                return {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'phone': formatted_phone
                }
            
            # Send SMS using Twilio
            message = self.client.messages.create(
                body=notification.message,
                from_=self.from_phone,
                to=formatted_phone
            )
            
            # Update rate limit cache
            if formatted_phone not in self.rate_limit_cache:
                self.rate_limit_cache[formatted_phone] = []
            self.rate_limit_cache[formatted_phone].append(datetime.now())
            
            # Log successful send
            result = {
                'success': True,
                'message_sid': message.sid,
                'phone': formatted_phone,
                'status': message.status,
                'notification_type': notification.notification_type.value,
                'priority': notification.priority.value,
                'timestamp': datetime.now().isoformat(),
                'shipment_id': notification.shipment_id,
                'customer_id': notification.customer_id
            }
            
            self.notification_history.append(result)
            logger.info(f"SMS sent successfully: {message.sid}")
            
            return result
            
        except TwilioException as e:
            logger.error(f"Twilio error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': notification.recipient_phone,
                'notification_type': notification.notification_type.value
            }
        except Exception as e:
            logger.error(f"Unexpected error sending SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'phone': notification.recipient_phone
            }
    
    async def send_bulk_sms(self, notifications: List[SMSNotification]) -> List[Dict[str, Any]]:
        """Send multiple SMS notifications efficiently"""
        results = []
        for notification in notifications:
            result = await self.send_sms(notification)
            results.append(result)
            # Small delay to avoid overwhelming Twilio
            await asyncio.sleep(0.1)
        
        return results

class LICSNotificationManager:
    """LICS-specific notification manager with template system"""
    
    def __init__(self):
        """Initialize notification manager with SMS service"""
        self.sms_service = TwilioSMSService()
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load SMS message templates for different notification types"""
        return {
            NotificationType.SHIPMENT_CREATED.value: 
                "Your shipment #{shipment_id} has been created and will be processed soon. Track at: {tracking_url}",
            
            NotificationType.DISPATCH_READY.value:
                "Your shipment #{shipment_id} is ready for dispatch. Expected pickup: {pickup_time}",
            
            NotificationType.IN_TRANSIT.value:
                "Your shipment #{shipment_id} is now in transit. Current location: {current_location}. ETA: {eta}",
            
            NotificationType.DELIVERED.value:
                "Great news! Your shipment #{shipment_id} has been delivered successfully. Thank you for choosing our service!",
            
            NotificationType.DELAYED.value:
                "Update: Your shipment #{shipment_id} is delayed. New ETA: {new_eta}. Reason: {delay_reason}",
            
            NotificationType.EXCEPTION.value:
                "Alert: Issue with shipment #{shipment_id}. Our team is working to resolve. Contact: {support_phone}",
            
            NotificationType.WEATHER_ALERT.value:
                "Weather Alert: {weather_condition} may affect shipments in {location}. Updates will follow.",
            
            NotificationType.ROUTE_OPTIMIZATION.value:
                "Route optimized for shipment #{shipment_id}. New ETA: {optimized_eta}. This may improve delivery time!",
            
            NotificationType.EMERGENCY.value:
                "URGENT: {emergency_message} For immediate assistance call: {emergency_contact}"
        }
    
    def _format_message(self, template: str, **kwargs) -> str:
        """Format message template with provided data"""
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning(f"Missing template parameter: {e}")
            return template
    
    async def notify_shipment_created(self, phone: str, shipment_id: str, tracking_url: str = "") -> Dict[str, Any]:
        """Send shipment created notification"""
        message = self._format_message(
            self.templates[NotificationType.SHIPMENT_CREATED.value],
            shipment_id=shipment_id,
            tracking_url=tracking_url or f"https://lics.track/{shipment_id}"
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.SHIPMENT_CREATED,
            priority=Priority.MEDIUM,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_dispatch_ready(self, phone: str, shipment_id: str, pickup_time: str) -> Dict[str, Any]:
        """Send dispatch ready notification"""
        message = self._format_message(
            self.templates[NotificationType.DISPATCH_READY.value],
            shipment_id=shipment_id,
            pickup_time=pickup_time
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.DISPATCH_READY,
            priority=Priority.HIGH,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_in_transit(self, phone: str, shipment_id: str, current_location: str, eta: str) -> Dict[str, Any]:
        """Send in transit notification"""
        message = self._format_message(
            self.templates[NotificationType.IN_TRANSIT.value],
            shipment_id=shipment_id,
            current_location=current_location,
            eta=eta
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.IN_TRANSIT,
            priority=Priority.MEDIUM,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_delivered(self, phone: str, shipment_id: str) -> Dict[str, Any]:
        """Send delivery confirmation notification"""
        message = self._format_message(
            self.templates[NotificationType.DELIVERED.value],
            shipment_id=shipment_id
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.DELIVERED,
            priority=Priority.HIGH,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_delayed(self, phone: str, shipment_id: str, new_eta: str, delay_reason: str) -> Dict[str, Any]:
        """Send delay notification"""
        message = self._format_message(
            self.templates[NotificationType.DELAYED.value],
            shipment_id=shipment_id,
            new_eta=new_eta,
            delay_reason=delay_reason
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.DELAYED,
            priority=Priority.HIGH,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_exception(self, phone: str, shipment_id: str, support_phone: str = "+1-800-LICS-HELP") -> Dict[str, Any]:
        """Send exception/problem notification"""
        message = self._format_message(
            self.templates[NotificationType.EXCEPTION.value],
            shipment_id=shipment_id,
            support_phone=support_phone
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.EXCEPTION,
            priority=Priority.CRITICAL,
            shipment_id=shipment_id
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_weather_alert(self, phone: str, weather_condition: str, location: str) -> Dict[str, Any]:
        """Send weather alert notification"""
        message = self._format_message(
            self.templates[NotificationType.WEATHER_ALERT.value],
            weather_condition=weather_condition,
            location=location
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.WEATHER_ALERT,
            priority=Priority.MEDIUM
        )
        
        return await self.sms_service.send_sms(notification)
    
    async def notify_emergency(self, phone: str, emergency_message: str, emergency_contact: str = "+1-911") -> Dict[str, Any]:
        """Send emergency notification"""
        message = self._format_message(
            self.templates[NotificationType.EMERGENCY.value],
            emergency_message=emergency_message,
            emergency_contact=emergency_contact
        )
        
        notification = SMSNotification(
            recipient_phone=phone,
            message=message,
            notification_type=NotificationType.EMERGENCY,
            priority=Priority.CRITICAL
        )
        
        return await self.sms_service.send_sms(notification)
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """Get recent notification history"""
        return self.sms_service.notification_history[-limit:]
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Get notification statistics"""
        history = self.sms_service.notification_history
        
        if not history:
            return {'total': 0, 'success_rate': 0, 'by_type': {}}
        
        total = len(history)
        successful = sum(1 for h in history if h.get('success'))
        success_rate = (successful / total) * 100 if total > 0 else 0
        
        by_type = {}
        for h in history:
            ntype = h.get('notification_type', 'unknown')
            if ntype not in by_type:
                by_type[ntype] = {'total': 0, 'successful': 0}
            by_type[ntype]['total'] += 1
            if h.get('success'):
                by_type[ntype]['successful'] += 1
        
        return {
            'total': total,
            'successful': successful,
            'success_rate': round(success_rate, 2),
            'by_type': by_type
        }

# Global instance for easy import
lics_notifier = LICSNotificationManager()

# Testing function
async def test_sms_system():
    """Test the SMS notification system"""
    print("Testing LICS SMS Notification System...")
    
    # Test phone number (replace with actual test number)
    test_phone = "+1234567890"  # Replace with actual test number
    test_shipment = "LICS-TEST-001"
    
    try:
        # Test shipment created notification
        result = await lics_notifier.notify_shipment_created(
            phone=test_phone,
            shipment_id=test_shipment
        )
        print(f"Shipment created notification: {result}")
        
        # Test in transit notification
        result = await lics_notifier.notify_in_transit(
            phone=test_phone,
            shipment_id=test_shipment,
            current_location="Distribution Center - Dallas",
            eta="Tomorrow 2:00 PM"
        )
        print(f"In transit notification: {result}")
        
        # Get stats
        stats = lics_notifier.get_notification_stats()
        print(f"Notification stats: {stats}")
        
    except Exception as e:
        print(f"Test error: {str(e)}")

if __name__ == "__main__":
    # Run test if executed directly
    asyncio.run(test_sms_system())