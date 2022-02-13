
from django.db.models import query
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from .models import Category, Product, Cart, Order, Payment, MembershipForm, Contact, UserProfile
from store.serializers import CategorySerializer, ProductSerializer, CartSerializer, OrderSerializer, PaymentSerializer, MembershipFormSerializer, ContactSerializer

from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django_countries import countries
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_406_NOT_ACCEPTABLE
from rest_framework.views import APIView
from rest_framework import status, authentication, permissions
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework.exceptions import ValidationError, PermissionDenied, NotAcceptable
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse,JsonResponse
from rest_framework.authentication import SessionAuthentication

# Stripe
import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
# import paypalrestsdk
# import logging

# Create your views here.
class ListProductApi(APIView):
    """List all of the products in the Products table."""
    def get(self, request, format=None):
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class ProductDetail(APIView):
    def get_object_or_404(self, category_slug, product_slug):
        try:
            return Product.objects.filter(category__slug=category_slug).get(slug=product_slug)
        except Product.DoesNotExist:
            return Http404

    def get(self, request, category_slug, product_slug, format=None):
        product = self.get_object_or_404(category_slug, product_slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

class CategoryDetail(APIView):
    def get_object_or_404(self, category_slug):
        try:
            return Category.objects.get(slug=category_slug)
        except Category.DoesNotExist:
            return Http404

    def get(self, request, category_slug, format=None):
        category = self.get_object_or_404(category_slug)
        serializer = CategorySerializer(category)
        return Response(serializer.data)

@api_view(['POST'])
def search(request):
    query = request.data.get('query', '')

    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    else:
        return Response({'products': []})

class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)

# Add to cart
class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Cart.objects.none()
    serializer_class = CartSerializer

    def get_queryset(self):
        queryset = Cart.objects.filter(user=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        results =Cart.objects.filter(user=request.user)
        output_serializer = CartSerializer(results, many=True)
        data = output_serializer.data[:]
        order = Order.objects.create(user=request.user)
        for items in data:
            product = dict(items)
            products = product["id"]
        order.products.add(products)
        return Response(data)

# Order
class OrderDetailView(APIView):
    """List all of the products in the Products table."""
    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=HTTP_200_OK)

# class OrderDetailView(generics.RetrieveAPIView):
#     serializer_class = OrderSerializer
#     permission_classes = (IsAuthenticated,)

#     def get_object(self):
#         try:
#             order = Order.objects.get(user=self.request.user, ordered=False)
#             return order
#         except ObjectDoesNotExist:
#             raise Http404("You do not have an active order")


class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, id=id)
        order_qs = Order.objects.filter(
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.products.filter(product__id=product.id).exists():
                order_item = Cart.objects.filter(
                    product=product,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.products.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


class OrderItemDeleteView(generics.DestroyAPIView):
    queryset = Cart.objects.all()
    

#Checkout
@api_view(['POST'])
@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def checkout(request):
    serializer = OrderSerializer(data=request.data)
    order = Order.objects.get(user=request.user, ordered=False)

    if serializer.is_valid():
        stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
        amount = int(order.get_total_price() * 100)

        try:
            charge = stripe.Charge.create(
                amount=amount,
                currency='USD',
                description='Charge from Direshop777',
                source=serializer.validated_data['stripe_charge_id']
            )

            serializer.save(user=request.user)
            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = request.user
            payment.amount = order.get_total_price()
            payment.save()

            # assign the payment to the order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PaymentView(generics.ListCreateAPIView):
#     permission_classes = [IsAuthenticated] 
#     queryset = Order.objects.none
#     serializer_class = OrderSerializer

#     def get_queryset(self):
#         queryset = Order.objects.filter(user=self.request.user, ordered=False)
#         return queryset

#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         orders =Order.objects.filter(user=request.user, ordered=False)
#         output_serializer = OrderSerializer(orders, many=True)
#         # data = output_serializer.data[:]
#         stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
#         total = orders.get_total_price()
#         amount = int(total* 100)
#         try:
#             # charge the customer because we cannot charge the token more than once
#             charge = stripe.Charge.create(
#                 amount=amount,  # cents
#                 description='Charge from Direshop777',
#                 currency='usd',
#                 source=serializer.validated_data['stripe_charge_id']
#             )
            
#             # create the payment
#             payment = Payment()
#             payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = orders.get_total_price()
#             payment.save()

#             # assign the payment to the order
#             order_items = orders.products.all()
#             order_items.update(ordered=True)
#             for item in order_items:
#                 item.save()

#             orders.ordered = True
#             orders.payment = payment
#             orders.save()

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
            
#         except Exception:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()

class MembershipFormList(generics.ListCreateAPIView):
    queryset = MembershipForm.objects.all()
    serializer_class = MembershipFormSerializer

class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class StripeConfigView(APIView):
    """
    StripeConfigView is the API of configs resource, and
    responsible to handle the requests of /config/ endpoint.
    """
    def get(self, request, format=None):
        config = {
            "publishable_key": str(settings.STRIPE_TEST_PUBLIC_KEY)
        }
        return Response(config)