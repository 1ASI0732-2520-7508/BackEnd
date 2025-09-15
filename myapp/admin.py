from django.contrib import admin
from .models import CustomUser, Company, Supplier, Item, Category


admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Supplier)
admin.site.register(Item)
admin.site.register(Category)
