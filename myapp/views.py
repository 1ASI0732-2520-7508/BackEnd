from rest_framework import viewsets, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .serializers import (
    UserSerializer, CompanySerializer, SupplierSerializer,
    ItemSerializer, CategorySerializer, GroupSerializer
)
from .models import Company, Supplier, Item, Category

User = get_user_model()

# Custom Token Serializer to include user data
class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['company_id'] = user.company_id if user.company else None
        token['company_name'] = user.company.company_name if user.company else None
        token['groups'] = [group.name for group in user.groups.all()]
        # ... you can add more user data here

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] # Only authenticated users can list/retrieve

    def get_permissions(self):
        if self.action in ['create']: # For registration (if you want an open registration)
            self.permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']: # Only admins can modify/delete users
            self.permission_classes = [permissions.IsAdminUser]
        return super().get_permissions()

    # You might want to override create method for user registration with password hashing
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(**serializer.validated_data)
        headers = self.get_success_headers(serializer.data)
        return Response(UserSerializer(user).data, status=201, headers=headers)

class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]



class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

# You might want a dedicated endpoint to get the current authenticated user's details
class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

# View for listing all groups (roles)
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser] # Only admins can manage groups