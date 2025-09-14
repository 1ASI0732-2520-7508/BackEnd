from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Extend Django's AbstractUser for custom fields if needed, or use it directly
# For this example, we'll assume CompanyID is the only custom field needed on the User for now.
# If you don't need CompanyID on the User directly, you can remove CustomUser and use Django's User.
class CustomUser(AbstractUser):
    company = models.ForeignKey('Company', on_delete=models.SET_NULL, null=True, blank=True)
    # Add any other user-specific fields if necessary

    # To avoid clashes with auth.User groups and user_permissions
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        db_table = 'auth_user' # Ensure it uses the default auth_user table

    def __str__(self):
        return self.username

class Company(models.Model):
    company_name = models.CharField(max_length=255)
    company_euc = models.CharField(max_length=255, unique=True) # Assuming EUC is unique identifier

    def __str__(self):
        return self.company_name

class Supplier(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    supplier_name = models.CharField(max_length=255)
    ruc_n = models.CharField(max_length=255, unique=True) # Assuming RUC_N is unique
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

# Note: Django's Group model will be used for 'Role'.
# You would populate the Group model with 'Admin', 'User', etc.
# in your database or with fixtures.