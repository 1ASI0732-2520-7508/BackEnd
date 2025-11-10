from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import Company, Supplier, Item, Category



class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(
        queryset = Group.objects.all(), 
        required = False,
        allow_null = False
    )
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password',
                   'company', 'company_name', 'group')
        extra_kwargs ={ 'password': {'write_only': True} }

    def create(self, validated_data):
        group = validated_data.pop('group', None)
        password = validated_data.pop('password', None)
        ##user = User(**validated_data)
        
        user = User.objects.create_user(password = password, **validated_data)
        
        # if password:
        #     user.set_password(password)
        # user.save()

        if group:
            user.groups.set([group])
        return user
    
    def update(self, instance, validated_data):
        groups_data = validated_data.pop('groups', None)
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()

        if groups_data is not None:
            instance.groups.set(groups_data)

        return instance
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'

class SupplierSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'
        read_only_fields = ('company_name',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.supplier_name', read_only=True)
    category_name = serializers.CharField(source='category.category_name', read_only=True)

    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('supplier_name', 'category_name')