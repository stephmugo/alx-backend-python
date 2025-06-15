from django.apps import AppConfig


class MessagingConfig(AppConfig):
    """
    Application configuration for the messaging app.
    
    Handles initialization of the messaging module including
    signal registration when Django starts up.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    
    def ready(self):
       
        try:
            # Import signals to register handlers
            import messaging.signals  # Note: corrected 'signal' to 'signals'
        except ImportError as e:
            # Log the error but don't crash the application
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to import messaging signals: {e}")