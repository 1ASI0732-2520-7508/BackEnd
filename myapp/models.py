from django.db import models
from django.contrib.auth.models import AbstractUser, Group



class CustomUser(AbstractUser):
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)

    # To avoid clashes with auth.User groups and user_permissions
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'auth_user' # Ensure it uses the default auth_user table

    def __str__(self):
        return self.username

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    company_euc = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.company_name

class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=255)
    ruc_n = models.CharField(max_length=255, unique=True) 
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.supplier_name

class Item(models.Model):
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    item_name = models.CharField(max_length=255)
    current_quantity = models.IntegerField(default=0)
    minimum_stock_level = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.item_name

class Category(models.Model):
    category_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.category_name

