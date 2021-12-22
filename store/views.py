from django.db.models import query
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from .models import Category, Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact, UserProfile
from store.serializers import CategorySerializer, ProductSerializer, OrderProductSerializer, OrderSerializer, CheckoutAddressSerializer, PaymentSerializer, MembershipFormSerializer, ContactSerializer

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
from django.http import HttpResponse,JsonResponse

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

# Add to cart
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug )
    order_item, created = OrderProduct.objects.get_or_create(
        product = product,
        user = request.user,
        ordered = False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)

    if order_qs.exists():
        order = order_qs[0]

        if order.products.filter(product__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return messages.info(request, f"{product.name} quantity has updated.")
        else:
            order.products.add(order_item)
            return messages.info(request, f"{product.name} has added to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.products.add(order_item)
        return messages.info(request, f"{product.name} has added to your cart")

# class AddToCartView(APIView):
#     def post(self, request, *args, **kwargs):
#         slug = request.data.get('slug', None)
#         if slug is None:
#             return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

#         product = get_object_or_404(Product, slug=slug)

#         order_item_qs = OrderProduct.objects.filter(
#             product=product,
#             user=request.user,
#             ordered=False
#         )

#         if order_item_qs.exists():
#             order_item = order_item_qs.first()
#             order_item.quantity += 1
#             order_item.save()
#         else:
#             order_item = OrderProduct.objects.create(
#                 product=product,
#                 user=request.user,
#                 ordered=False
#             )
#             order_item.save()

#         order_qs = Order.objects.filter(user=request.user, ordered=False)
#         if order_qs.exists():
#             order = order_qs[0]
#             if not order.products.filter(product__id=order_item.id).exists():
#                 order.products.add(order_item)
#                 return Response(status=HTTP_200_OK)

#         else:
#             ordered_date = timezone.now()
#             order = Order.objects.create(
#                 user=request.user, ordered_date=ordered_date)
#             order.products.add(order_item)
#             return Response(status=HTTP_200_OK)

# Remove from cart.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug )
    order_qs = Order.objects.filter(
        user=request.user, 
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists():
            order_item = OrderProduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            return messages.info(request, f"{product.name} has been removed from your cart")
        else:

            return messages.info(request, f"{product.name} not in your cart")
    else:
        #add message doesnt have order
        return messages.info(request, "You do not have an Order")

# Reduce item quantity in cart.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reduce_quantity_item(request, slug):
    product = get_object_or_404(Product, slug=slug )
    order_qs = Order.objects.filter(
        user = request.user, 
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(product__slug=product.slug).exists() :
            order_item = OrderProduct.objects.filter(
                product= product,
                user = request.user,
                ordered = False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order_item.delete()
            return messages.info(request, f"{product.name} quantity has updated")
        else:
            return messages.info(request, f"{product.name} not in your cart")
    else:
        #add message doesn't have order
        return messages.info(request, "You do not have an active order")

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
# class OrdersList(APIView):
#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         orders = Order.objects.filter(user=request.user)
#         serializer = OrderSerializer(orders, many=True)
#         return Response(serializer.data)

# class OrderQuantityUpdateView(APIView):
#     def post(self, request, *args, **kwargs):
#         slug = request.data.get('slug', None)
#         if slug is None:
#             return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
#         product = get_object_or_404(Product, slug=slug)
#         order_qs = Order.objects.filter(
#             user=request.user,
#             ordered=False
#         )
#         if order_qs.exists():
#             order = order_qs[0]
#             # check if the order item is in the order
#             if order.products.filter(product__slug=product.slug).exists():
#                 order_item = OrderProduct.objects.filter(
#                     product=product,
#                     user=request.user,
#                     ordered=False
#                 )[0]
#                 if order_item.quantity > 1:
#                     order_item.quantity -= 1
#                     order_item.save()
#                 else:
#                     order.products.remove(order_item)
#                 return Response(status=HTTP_200_OK)
#             else:
#                 return Response({"message": "This item was not in your cart"}, status=HTTP_400_BAD_REQUEST)
#         else:
#             return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


class OrderItemDeleteView(generics.DestroyAPIView):
    permission_classes = (IsAuthenticated, )
    queryset = OrderProduct.objects.all()
    

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
            # return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


# #Checkout
# class PaymentView(APIView):

#     def post(self, request, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         userprofile = UserProfile.objects.get(user=self.request.user)
#         token = request.data.get('stripeToken')
#         checkout_address_id = request.data.get('selectedCheckoutAddress')

#         checkout_address = CheckoutAddress.objects.get(id=checkout_address_id)

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

#                 # charge the customer because we cannot charge the token more than once
#             charge = stripe.Charge.create(
#                 amount=amount,  # cents
#                 currency="usd",
#                 customer=userprofile.stripe_customer_id
#             )
#             # charge once off on the token
#             # charge = stripe.Charge.create(
#             #     amount=amount,  # cents
#             #     currency="usd",
#             #     source=token
#             # )

#             # create the payment
#             payment = Payment()
#             payment.stripe_charge_id = charge['id']
#             payment.user = self.request.user
#             payment.amount = order.get_total()
#             payment.save()

#             # assign the payment to the order

#             order_items = order.products.all()
#             order_items.update(ordered=True)
#             for item in order_items:
#                 item.save()

#             order.ordered = True
#             order.payment = payment
#             order.checkout_address = checkout_address
#             # order.ref_code = create_ref_code()
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

#         return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)

# @api_view(['GET','POST'])
# @permission_classes([IsAuthenticated])
# def CheckoutAddress_api_view(request):
    
#     if request.method == 'GET':
#         items = CheckoutAddress.objects.filter(owner=request.user,)
#         serializer = CheckoutAddressSerializer(items, many=True)
#         return JsonResponse(serializer.data, safe =False)
    
#     elif request.method == 'POST':
#         owner = request.user
#         data = JSONParser().parse(request)
#         serializer = CheckoutAddressSerializer(data = data)
 
#         if serializer.is_valid():
#             serializer.save(owner)
#             return JsonResponse(serializer.data,status = 201)
#         return JsonResponse(serializer.errors,status = 400)

# @api_view(['POST'])
# @authentication_classes([authentication.TokenAuthentication])
# @permission_classes([permissions.IsAuthenticated])
# def checkout(request):
#     serializer = OrderSerializer(data=request.data)

#     if serializer.is_valid():

#         paid_amount = sum(item.get('quantity') * item.get('product').price for item in serializer.validated_data['productss'])
#         payment = paypalrestsdk.Payment({

#             "intent": "sale",
#             "payer": {
#                 "payment_method": "paypal"},
#             "redirect_urls": {
#                 "return_url": "http://localhost:3000/payment/execute",
#                 "cancel_url": "http://localhost:3000/"},
#             "transactions": [{
#                 "item_list": {
#                     "items": [{
#                         "name": serializer.validated_data['products'],
#                         "sku": serializer.validated_data['product'],
#                         "price": serializer.validated_data['price'],
#                         "currency": "USD",
#                         "quantity": serializer.validated_data['quantity']}]},
#                 "amount": {
#                     "total": paid_amount,
#                     "currency": "USD"},
#                 "description": "This is the payment transaction description."}]})

#         if payment.create():
#             print("Payment created successfully")
#         else:
#             print(payment.error)

#         try:
#             charge = stripe.Charge.create(
#                 amount=int(paid_amount * 100),
#                 currency='USD',
#                 description='Charge from Djackets',
#                 source=serializer.validated_data['stripe_token']
#             )

#             serializer.save(user=request.user, paid_amount=paid_amount)

#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Exception:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class PaymentView(APIView):

#     def post(self, request, *args, **kwargs):
#         order = Order.objects.get(user=self.request.user, ordered=False)
#         userprofile = UserProfile.objects.get(user=self.request.user)
#         token = request.data.get('stripeToken')
#         billing_address_id = request.data.get('selectedBillingAddress')
#         shipping_address_id = request.data.get('selectedShippingAddress')

#         billing_address = Address.objects.get(id=billing_address_id)
#         shipping_address = Address.objects.get(id=shipping_address_id)

#         pass


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def checkout_api_view(request):

#     if request.method == 'GET':
#         items = Order.objects.filter(owner=request.user, ordered=False)
#         serializer = OrderSerializer(items, many=True)
#         return JsonResponse(serializer.data, safe =False)
    
#     elif request.method == 'POST':
#         items = Order.objects.filter(owner=request.user, ordered=False)
#         serializer = OrderSerializer(items, many=True)
#         owner = request.user
#         checkout_address = CheckoutAddress(
#             user=request.user,
#             street_address=serializer.validated_data['street_address'],
#             apartment_address=serializer.validated_data['apartment_address'],
#             country=serializer.validated_data['country'],
#             zip=serializer.validated_data['zip']
#         )
#         checkout_address.save()
#         items.checkout_address = checkout_address
#         items.save()
#         data = JSONParser().parse(request)
#         serializer =OrderSerializer(data = data)
 
#         if serializer.is_valid():
#             serializer.save(owner)
#             return JsonResponse(serializer.data,status = 201)
#         return JsonResponse(serializer.errors,status = 400)

class PaymentListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

class MembershipFormList(generics.ListCreateAPIView):
    queryset = MembershipForm.objects.all()
    serializer_class = MembershipFormSerializer

class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer