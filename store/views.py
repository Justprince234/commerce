from django.db.models import query
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings

from .models import Category, Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact, UserProfile, Coupon, Cart
from store.serializers import CategorySerializer, ProductSerializer, OrderProductSerializer, OrderSerializer, CheckoutAddressSerializer, PaymentSerializer, MembershipFormSerializer, ContactSerializer, CartItemSerializer

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

# Stripe
import stripe
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
# import paypalrestsdk
# import logging


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)

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

# Add to cart
class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        item = get_object_or_404(Product, slug=slug)

        order_item_qs = OrderProduct.objects.filter(
            item=item,
            # user=request.user,
            ordered=False
        )
        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderProduct.objects.create(
                item=item,
                # user=request.user,
                ordered=False
            )
            order_item.save()

        order_qs = Order.objects.filter(ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.products.filter(item__id=order_item.id).exists():
                order.products.add(order_item)
                return Response(status=HTTP_200_OK)

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(ordered_date=ordered_date)
            order.products.add(order_item)
            return Response(status=HTTP_200_OK)

class CountryListView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(countries, status=HTTP_200_OK)

class CheckoutAddressListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CheckoutAddressSerializer

    def get_queryset(self):
        qs = CheckoutAddress.objects.all()
        return qs.filter(user=self.request.user)


class CheckoutAddressCreateView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CheckoutAddressSerializer
    queryset = CheckoutAddress.objects.all()


class CheckoutAddressUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = CheckoutAddressSerializer
    queryset = CheckoutAddress.objects.all()


class CheckoutAddressDeleteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = CheckoutAddress.objects.all()

# Order
class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.products.filter(product__slug=product.slug).exists():
                order_item = OrderProduct.objects.filter(
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
    queryset = OrderProduct.objects.all()
    

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_object(self):
        try:
            order = Order.objects.get(ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
            # return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)

#Checkout
class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(ordered=False)
        userprofile = UserProfile.objects.all()
        token = request.data.get('stripeToken')
        checkout_address_id = request.data.get('selectedCheckoutAddress')

        shipping_address = CheckoutAddress.objects.get(id=checkout_address_id)

        if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=self.request.order.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.one_click_purchasing = True
            userprofile.save()

        amount = int(order.get_final_price() * 100)

        try:

                # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                description='Charge from Direshop777 Store',
                customer=userprofile.stripe_customer_id
            )
            # charge once off on the token
            # charge = stripe.Charge.create(
            #     amount=amount,  # cents
            #     currency="usd",
            #     source=token
            # )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.amount = order.get_final_price()
            payment.save()

            # assign the payment to the order

            order_items = order.products.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.shipping_address = shipping_address
            # order.ref_code = create_ref_code()
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."}, status=HTTP_400_BAD_REQUEST)

        except Exception as e:
            # send an email to ourselves
            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)

class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)

class CartItemAPIView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        queryset = Cart.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart)
        product = Product.objects.get(pk=request.data['product_id'])
        current_item = Cart.objects.filter(cart=cart, product=product)

        if current_item.count() > 0:
            raise NotAcceptable("You already have this item in your shopping cart")

        try:
            quantity = int(request.data["quantity"])
        except Exception as e:
            raise ValidationError("Please Enter Your Quantity")

        cart_item = Cart(cart=cart, product=product, quantity=quantity)
        cart_item.save()
        serializer = CartItemSerializer(cart_item)
        total = float(product.price) * float(quantity)
        cart.total = total
        cart.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CartItemView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    queryset = Cart.objects.all()

    def retrieve(self, request, *args, **kwargs):
        cart_item = self.get_object()
        serializer = self.get_serializer(cart_item)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        cart_item = self.get_object()
        print(request.data)
        product = Product.objects.get(pk=request.data['product_id'])

        try:
            quantity = int(request.data["quantity"])
        except Exception as e:
            raise ValidationError("Please, input vaild quantity")

        serializer = CartItemSerializer(cart_item, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.delete()

        return Response(
            {"detail": _("your item has been deleted.")},
            status=status.HTTP_204_NO_CONTENT,
        )

class PaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(stripe_charge_id=self.request.stripe_charge_id)

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