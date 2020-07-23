from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import render, reverse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from helpers.services import get_categories, get_product, get_brands, ContentMixin
from ecommerce.models import ShippingInfo, ShippingLocation, Product
from .forms import UserRegistrationForm, LoginForm, PlainForm, ContactForm
#


class HomepageView(ContentMixin, generic.TemplateView):
    template_name = 'website/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['categories'] = get_categories(self.request, 10)
        context['products'] = get_product(self.request, 10)
        context['brands'] = get_brands(self.request, 10)
        return context


class RegistrationView(generic.FormView):
    template_name = 'website/account.html'
    form_class = UserRegistrationForm

    def get_success_url(self):
        return reverse('login')

    def form_valid(self, form):
        # if any of the operation fails, it should revert everything that have been saved.
        with transaction.atomic():
            user = User(username=form.cleaned_data['username'], email=form.cleaned_data['email'],
                        first_name=form.cleaned_data['first_name'], last_name=form.cleaned_data['last_name'])
            user.set_password(form.cleaned_data['password'])
            user.save()
            shipping = ShippingInfo(user=user, address=form.cleaned_data['home_address'],
                                    first_name=form.cleaned_data['first_name'],
                                    last_name=form.cleaned_data['last_name'],
                                    phone_number=form.cleaned_data['phone'],
                                    email_address=form.cleaned_data['email'],
                                    primary=True)
            shipping.save()
        messages.success(self.request, "Account created successfully")
        return super().form_valid(form)


class LoginView(generic.FormView):
    template_name = 'website/login.html'
    form_class = LoginForm

    def get_success_url(self):
        return reverse('profile')

    def form_valid(self, form):
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(self.request, user)
            messages.success(self.request, "login successful")
        else:
            messages.error(self.request, "No account found. Please check login credentials and try again")
            return super().form_invalid(form)

        return super().form_valid(form)


class ContactView(ContentMixin, generic.FormView):
    template_name = 'website/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['categories'] = get_categories(self.request, 10)
        return context

    def form_valid(self, form):
        contact_mail(form.cleaned_data)
        messages.success(self.request, "Message sent successfully.")
        return super().form_valid(form)


def contact_mail(obj):
    message = render_to_string('emails/contact-email.html', {
        'context': obj
    })
    mail_subject = 'Customer Feedback'
    to_email = 'admin@gmail.com'
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.content_subtype = 'html'
    email.send()