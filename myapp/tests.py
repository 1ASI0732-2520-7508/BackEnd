from django.test import TestCase
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.test import APIRequestFactory

from .models import Company, Supplier, Item, Category
from .serializers import UserSerializer, ItemSerializer
from .permission import IsEmployee


class ModelTests(TestCase):
    def test_company_str_and_unique_euc(self):
        c1 = Company.objects.create(company_name="Acme SA", company_euc="EU-001")
        self.assertEqual(str(c1), "Acme SA")
        # unique en company_euc
        with self.assertRaises(IntegrityError):
            Company.objects.create(company_name="Otra", company_euc="EU-001")

    def test_supplier_unique_ruc_and_str(self):
        comp = Company.objects.create(company_name="Acme", company_euc="EU-002")
        Supplier.objects.create(company=comp, supplier_name="Prov A", ruc_n="RUC-1")
        with self.assertRaises(IntegrityError):
            Supplier.objects.create(company=comp, supplier_name="Prov B", ruc_n="RUC-1")
        self.assertEqual(str(Supplier.objects.get(ruc_n="RUC-1")), "Prov A")

    def test_item_defaults_and_str(self):
        comp = Company.objects.create(company_name="Acme", company_euc="EU-003")
        sup = Supplier.objects.create(company=comp, supplier_name="Prov X", ruc_n="RUC-X")
        cat = Category.objects.create(category_name="Laptops")
        it = Item.objects.create(
            supplier=sup, category=cat, item_name="ThinkPad",
            unit_price="1234.56"
        )
        self.assertEqual(it.current_quantity, 0)
        self.assertEqual(it.minimum_stock_level, 0)
        self.assertEqual(str(it), "ThinkPad")


class SerializerTests(TestCase):
    def test_user_serializer_create_hashes_password_and_readonly_fields(self):

        User = get_user_model()
        comp = Company.objects.create(company_name="Acme", company_euc="EU-004")

        data = {
            "username": "sebas",
            "email": "s@x.com",
            "password": "p4ssw0rd",
            "company": comp.id
        }
        s = UserSerializer(data=data)
        self.assertTrue(s.is_valid(), msg=s.errors)
        u = s.save()

        # Password hasheado
        self.assertTrue(u.check_password("p4ssw0rd"))

        # Campos de solo lectura expuestos
        out = UserSerializer(u).data
        self.assertEqual(out["company_name"], "Acme")
        self.assertIsInstance(out["groups"], list)

    def test_item_serializer_exposes_supplier_and_category_names_read_only(self):
        comp = Company.objects.create(company_name="Acme", company_euc="EU-005")
        sup = Supplier.objects.create(company=comp, supplier_name="Prov Z", ruc_n="RUC-Z")
        cat = Category.objects.create(category_name="Monitores")
        item = Item.objects.create(
            supplier=sup, category=cat, item_name="UltraView",
            unit_price="999.99"
        )
        data = ItemSerializer(item).data
        self.assertEqual(data["supplier_name"], "Prov Z")
        self.assertEqual(data["category_name"], "Monitores")


class PermissionTests(TestCase):
    def test_is_employee_permission_allows_only_group_members(self):
        User = get_user_model()
        emp_group, _ = Group.objects.get_or_create(name="Employee")
        user_in = User.objects.create_user(username="in", password="x")
        user_in.groups.add(emp_group)
        user_out = User.objects.create_user(username="out", password="x")

        factory = APIRequestFactory()
        perm = IsEmployee()

        req_in = factory.get("/resource"); req_in.user = user_in
        req_out = factory.get("/resource"); req_out.user = user_out

        self.assertTrue(perm.has_permission(req_in, view=None))
        self.assertFalse(perm.has_permission(req_out, view=None))
