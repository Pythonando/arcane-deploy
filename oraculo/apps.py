from django.apps import AppConfig


class OraculoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'oraculo'

    def ready(self):
        import oraculo.signals