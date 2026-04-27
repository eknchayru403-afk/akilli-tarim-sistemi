"""
Accounts forms — Kullanıcı kayıt ve giriş formları.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Kullanıcı kayıt formu."""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'E-posta adresiniz'}),
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'city', 'phone', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Kullanıcı adı'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Ad'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Soyad'}),
            'city': forms.TextInput(attrs={'placeholder': 'Şehir'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Telefon (opsiyonel)'}),
        }


class CustomLoginForm(AuthenticationForm):
    """Kullanıcı giriş formu."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Kullanıcı adı'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Şifre'}),
    )


class UserProfileForm(forms.ModelForm):
    """Kullanıcı profil güncelleme formu."""

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'city', 'phone')
