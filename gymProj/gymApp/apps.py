from django.apps import AppConfig


class GymappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "gymApp"

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import grant_group_perms

        post_migrate.connect(grant_group_perms, sender=self)
