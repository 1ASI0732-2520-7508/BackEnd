from django.apps import AppConfig


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from .models import Item, Category, Company
        from auditlog.registry import auditlog
        
        auditlog.register(Item)
        auditlog.register(Category)
        auditlog.register(Company)