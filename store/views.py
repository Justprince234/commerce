from django.db.models import query
from django.db.models import Q
from django.http.response import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone

from .models import Category, Product, OrderProduct, Order, CheckoutAddress, Payment, MembershipForm, Contact
from store.serializers import CategorySerializer, ProductSerializer, OrderProductSerializer, OrderSerializer, CheckoutAddressSerializer, PaymentSerializer, MembershipFormSerializer, ContactSerializer

from rest_framework.response import Response
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

# Remove item from cart
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

class OrdersList(APIView):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def CheckoutAddress_api_view(request):
    
    if request.method == 'GET':
        items = CheckoutAddress.objects.filter(owner=request.user,)
        serializer = CheckoutAddressSerializer(items, many=True)
        return JsonResponse(serializer.data, safe =False)
    
    elif request.method == 'POST':
        owner = request.user
        data = JSONParser().parse(request)
        serializer = CheckoutAddressSerializer(data = data)
 
        if serializer.is_valid():
            serializer.save(owner)
            return JsonResponse(serializer.data,status = 201)
        return JsonResponse(serializer.errors,status = 400)

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


class MembershipFormList(generics.ListCreateAPIView):
    queryset = MembershipForm.objects.all()
    serializer_class = MembershipFormSerializer

class ContactList(generics.ListCreateAPIView):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer