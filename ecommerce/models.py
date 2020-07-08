from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html
from ckeditor.fields import RichTextField
import random
import string
import ast
# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    TYPE = (('old', 'Old'),
            ('new', 'New'))
    name = models.CharField(max_length=200)
    model = models.CharField(max_length=400, null=True)
    description = RichTextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    display_picture = models.ImageField(upload_to='products', blank=True)
    product_type = models.CharField(max_length=3, choices=TYPE, default=TYPE[0][0])
    qty = models.CharField(max_length=1)
    image_1 = models.ImageField(upload_to='products', blank=True)
    image_2 = models.ImageField(upload_to='products', blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ShippingInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=200, null=True)
    last_name = models.CharField(max_length=200, null=True)
    address = models.TextField(max_length=200)
    phone_number = models.CharField(max_length=14)
    email_address = models.CharField(max_length=200)
    primary = models.BooleanField(default=False)

    def __str__(self):
        return self.address


class ShippingLocation(models.Model):
    location = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.location + " " + str(self.price)


class Banks(models.Model):
    bank_name = models.CharField(max_length=200)
    acc_name = models.CharField(max_length=200)
    acc_no = models.CharField(max_length=200)

    def __str__(self):
        return "%s (%s %s)"%(self.bank_name, self.acc_name, self.acc_no)


class Order(models.Model):
    @staticmethod
    def generate_random_key(n):
        return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(n))

    PAYMENT_TYPE = (
        ('bank', 'bank'),
        ('cash', 'cash')
    )
    STATUS_TYPE = (
        ('pending', 'pending'),
        ('success', 'success'),
        ('terminated', 'terminated'),
        ('completed', 'completed')
    )
    cart = models.CharField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    token = models.CharField(max_length=10, unique=True, default=0)
    order_date = models.DateTimeField(auto_now=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.ForeignKey(ShippingLocation, on_delete=models.CASCADE)
    user_shipping = models.ForeignKey(ShippingInfo, on_delete=models.CASCADE, null=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_TYPE)
    status = models.CharField(max_length=10, choices=STATUS_TYPE)
    date = models.DateTimeField(auto_now=True)

    def display_cart(self):
        html_table = "<table cellpadding='1'><thead><tr><th>Title</th><th>Qty</th><th>Amount</th></tr></thead>"
        body = "<tbody>"
        carts = ast.literal_eval(self.cart)
        for item in carts.keys():
            table = "<tr>"
            table = table + "<td>" + carts[item]["title"] + "</td>"
            table = table + "<td>" + str(carts[item]["qty"]) + "</td>"
            table = table + "<td>" + carts[item]["amount"] + "</td>"
            table = table + "</tr>"
            body = body + table
        body = body + "</tbody></table>"
        html_table = html_table + body
        return format_html(html_table)

    def __str__(self):
        try:
            return str(self.token + " " + self.user.username)
        except:
            return str(self.token + "  non user order.")

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.token = self.generate_random_key(10)
        return super().save()


class SliderText(models.Model):
    title = models.CharField(max_length=150, unique=True)
    img = models.FileField(upload_to='slider')

    def __str__(self):
        return self.title


class DealProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    duration = models.DateTimeField()

    def __str__(self):
        return self.product.name

