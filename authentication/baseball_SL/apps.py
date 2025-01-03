from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication.baseball_SL'

    def ready(self):
        import authentication.baseball_SL.signals  # Import signals related to the 'authentication' app