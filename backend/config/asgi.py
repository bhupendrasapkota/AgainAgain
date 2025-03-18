import os
from django.core.asgi import get_asgi_application

ENV = os.getenv('DJANGO_ENV', 'development')

if ENV == 'production':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

application = get_asgi_application()
