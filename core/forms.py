from django import forms
from .models import Product
from django.contrib.auth.models import User
from .models import ContactMessage, Feedback


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image']


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['message']  # Only allow users to submit the message content

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']

        