from django.core.mail import EmailMessage
from django.db import transaction
from django.http import JsonResponse
from django.contrib import messages
from django.shortcuts import render, reverse
from django.template.loader import render_to_string
from django.views import generic
from helpers.services import get_brands, get_categories
from ecommerce.models import Banks, Brand, Category, Order, Product, ShippingInfo, ShippingLocation
from website.forms import UserRegistrationForm
from .forms import *
# Create your views here.


class ContentMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brands'] = get_brands(self.request, 0)
        context['carts'] = self.request.session.get('cart', {})
        # calculations for cart
        if context['carts']:
            amount = 0
            qty = 0
            for cart_id, cart_items in context['carts'].items():
                amount += float(cart_items['amount'])
                qty += int(cart_items['qty'])

            context['cart_extra'] = {
                'total_amount': amount,
                'total_qty': qty,
                'total_items': len(context['carts'])
            }
        context['categories'] = get_categories(self.request, 0)
        return context


class CategoryView(ContentMixin, generic.ListView):
    template_name = 'ecommerce/categories.html'
    paginate_by = 15
    context_object_name = 'products'
    ordering = 'date_added'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category_name'] = Category.objects.get(id=self.kwargs['id']).name
        context['product_count'] = Product.objects.filter(category_id=self.kwargs['id']).count()
        return context

    def get_queryset(self):
        cat_id = self.kwargs['id']
        return Product.objects.filter(category_id=cat_id)


class BrandView(ContentMixin, generic.ListView):
    template_name = 'ecommerce/brand.html'
    model = Product
    paginate_by = 15
    ordering = 'date_added'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['brand_name'] = Brand.objects.get(id=self.kwargs['id']).name
        context['product_count'] = Product.objects.filter(brand_id=self.kwargs['id']).count()
        return context

    def get_queryset(self):
        brand_id = self.kwargs['id']
        return Product.objects.filter(brand_id=brand_id)


class ProductView(ContentMixin, generic.DetailView):
    template_name = 'ecommerce/product.html'
    model = Product
    context_object_name = 'product'
    pk_url_kwarg = 'id'


class SearchView(ContentMixin, generic.TemplateView):
    template_name = 'ecommerce/search.html'

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data()
        try:
            if self.request.GET.get('q'):
                query = self.request.GET.get('q')
                products = Product.objects.filter(title__contains=query)
                context['products'] = products
        except KeyError:
            pass

        return context


class CartView(ContentMixin, generic.TemplateView):
    template_name = 'ecommerce/cart.html'


class CheckoutView(ContentMixin, generic.FormView):
    template_name = 'ecommerce/checkout.html'
    form_class = ShippingForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['shipping_location'] = ShippingLocation.objects.all()
        context['shipping_address'] = ShippingInfo.objects.filter(user_id=self.request.user.id)
        return context

    def get_success_url(self):
        return reverse('checkout')

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def form_valid(self, form):
        try:
            context = self.get_context_data()
            cart_items = self.request.session.get('cart')
            email_context = {'carts': cart_items, 'user': self.request.user, 'extra': context['cart_extra'],
                             'shipping': ShippingLocation.objects.get(id=self.request.POST['shipping']),
                             'payment': self.request.POST['payment']}
            if self.request.POST['payment'] == 'bank':
                email_context['banks'] = Banks.objects.all()

            with transaction.atomic():
                shipping = ShippingInfo(address=form.cleaned_data['home_address'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'],
                                        phone_number=form.cleaned_data['phone'],
                                        email_address=form.cleaned_data['email'],
                                        primary=True)
                shipping.save()
                order = Order(cart=cart_items,
                              total=context['cart_extra']['total_amount'],
                              shipping_id=self.request.POST['shipping'],
                              user_shipping_id=shipping.id, payment_method=self.request.POST['payment'],
                              status='pending')
                order.save()

            email_context['user_shipping'] = ShippingInfo.objects.get(id=shipping.id)

            email_context['order'] = order
            self.request.session.modified = True
            del self.request.session['cart']
            self.request.session['cart'] = {}
            send_order_mail(email_context)
            order_notification_mail()
            messages.success(self.request, "Order placed successfully. Check your email to know more about your order")

        except KeyError as err:
            messages.error(self.request, "An error occurred while trying to process your order. %s is missing" % err)
            return super().form_invalid(form)

        return super().form_valid(form)


def cart_action(request):
    try:
        product = request.GET.get('product')
        qty = request.GET.get('qty')
        action = request.GET.get('action')
        request.session.modified = True
        if not request.session.get('cart'):
            request.session['cart'] = {}

        if not request.session['cart'].get(product) and (action == 'add' or action == 'update'):
            try:
                product_obj = Product.objects.get(id=product)
                request.session['cart'][product] = {'title': product_obj.name, 'qty': int(qty),
                                                 'price': str(product_obj.selling_price),
                                                 'amount': str(product_obj.selling_price * int(qty)),
                                                 'image_url': product_obj.display_picture.url }
                messages.success(request, "Product added to cart successfully")
            except Product.DoesNotExist:
                pass
        else:
            if action == 'add' and int(qty) > 0:
                request.session['cart'][product]['qty'] += int(qty)
                request.session['cart'][product]['amount'] = str(int(request.session['cart'][product]['qty']) *
                                                              float(request.session['cart'][product]['price']))
                messages.success(request, "Product added to cart successfully")

            elif action == 'update' and int(qty) > 0:
                request.session['cart'][product]['qty'] = int(qty)
                request.session['cart'][product]['amount'] = str(int(qty) * float(request.session['cart'][product]['price']))
                messages.success(request, "your cart have been updated successfully")

            elif action == 'remove' and int(request.session['cart'][product]['qty']) > 0 :
                result = request.session['cart'][product]['qty'] - int(qty)
                if result < 1:
                    request.session['cart'][product]['qty'] = 1
                else:
                    request.session['cart'][product]['qty'] -= int(qty)

                messages.success(request, "your cart have been updated successfully")

            elif action == 'delete':
                if request.session['cart'].get(product):
                    request.session['cart'].pop(product)
                    messages.success(request, "your cart have been updated successfully")

    except KeyError as err:
        print(err)
        messages.error(request, "An error occured. %s is missing " % err)
        return JsonResponse(status=400, data={'error': 'session key is missing'})

    return JsonResponse(status=200, data=request.session['cart'])


def send_order_mail(obj):

    message = render_to_string('emails/order-email.html', {
        'context': obj

    })
    mail_subject = 'Order'
    to_email = obj['user_shipping'].email_address
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()


def order_notification_mail():
    message = render_to_string('emails/order-notification.html', None)
    mail_subject = 'Order Notification'
    to_email = 'sales@lasebooks.com.ng'
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()