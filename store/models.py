from datetime import date
from django.db import models
from django.db.models.base import Model
from django_countries.fields import CountryField
from django.urls import reverse
from  django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

SEX = (
    ('G', 'Select gender'),
    ('M', 'Male'),
    ('F', 'Female'),
)

class UserProfile(models.Model):
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return str(self.stripe_customer_id)

class Category(models.Model):
    """Creates a database instance of Category in database."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

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


class Cart(models.Model):
    """Creates a database instance OrderItem in database."""
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"
        
    def get_total_product_price(self):
        return self.quantity * self.product.price

    def get_final_price(self):
        return self.get_total_product_price()

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50, blank=True, default='')
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    products = models.ManyToManyField(Cart)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    shipping_address = models.CharField(max_length=100)
    country = CountryField(multiple=False, blank_label='(select country)')
    zip = models.CharField(max_length=100)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return str(self.first_name)
    
    def get_total_price(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        return total

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return str(self.stripe_customer_id)
    
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