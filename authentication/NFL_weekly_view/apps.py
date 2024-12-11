from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication.NFL_weekly_view'

    def ready(self):
        import authentication.NFL_weekly_view.signals  # Import signals related to the 'authentication' app