import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Auction_Site.settings')  # Replace 'Auction_Site' with your actual settings module folder name if different

application = get_wsgi_application()