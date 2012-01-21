import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'joiarara.settings'
sys.path.append('/root/joiarara')
sys.path.append('/root')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
