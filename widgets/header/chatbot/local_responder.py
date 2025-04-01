"""
Local response generator for chat without API dependency.
"""

import re
import random
from .car_knowledge_base import CarPartsKnowledgeBase


class LocalChatResponder:
    """Provides local fallback responses without requiring API access"""

    def __init__(self, username="User", car_knowledge=None):
        """Initialize with username for personalized responses"""
        self.username = username
        self.car_knowledge = car_knowledge or CarPartsKnowledgeBase()
        self.initialize_responses()

    def initialize_responses(self):
        """Set up response patterns"""
        # Response patterns with multiple options
        self.response_patterns = {
            # General conversation patterns
            r'hello|hi|hey': [
                f"Hello {self.username}! How can I help you today?",
                f"Hi {self.username}! I'm your assistant. What do you need help with?",
                "Hello there! How may I help you today?"
            ],
            r'how are you': [
                "I'm doing well, thanks for asking! How can I help you?",
                "I'm functioning perfectly. What can I assist you with today?",
                "All systems operational! How can I be of service?"
            ],
            r'your name|who are you': [
                "I'm your built-in AI assistant, designed to help with your queries.",
                "I'm an AI assistant integrated into this application to provide help and information.",
                "I'm your virtual assistant, ready to answer questions and provide assistance."
            ],
            r'thanks|thank you': [
                "You're welcome! Feel free to ask if you need anything else.",
                "Happy to help! Let me know if you need more assistance.",
                "Anytime! That's what I'm here for."
            ],
            r'bye|goodbye': [
                "Goodbye! Feel free to chat again when you need assistance.",
                "Until next time! I'll be here if you need help.",
                "Bye! You can reopen this chat whenever you need me."
            ],
            r'help|assist': [
                "I can help with questions about car parts and vehicle maintenance. Just ask!",
                "Need assistance? I'm here to help you with car-related questions.",
                "How can I assist you today? I'm knowledgeable about cars and their components."
            ],

            # Car-specific patterns
            r'engine|motor': [
                "The engine is the power unit of a vehicle, converting fuel into motion through combustion.",
                "Car engines can be classified as inline, V-type, or flat configurations based on cylinder arrangement.",
                "Modern engines feature electronic fuel injection, variable valve timing, and turbocharging for efficiency."
            ],
            r'brake|brakes': [
                "Brakes are crucial safety components that slow or stop the vehicle using friction.",
                "Most cars use disc brakes in front and either disc or drum brakes in the rear.",
                "The brake system includes pads, rotors, calipers, lines, and the master cylinder."
            ],
            r'transmission|gearbox': [
                "The transmission transfers power from the engine to the wheels while allowing gear ratio changes.",
                "Common types include manual, automatic, CVT (Continuously Variable Transmission), and dual-clutch.",
                "Transmission problems often manifest as delayed shifting, strange noises, or fluid leaks."
            ],
            r'suspension|shock': [
                "The suspension system provides a smooth ride by absorbing road imperfections.",
                "Key components include springs, shock absorbers, struts, control arms, and sway bars.",
                "Signs of suspension issues include excessive bouncing, uneven tire wear, and pulling to one side."
            ],
            r'battery|electrical': [
                "The car battery provides power for starting and for electrical systems when the engine is off.",
                "Most modern vehicles use 12-volt lead-acid batteries, though some hybrids use different types.",
                "Battery issues often appear as slow starting, dimming lights, or electrical system failures."
            ],
            r'oil|lubrication': [
                "Engine oil lubricates moving parts, reduces friction, helps with cooling, and prevents corrosion.",
                "It's important to change your oil and filter regularly according to the manufacturer's schedule.",
                "Low oil pressure or contaminated oil can cause serious engine damage and reduced performance."
            ],
            r'tire|wheel': [
                "Tires are your only contact with the road and affect handling, braking, and fuel economy.",
                "Regular rotation, proper inflation, and alignment checks extend tire life and improve safety.",
                "Tire pressure should be checked monthly, and tires should be replaced when tread depth is low."
            ],
            r'fuel|gas|petrol|diesel': [
                "The fuel system delivers the right amount of fuel to the engine for combustion.",
                "Components include the tank, pump, filter, injectors or carburetor, and fuel lines.",
                "Using the recommended fuel grade for your vehicle helps maintain performance and efficiency."
            ],
            r'cooling|radiator|overheat': [
                "The cooling system prevents engine overheating by circulating coolant and releasing heat.",
                "Key components include the radiator, water pump, thermostat, hoses, and cooling fans.",
                "Overheating can cause serious engine damage and should be addressed immediately."
            ],

            # Hebrew patterns
            r'שלום|היי': [
                f"שלום {self.username}! במה אוכל לעזור לך היום?",
                f"היי {self.username}! אני העוזר הדיגיטלי שלך. איך אוכל לסייע?",
                "שלום! במה אוכל לעזור?"
            ],
            r'תודה': [
                "בשמחה! אם תצטרך עוד עזרה, אני כאן.",
                "בכיף! אשמח לעזור בכל דבר נוסף.",
                "תמיד לשירותך!"
            ],
            r'להתראות|ביי': [
                "להתראות! אשמח לעזור שוב בפעם הבאה.",
                "ביי! אני כאן אם תצטרך עוד משהו.",
                "להתראות! תוכל לפתוח את הצ'אט בכל פעם שתרצה."
            ],
            r'מנוע': [
                "המנוע הוא יחידת הכוח של הרכב שממירה דלק לתנועה באמצעות בעירה.",
                "מנועי רכב יכולים להיות מסווגים כתצורת שורה, V או שטוחה על פי סידור הצילינדרים.",
                "מנועים מודרניים כוללים הזרקת דלק אלקטרונית, תזמון שסתומים משתנה וטורבו ליעילות."
            ],
            r'בלמים': [
                "הבלמים הם רכיבי בטיחות קריטיים שמאטים או עוצרים את הרכב באמצעות חיכוך.",
                "רוב המכוניות משתמשות בבלמי דיסק בחזית ובלמי דיסק או תוף מאחור.",
                "מערכת הבלימה כוללת רפידות, דיסקיות, קליפרים, צינורות ובוכנת בלם ראשית."
            ]
        }

        # Default responses for when no pattern matches
        self.default_responses = [
            f"I'm here to help with car-related questions. What would you like to know about your vehicle?",
            "I can provide information about car parts and maintenance. How can I assist you?",
            "I'm specialized in automotive information. What car component are you interested in learning about?",
            "I'm ready to help with your vehicle questions. What would you like to know about car parts or maintenance?"
        ]

        # Hebrew default responses
        self.hebrew_default_responses = [
            f"אני כאן כדי לעזור עם שאלות הקשורות לרכב. מה תרצה לדעת על הרכב שלך?",
            "אני יכול לספק מידע על חלקי רכב ותחזוקה. כיצד אוכל לסייע לך?",
            "אני מתמחה במידע על רכב. באיזה רכיב ברכב אתה מעוניין ללמוד עליו?",
            "אני מוכן לעזור עם שאלות הרכב שלך. מה תרצה לדעת על חלקי רכב או תחזוקה?"
        ]

    def is_hebrew(self, text):
        """Detect if text contains Hebrew characters"""
        hebrew_pattern = re.compile(r'[\u0590-\u05FF\u05D0-\u05EA\u05F0-\u05F4]+')
        return bool(hebrew_pattern.search(text))

    def get_response(self, message):
        """Generate a response based on the message content"""
        # First, check the car parts knowledge base
        if self.car_knowledge.is_car_parts_query(message):
            car_info = self.car_knowledge.search(message)
            if car_info:
                return car_info

        # Check if message is in Hebrew
        is_heb = self.is_hebrew(message)
        message_lower = message.lower()

        # Check patterns for matches
        for pattern, responses in self.response_patterns.items():
            if re.search(pattern, message_lower):
                return random.choice(responses)

        # If no pattern matches, use default responses
        if is_heb:
            return random.choice(self.hebrew_default_responses)
        else:
            return random.choice(self.default_responses)