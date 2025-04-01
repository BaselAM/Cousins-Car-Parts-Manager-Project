"""
OpenAI integration with fallback capability.
"""

from logger import get_logger
from .local_responder import LocalChatResponder
from .car_knowledge_base import CarPartsKnowledgeBase

# Get a module-specific logger
logger = get_logger(__name__)

# Import OpenAI package if available
OPENAI_AVAILABLE = False
try:
    import openai

    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not available. Will use local response generator.")


class OpenAIChat:
    """OpenAI chat integration with automatic fallback to local responses when needed"""

    def __init__(self, api_key=None, model="gpt-3.5-turbo", temperature=0.7, max_tokens=150):
        """Initialize with optional API key and configurable parameters"""
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.client = None

        # Initialize knowledge base and fallback responder
        self.car_knowledge = CarPartsKnowledgeBase()
        self.fallback = LocalChatResponder(car_knowledge=self.car_knowledge)

        # Determine if we should use fallback mode
        self.use_fallback_mode = not OPENAI_AVAILABLE

        # Initialize system prompt
        self.messages = [
            {"role": "system", "content": (
                "You are a helpful assistant specialized in providing information about car parts "
                "and vehicle maintenance. Provide concise, informative responses. "
                "You should respond in multiple languages including Hebrew. "
                "Match your response language to the user's language."
            )}
        ]

        # Try to set up the client if we have an API key
        if api_key and OPENAI_AVAILABLE:
            self.setup_client(api_key)

    def setup_client(self, api_key):
        """Set up the OpenAI client with the given API key"""
        if not OPENAI_AVAILABLE:
            self.use_fallback_mode = True
            logger.warning("OpenAI package not available. Using fallback mode.")
            return

        self.api_key = api_key
        if api_key:
            try:
                self.client = openai.OpenAI(api_key=api_key)
                self.use_fallback_mode = False
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")
                self.use_fallback_mode = True
        else:
            self.client = None
            self.use_fallback_mode = True
            logger.info("No API key provided. Using fallback mode.")

    def get_response(self, message):
        """Get a response from OpenAI API or fallback to local responses if needed"""
        # First, check if it's a specific car parts query in our knowledge base
        if self.car_knowledge.is_car_parts_query(message):
            car_info = self.car_knowledge.search(message)
            if car_info:
                logger.debug("Found car parts information in knowledge base")
                return car_info

        # Check if we should use fallback mode
        if self.use_fallback_mode or not OPENAI_AVAILABLE or not self.client or not self.api_key:
            logger.debug("Using local response generator")
            return self.fallback.get_response(message)

        # Add user message to history
        self.messages.append({"role": "user", "content": message})

        # Trim conversation history if it gets too long (keep last 5 messages plus system prompt)
        if len(self.messages) > 6:
            self.messages = [self.messages[0]] + self.messages[-5:]

        try:
            # Call the OpenAI API
            logger.debug(f"Sending request to OpenAI API with model: {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Extract and store the response
            ai_response = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": ai_response})
            logger.debug("Received successful response from OpenAI API")

            return ai_response

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")

            # Check for quota exceeded errors and permanently switch to fallback mode
            error_str = str(e).lower()
            if any(x in error_str for x in ['quota', 'rate limit', 'capacity']):
                self.use_fallback_mode = True
                logger.warning("Permanently switching to fallback mode due to API limits")

            # Use fallback for this response
            logger.info("Falling back to local response generator")
            return self.fallback.get_response(message)