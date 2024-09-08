import os
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(username='admin', email='admin@example.com', password='admin')
    print(f'Superuser admin created.')
else:
    print(f'Superuser admin already exists.')
