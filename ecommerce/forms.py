from django import forms
from django.forms.widgets import TextInput, PasswordInput


class ShippingForm(forms.Form):
    first_name = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                        'type': 'text', 'id': 'f-name',
                                                                        'placeholder': 'Enter first name'}))
    last_name = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                       'type': 'text', 'id': 'l_name',
                                                                       'placeholder': 'Enter last name'}))
    phone = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                   'type': 'text', 'id': 'phone',
                                                                   'placeholder': 'Enter phone'}))
    email = forms.EmailField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                    'type': 'text', 'id': 'email',
                                                                    'placeholder': 'Enter email'}))
    home_address = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                          'type': 'text', 'id': 'address',
                                                                          'placeholder': 'Enter home address'}))


class PlainForm(forms.Form):
    pass
