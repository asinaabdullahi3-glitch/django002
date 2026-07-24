import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# Add project root to Python path so imports like "config.settings" resolve correctly.
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.prod")

application = get_wsgi_application()
