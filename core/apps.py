from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Only run this logic on Render or when explicitly triggered
        if os.environ.get('AUTO_CREATE_SUPERUSER') == 'True':
            from django.contrib.auth import get_user_model
            from django.db.utils import OperationalError, ProgrammingError

            try:
                User = get_user_model()
                username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
                email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@chams.com')
                password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'securepassword123')

                if not User.objects.filter(username=username).exists():
                    User.objects.create_superuser(username=username, email=email, password=password)
                    print(">>> Superuser created successfully via startup routine!")
            except (OperationalError, ProgrammingError):
                # Handles cases where database tables haven't been migrated yet on initial boot
                pass