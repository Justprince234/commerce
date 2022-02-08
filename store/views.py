
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
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        for items in data:
            product = dict(items)
            products = product["id"]
        order.products.add(products)
        return Response(data)

# Order
class OrderDetailView(APIView):
    """List all of the products in the Products table."""
    def get(self, request, format=None):
        products = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(products, many=True)
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
        amount = int(order.get_total() * 100)

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
            payment.amount = order.get_total()
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

# class PaymentView(APIView):

#     def post(self, request, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         userprofile = UserProfile.objects.get(user=self.request.user)
#         token = request.data.get('stripeToken')

#         if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
#             customer = stripe.Customer.retrieve(
#                 userprofile.stripe_customer_id)
#             customer.sources.create(source=token)

#         else:
#             customer = stripe.Customer.create(
#                 email=self.request.user.email,
#             )
#             customer.sources.create(source=token)
#             userprofile.stripe_customer_id = customer['id']
#             userprofile.one_click_purchasing = True
#             userprofile.save()

#         amount = int(order.get_total() * 100)

#         try:
#             # charge the customer because we cannot charge the token more than once
#             charge = stripe.Charge.create(
#                 amount=amount,  # cents
#                 description="Direshop777 Charge.",
#                 currency="usd",
#                 customer=userprofile.stripe_customer_id
#             )
            
#             # create the payment
#             payment = Payment()
#             payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = order.get_total()
#             payment.save()

#             # assign the payment to the order

#             order_items = order.items.all()
#             order_items.update(ordered=True)
#             for item in order_items:
#                 item.save()

#             order.ordered = True
#             order.payment = payment
#             order.save()

#             return Response(status=HTTP_200_OK)

#         except stripe.error.CardError as e:
#             body = e.json_body
#             err = body.get('error', {})
#             return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

#         except stripe.error.RateLimitError as e:
#             # Too many requests made to the API too quickly
#             messages.warning(self.request, "Rate limit error")
#             return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

#         except stripe.error.InvalidRequestError as e:
#             print(e)
#             # Invalid parameters were supplied to Stripe's API
#             return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

#         except stripe.error.AuthenticationError as e:
#             # Authentication with Stripe's API failed
#             # (maybe you changed API keys recently)
#             return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

#         except stripe.error.APIConnectionError as e:
#             # Network communication with Stripe failed
#             return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

#         except stripe.error.StripeError as e:
#             # Display a very generic error to the user, and maybe send
#             # yourself an email
#             return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

#         except Exception as e:
#             # send an email to ourselves
#             return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

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