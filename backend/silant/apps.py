from django.apps import AppConfig


class SilantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'silant'
    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import ensure_groups_and_perms
        post_migrate.connect(ensure_groups_and_perms, sender=self)