from datetime import date
from django.db import models
from accounts.models import User
from django_countries.fields import CountryField
from django.urls import reverse
from  django.conf import settings
from django.db.models.signals import post_save

# Create your models here.

SEX = (
    ('G', 'Select gender'),
    ('M', 'Male'),
    ('F', 'Female'),
)

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    paypal_customer_id = models.CharField(max_length=100, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.fist_name

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


class OrderProduct(models.Model):
    """Creates a database instance OrderItem in database."""
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
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
        return self.get_total_item_price()

class Order(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(OrderProduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    checkout_address = models.ForeignKey(
        'CheckoutAddress', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date',)

    def __str__(self):
        return self.owner.first_name
    
    def get_total_price(self):
        total = 0
        for order_item in self.products.all():
            total += order_item.get_final_price()
        return total


class CheckoutAddress(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    apartment_address = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    state = models.CharField(max_length=50)
    country = CountryField(multiple=False, blank_label='(select country)')
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.owner.first_name

class Payment(models.Model):
    paypal_id = models.CharField(max_length=100)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, 
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def __str__(self):
        return self.owner.first_name
    
class MembershipForm(models.Model):
    country = CountryField(multiple=False, blank_label='(select country)')
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(choices=SEX,default="G", max_length=1)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=50, blank=True, default='')
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