from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile
from .models import Feedback
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'feedback', 'rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
        }

class SignUpForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'First name should only contain letters and spaces')]
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        validators=[RegexValidator(r'^[a-zA-Z\s]+$', 'Last name should only contain letters and spaces')]
    )
    username = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=True)
    phone_number = forms.CharField(max_length=11, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match")
        return password2

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        
        # Ensure the phone number is in the format for Pakistan, starting with 03 and containing 11 digits
        if not re.match(r'^03\d{9}$', phone_number):
            raise ValidationError("Please enter a valid Pakistani phone number (11 digits, starting with 03).")
        
        return phone_number

    def save(self, commit=True):
        user = super(SignUpForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['phone_number'],
                address=self.cleaned_data['address']
            )
        return user


class LoginForm(AuthenticationForm):
    pass

class MasalaOrderForm(forms.Form):
    flavor = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=forms.HiddenInput()
    )
    quantity = forms.ChoiceField(
        choices=[('250g', '250g'), ('500g', '500g'), ('1Kg', '1Kg')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    phone_number = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    delivery_address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Delivery Address'}))

class OrderForm(forms.Form):
    flavor = forms.CharField(widget=forms.HiddenInput())
    quantity = forms.ChoiceField(choices=[('250g', '250g'), ('500g', '500g'), ('1Kg', '1Kg')], widget=forms.Select(attrs={'class': 'form-control'}))

class CheckoutForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    delivery_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=True
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the user from kwargs
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            # Add the readonly attribute to the fields for authenticated users
            self.fields['name'].widget.attrs['readonly'] = 'readonly'
            self.fields['email'].widget.attrs['readonly'] = 'readonly'
            # Add a class to the read-only fields
            self.fields['name'].widget.attrs['class'] += ' readonly-field'
            self.fields['email'].widget.attrs['class'] += ' readonly-field'
            # Optionally, you can also style the phone_number and delivery_address fields differently
            # if you need to apply specific styling to editable fields.
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^03\d{9}$', phone_number):
            raise ValidationError("Please enter a valid Pakistani phone number (11 digits, starting with 03).")
        return phone_number

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name.replace(" ", "").isalpha():
            raise ValidationError("Name should contain only alphabetic characters.")
        return name
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", widget=forms.EmailInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Enter your registered email'
    }))

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("We couldn't find a user with that email address.")
        return email

class PasswordResetVerificationForm(forms.Form):
    code = forms.CharField(
        max_length=6,
        label="Enter the code sent to your email",
        widget=forms.TextInput(attrs={
            'class': 'form-control',  # Add Bootstrap form-control class
            'placeholder': 'Verification Code'  # Placeholder for clarity
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'New password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Confirm new password'
        })
    
