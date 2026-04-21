"""
Accounts views — Kayıt, giriş, çıkış ve profil view'ları.
"""

import logging

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render

from .forms import CustomLoginForm, CustomUserCreationForm, UserProfileForm

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    """Kullanıcı giriş view'ı."""

    template_name = 'accounts/login.html'
    authentication_form = CustomLoginForm
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    """Kullanıcı çıkış view'ı."""

    next_page = '/accounts/login/'


def register_view(request):
    """Kullanıcı kayıt view'ı."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
            logger.info("Yeni kullanıcı kayıt: %s", user.username)
            return redirect('dashboard:index')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """Kullanıcı profil görüntüleme ve güncelleme."""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profil bilgileriniz güncellendi.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})
