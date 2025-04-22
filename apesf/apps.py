from django.apps import AppConfig

class ApesfConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apesf'

    def ready(self):
        import apesf.signals  # Charge les signaux