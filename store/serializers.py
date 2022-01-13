from django.db import models
from django.db.models import fields
from rest_framework import serializers
from .models import Category,Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact, Coupon, Cart

from rest_framework.fields import CurrentUserDefault
from django_countries.serializer_fields import CountryField


# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True)
    class Meta:
        model = Category
        fields = '__all__'

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

# Checkout Address Serializer
class CheckoutAddressSerializer(serializers.ModelSerializer):
    country = CountryField()
    class Meta:
        model = CheckoutAddress
        fields = '__all__'

class OrderProductSerializer(serializers.ModelSerializer):
    product =  ProductSerializer()
    get_total_product_price = serializers.IntegerField(read_only=True)
    get_final_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderProduct
        fields = '__all__'

    def get_product(self, obj):
        return ProductSerializer(obj.product).data

    def get_total_product_price(self, obj):
        return obj.get_total_product_price()

    def get_final_price(self, obj):
        return obj.get_final_price()

class OrderSerializer(serializers.ModelSerializer):
    products =  OrderProductSerializer(many=True)
    class Meta:
        model = Order
        fields = '__all__'

    def get_order_items(self, obj):
        return OrderProductSerializer(obj.products.all(), many=True).data

    def get_total_price(self, obj):
        return obj.get_total_price()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False)
    class Meta:
        model = Cart
        fields = '__all__'

class MembershipFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipForm
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'