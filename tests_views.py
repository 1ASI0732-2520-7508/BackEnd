# myapp/tests_views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken

from myapp.models import Company, Supplier, Item, Category
from myapp.views import (
    MyTokenObtainPairView,
    UserViewSet,
    CompanyViewSet,
    SupplierViewSet,
    CategoryViewSet,
    ItemViewSet,
    CurrentUserView,
    GroupViewSet,
    LogEntryViewSet,
)

User = get_user_model()


class ControllerTestBase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()

        # Datos base
        self.company = Company.objects.create(company_name="Acme", company_euc="EU-001")
        self.emp_group = Group.objects.create(name="Employee")
        self.mgr_group = Group.objects.create(name="Manager")

        # Usuario normal
        self.user = User.objects.create_user(
            username="sebas", email="s@x.com", password="p4ss", company=self.company
        )
        self.user.groups.add(self.emp_group)

        # Admin
        self.admin = User.objects.create_user(
            username="admin", email="a@x.com", password="admin123",
            company=self.company, is_staff=True, is_superuser=True
        )
        self.admin.groups.add(self.mgr_group)

        # Entidades auxiliares
        self.category = Category.objects.create(category_name="Electrónica")
        self.supplier = Supplier.objects.create(
            company=self.company, supplier_name="Proveedor X", ruc_n="RUC-0001"
        )


class TestAuthToken(ControllerTestBase):


    def test_token_incluye_claims_personalizados(self):
        view = MyTokenObtainPairView.as_view()
        req = self.factory.post("/api/token/", {"username": "sebas", "password": "p4ss"}, format="json")
        resp = view(req)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data)

        claims = AccessToken(resp.data["access"])
        self.assertEqual(claims["username"], "sebas")
        self.assertEqual(claims["email"], "s@x.com")
        self.assertEqual(claims["company_id"], self.company.id)
        self.assertEqual(claims["company_name"], "Acme")
        self.assertIn("Employee", claims["groups"])


class TestUserViewSet(ControllerTestBase):


    def test_create_usuario_abierto(self):
        view = UserViewSet.as_view({"post": "create"})
        payload = {
            "username": "nuevo",
            "email": "n@x.com",
            "password": "clave123",
            "company": self.company.id,
        }
        req = self.factory.post("/users/", payload, format="json")  # create es AllowAny
        resp = view(req)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["username"], "nuevo")

    def test_list_requiere_autenticacion(self):
        view = UserViewSet.as_view({"get": "list"})
        req = self.factory.get("/users/")
        # sin auth debe negar (401/403 según settings); probamos con auth para éxito
        force_authenticate(req, user=self.user)
        resp = view(req)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_update_solo_admin(self):
        otro = User.objects.create_user(username="otro", password="x", company=self.company)

        # no admin → 403
        view = UserViewSet.as_view({"patch": "partial_update"})
        req = self.factory.patch(f"/users/{otro.pk}/", {"email": "nuevo@x.com"}, format="json")
        force_authenticate(req, user=self.user)
        resp = view(req, pk=otro.pk)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

        # admin → 200
        req2 = self.factory.patch(f"/users/{otro.pk}/", {"email": "ok@x.com"}, format="json")
        force_authenticate(req2, user=self.admin)
        resp2 = view(req2, pk=otro.pk)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertEqual(resp2.data["email"], "ok@x.com")


class TestCompanyViewSet(ControllerTestBase):


    def test_company_create_y_list(self):
        # create
        create_v = CompanyViewSet.as_view({"post": "create"})
        req_c = self.factory.post("/companies/", {"company_name": "Beta", "company_euc": "EU-002"}, format="json")
        force_authenticate(req_c, user=self.user)
        resp_c = create_v(req_c)
        self.assertEqual(resp_c.status_code, status.HTTP_201_CREATED)

        # list
        list_v = CompanyViewSet.as_view({"get": "list"})
        req_l = self.factory.get("/companies/")
        force_authenticate(req_l, user=self.user)
        resp_l = list_v(req_l)
        self.assertEqual(resp_l.status_code, status.HTTP_200_OK)
        self.assertTrue(any(c["company_name"] == "Beta" for c in resp_l.data))


class TestSupplierViewSet(ControllerTestBase):


    def test_supplier_create_y_list(self):
        create_v = SupplierViewSet.as_view({"post": "create"})
        payload = {
            "company": self.company.id,
            "supplier_name": "Prov Nuevo",
            "ruc_n": "RUC-NEW-1",
            "address": "Av. 123",
        }
        req_c = self.factory.post("/suppliers/", payload, format="json")
        force_authenticate(req_c, user=self.user)
        resp_c = create_v(req_c)
        self.assertEqual(resp_c.status_code, status.HTTP_201_CREATED)

        list_v = SupplierViewSet.as_view({"get": "list"})
        req_l = self.factory.get("/suppliers/")
        force_authenticate(req_l, user=self.user)
        resp_l = list_v(req_l)
        self.assertEqual(resp_l.status_code, status.HTTP_200_OK)
        self.assertTrue(any(s["supplier_name"] == "Prov Nuevo" for s in resp_l.data))


class TestCategoryViewSet(ControllerTestBase):


    def test_category_create_y_list(self):
        create_v = CategoryViewSet.as_view({"post": "create"})
        req_c = self.factory.post("/categories/", {"category_name": "Periféricos"}, format="json")
        force_authenticate(req_c, user=self.user)
        resp_c = create_v(req_c)
        self.assertEqual(resp_c.status_code, status.HTTP_201_CREATED)

        list_v = CategoryViewSet.as_view({"get": "list"})
        req_l = self.factory.get("/categories/")
        force_authenticate(req_l, user=self.user)
        resp_l = list_v(req_l)
        self.assertEqual(resp_l.status_code, status.HTTP_200_OK)
        self.assertTrue(any(c["category_name"] == "Periféricos" for c in resp_l.data))


class TestItemViewSet(ControllerTestBase):


    def test_item_create_y_list(self):
        create_v = ItemViewSet.as_view({"post": "create"})
        payload = {
            "supplier": self.supplier.id,
            "category": self.category.id,
            "item_name": "ThinkPad X",
            "current_quantity": 5,
            "minimum_stock_level": 1,
            "unit_price": "1200.00",
            "description": "Laptop",
        }
        req_c = self.factory.post("/items/", payload, format="json")
        force_authenticate(req_c, user=self.user)
        resp_c = create_v(req_c)
        self.assertEqual(resp_c.status_code, status.HTTP_201_CREATED)

        list_v = ItemViewSet.as_view({"get": "list"})
        req_l = self.factory.get("/items/")
        force_authenticate(req_l, user=self.user)
        resp_l = list_v(req_l)
        self.assertEqual(resp_l.status_code, status.HTTP_200_OK)
        self.assertTrue(any(i["item_name"] == "ThinkPad X" for i in resp_l.data))


class TestCurrentUserView(ControllerTestBase):


    def test_current_user_get(self):
        view = CurrentUserView.as_view()
        req = self.factory.get("/me/")
        force_authenticate(req, user=self.user)
        resp = view(req)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["username"], "sebas")
        self.assertEqual(resp.data["company_name"], "Acme")


class TestGroupViewSet(ControllerTestBase):


    def test_group_list_admin_only(self):
        view = GroupViewSet.as_view({"get": "list"})


        req1 = self.factory.get("/groups/")
        force_authenticate(req1, user=self.user)
        resp1 = view(req1)
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)


        req2 = self.factory.get("/groups/")
        force_authenticate(req2, user=self.admin)
        resp2 = view(req2)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp2.data), 1)  # Employee/Manager ya existen


class TestLogEntryViewSet(ControllerTestBase):


    def test_logentry_list_admin_only(self):
        view = LogEntryViewSet.as_view({"get": "list"})


        req1 = self.factory.get("/audit/logs/")
        force_authenticate(req1, user=self.user)
        resp1 = view(req1)
        self.assertEqual(resp1.status_code, status.HTTP_403_FORBIDDEN)


        req2 = self.factory.get("/audit/logs/")
        force_authenticate(req2, user=self.admin)
        resp2 = view(req2)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
