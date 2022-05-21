from datetime import date
from django.db import models
from django.db.models.base import Model
from django_countries.fields import CountryField
from django.urls import reverse
from  django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from mptt.models import MPTTModel
from mptt.fields import TreeForeignKey
from config.settings import BRAINTREE_CONF

import braintree
from braintree.exceptions.authentication_error import AuthenticationError

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

gateway = braintree.BraintreeGateway(BRAINTREE_CONF)

# Create your models here.
try:
    gateway

    braintree_authentication = True
except AuthenticationError as error:
    braintree_authentication = False

class UserProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    braintree_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return str(self.user)

class Category(MPTTModel):
    """Creates a database instance of Category in database."""
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    class MPTTMeta:
        order_insertion_by=['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f"/{self.slug}/"

class Product(models.Model):
    """Creates a database instance Item in database."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    photo_main = models.ImageField(upload_to='photos/%Y/%m/%d/')
    photo_1 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_2 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_3 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    photo_4 = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE)
    description = models.TextField()
    price = models.FloatField()
    membership_price = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/{self.category.slug}/{self.slug}/'

class ProductReview(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='reviews', on_delete=models.CASCADE)

    content = models.TextField(blank=True, null=True)
    stars = models.IntegerField()

    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

class Subscriber(models.Model):
    email = models.EmailField(max_length=255)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '%s' % self.email


class Cart(models.Model):
    """Creates a database instance of Cart in database."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user', '-date']

    def __str__(self):
        return f'{self.user}'
        
    def get_total_product_price(self):
        return self.quantity * self.product.price

    def get_final_price(self):
        return self.get_total_product_price()

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Cart)
    paid = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True, null=True)
    shipping_address = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(multiple=False, blank_label='(select country)', default="US")
    zip = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return str(self.user)
    
    def get_total_price(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total
SEX = (
    ('G', 'Select gender'),
    ('M', 'Male'),
    ('F', 'Female'),
)

class MembershipForm(models.Model):
    country = CountryField(multiple=False, blank_label='(select country)')
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(choices=SEX,default="G", max_length=1)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    def __str__(self):
        return self.first_name

class Contact(models.Model):

    name = models.CharField(max_length=200)
    email = models.EmailField()
    query = models.TextField()

    class Meta:
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.name

def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)