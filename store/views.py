
from django.db.models import query
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from config.settings import BRAINTREE_CONF

from .models import Category, Product, Cart, Order, MembershipForm, Contact, UserProfile
from store.serializers import CategorySerializer, ProductSerializer, CartPostSerializer, OrderSerializer, MembershipFormSerializer, ContactSerializer, CartGetSerializer

from rest_framework import viewsets
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django_countries import countries
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
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
from django.views.decorators.http import require_http_methods
from rest_framework import serializers

# Braintree
import braintree

# instantiate Braintree payment gateway
gateway = braintree.BraintreeGateway(BRAINTREE_CONF)


# Create your views here.
class ListProduct(generics.ListCreateAPIView):    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class DetailProduct(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ListCategory(generics.ListCreateAPIView):
    queryset = Category.objects.filter(parent__isnull=True)
    serializer_class = CategorySerializer

class DetailCategory(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

# class ListCart(generics.ListCreateAPIView):
#     # permission_classes = (permissions.IsAuthenticated,)
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

class DetailCart(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartPostSerializer 

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
class CartGetView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Cart.objects.none()
    serializer_class = CartGetSerializer

    def get_queryset(self):
        queryset = Cart.objects.filter(user=self.request.user)
        print(queryset)
        return queryset

class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated] 
    queryset = Cart.objects.none()
    serializer_class = CartPostSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        results =Cart.objects.filter(user=request.user)
        output_serializer = CartPostSerializer(results, many=True)
        data = output_serializer.data[:]
        order = Order.objects.create(user=request.user)
        for items in data:
            product = dict(items)
            products = product["id"]
        order.products.add(products)
        return Response(data)

class BraintreeClientTokenView(APIView):
    """Generate and return client token."""
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        self.user = request.user
        customer_kwargs = {
            "first_name": self.user.first_name,
            "last_name": self.user.surname,
            "email": self.user.email,
        }
        customer_result = braintree.Customer.create(customer_kwargs)
        customer_id = customer_result.customer.id
        client_token = braintree.ClientToken.generate({
                'customer_id': customer_id
            })
        return Response(client_token)



#Checkout
class Checkout(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer


    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        return queryset

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(context={'request': request}, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.user = request.user
        customer_kwargs = {
            "first_name": self.user.first_name,
            "last_name": self.user.surname,
            "email": self.user.email,
        }
        customer_result = braintree.Customer.create(customer_kwargs)
        customer_id = customer_result.customer.id
        nonce = request.data.get("payment_method_nonce")
        user_profile = UserProfile.objects.filter(user=request.user)
        orders =Order.objects.filter(user=request.user, paid=False)
        for items in orders:
            total = items.get_total_price()
        try:
            # charge the customer because we cannot charge the token more than once
            result = braintree.Transaction.sale({
                'customer_id': customer_id,
                'amount': str(total),
                'payment_method_nonce': nonce,
                'descriptor': {'name': 'DIRESHOP777'},
                'options': {
                    'submit_for_settlement': True,
                    'store_in_vault_on_success': True
                    }
                })
            if result.is_success:
                user_profile.braintree_id = result.transaction.id
                user_profile.save()
                orders.paid = True
                orders.save()
            serializer.save(user=request.user)
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)  
        except Exception:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ListCart(generics.ListCreateAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

# class DetailCart(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = (permissions.IsAuthenticated,)
#     queryset = Cart.objects.all()
#     serializer_class = CartSerializer

# Order
class OrderDetailView(APIView):
    """List all of the order in the order table."""
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
    

class MembershipFormList(generics.ListCreateAPIView):
    queryset = MembershipForm.objects.all()
    serializer_class = MembershipFormSerializer

class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

class BraintreeConfigView(APIView):
    """
    BraintreeConfigView is the API of configs resource, and
    responsible to handle the requests of /config/ endpoint.
    """
    def get(self, request, format=None):
        config = {
            "publishable_key": str(settings.BRAINTREE_PUBLIC_KEY)
        }
        return Response(config)

class BraintreeTokenizationView(APIView):
    """
    BraintreeTokenizationView is the API of configs resource, and
    responsible to handle the requests of Tokenization endpoint.
    """
    def get(self, request, format=None):
        config = {
            "Tokenization_Key": "sandbox_s96mdk2n_x8k6mngqj2qz555h"
        }
        return Response(config)