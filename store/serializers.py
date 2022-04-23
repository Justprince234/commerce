from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import Category,Product, Cart, Order, MembershipForm, Contact
from rest_framework_recursive.fields import RecursiveField
from rest_framework.fields import CurrentUserDefault
from django_countries.serializer_fields import CountryField
from accounts.models import User


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value

# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id']

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)
    products = ProductSerializer(many=True)
    class Meta:
        model = Category
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    product = serializers.SerializerMethodField(read_only=True)
    total_product_price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = '__all__'

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

    def get_total_product_price(self, obj):
        return obj.get_total_product_price()

    def get_final_price(self, obj):
        return obj.get_final_price()

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["user"] = self.fields["user"].get_default()
        return super().save(**kwargs)

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    products = serializers.PrimaryKeyRelatedField(queryset=Cart.objects.all(), many=True)
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'

    def get_order_products(self, obj):
        return CartSerializer(obj.products.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total_price()

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["user"] = self.fields["user"].get_default()
        return super().save(**kwargs)

class MembershipFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipForm
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'