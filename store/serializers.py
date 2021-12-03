from rest_framework import serializers
from .models import Category,Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact

from rest_framework.fields import CurrentUserDefault


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


class OrderProductSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = OrderProduct
        fields = '__all__'

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = Order
        fields = '__all__'

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class CheckoutAddressSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = CheckoutAddress
        fields = '__all__'

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class PaymentSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = Payment
        fields = '__all__'

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class MembershipFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipForm
        fields = '__all__'

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'