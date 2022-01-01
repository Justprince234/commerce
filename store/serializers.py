from rest_framework import serializers
from .models import Category,Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact, Coupon

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
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    country = CountryField()
    class Meta:
        model = CheckoutAddress
        fields = '__all__'

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)


class OrderProductSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
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


    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class OrderSerializer(serializers.ModelSerializer):
    products =  OrderProductSerializer(many=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
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

    def save(self, **kwargs):
        """Include default for read_only `account` field"""
        kwargs["owner"] = self.fields["owner"].get_default()
        return super().save(**kwargs)

class PaymentSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=serializers.CurrentUserDefault())
    class Meta:
        model = Payment
        fields = '__all__'

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

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
