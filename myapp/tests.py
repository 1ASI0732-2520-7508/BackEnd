from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken
import jwt

from .models import Company, Supplier, Category, Item
from .serializers import UserSerializer


User = get_user_model()


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(
            company_name="Acme Corp",
            company_euc="ACME123"
        )
        self.manager_group = Group.objects.create(name="Manager")

    def _create_user(self, username="manager", password="StrongPass123!", *, is_staff=False, is_superuser=False):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
            company=self.company,
        )
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save(update_fields=["is_staff", "is_superuser"])
        return user

    def _auth_header(self, user):
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(token)}"}

    def test_user_serializer_creates_user_with_group_and_hashed_password(self):
        serializer = UserSerializer(
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "StrongPass123!",
                "group": self.manager_group.pk,
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertIn(self.manager_group, user.groups.all())

    def test_obtain_token_includes_custom_claims(self):
        user = self._create_user()
        user.groups.add(self.manager_group)

        url = reverse("token_obtain_pair")
        response = self.client.post(
            url,
            {"username": user.username, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]
        decoded = jwt.decode(
            access_token,
            settings.SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )

        self.assertEqual(decoded["username"], user.username)
        self.assertEqual(decoded["email"], user.email)
        self.assertEqual(decoded["company_id"], user.company_id)
        self.assertIn("Manager", decoded["groups"])

    def test_current_user_endpoint_returns_authenticated_user(self):
        user = self._create_user(username="employee")
        headers = self._auth_header(user)

        response = self.client.get(reverse("current_user"), **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], user.username)
        self.assertEqual(response.data["company"], user.company_id)

    def test_items_endpoint_requires_authentication(self):
        response = self.client.get(reverse("item-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_list_items(self):
        supplier = Supplier.objects.create(
            company=self.company,
            supplier_name="Supplier One",
            ruc_n="SUP123456",
        )
        category = Category.objects.create(category_name="Electronics")
        item = Item.objects.create(
            supplier=supplier,
            category=category,
            item_name="Laptop",
            current_quantity=10,
            minimum_stock_level=2,
            unit_price="1200.00",
            description="Ultrabook",
        )

        user = self._create_user(username="inventory_user")
        headers = self._auth_header(user)

        response = self.client.get(reverse("item-list"), **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["item_name"], item.item_name)
        self.assertEqual(response.data[0]["supplier_name"], supplier.supplier_name)
        self.assertEqual(response.data[0]["category_name"], category.category_name)

    def test_group_endpoint_requires_admin_privileges(self):
        admin_user = self._create_user(username="admin", is_staff=True, is_superuser=True)
        regular_user = self._create_user(username="regular")

        response = self.client.get(reverse("group-list"), **self._auth_header(admin_user))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse("group-list"), **self._auth_header(regular_user))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
