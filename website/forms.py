from django import forms
from django.forms.widgets import TextInput, PasswordInput
from django.contrib.auth.models import User
from django.db.models import Q


class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                        'type': 'text', 'id': 'f-name',
                                                                        'placeholder': 'Enter first name'}))
    last_name = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                       'type': 'text', 'id': 'l_name',
                                                                       'placeholder': 'Enter last name'}))
    username = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                   'type': 'text', 'id': 'username',
                                                                   'placeholder': 'Enter username'}))
    phone = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                    'type': 'text', 'id': 'phone',
                                                                    'placeholder': 'Enter phone'}))
    email = forms.EmailField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                    'type': 'text', 'id': 'email',
                                                                    'placeholder': 'Enter email'}))
    home_address = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                    'type': 'text', 'id': 'address',
                                                                    'placeholder': 'Enter home address'}))
    password = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                      'type': 'password', 'id': 'password',
                                                                      'placeholder': 'Enter password'}))

    def clean(self):
        clean_data = self.cleaned_data
        # check if email or username already exists
        user = User.objects.filter(Q(username = clean_data['username'])|Q(email= clean_data['email']))
        if len(user) != 0:
            raise forms.ValidationError('Username or email already exists. Please try another one')

        return clean_data


class LoginForm(forms.Form):
    username = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                      'type': 'text', 'id': 'username',
                                                                      'placeholder': 'Enter Username'}))
    password = forms.CharField(required=True, widget=TextInput(attrs={'class': 'form-control',
                                                                      'type': 'password', 'id': 'password',
                                                                      'placeholder': 'Enter Password'}))


class PlainForm(forms.Form):
    pass


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Full Name'}))
    email = forms.EmailField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    message = forms.CharField(max_length=200, widget=forms.Textarea(attrs={'placeholder': 'Type your message here..'}))