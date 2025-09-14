from django.contrib import admin
from .models import CustomUser, Company, Supplier, Item, Category

# Register your models here.


admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(Supplier)
admin.site.register(Item)
admin.site.register(Category)
