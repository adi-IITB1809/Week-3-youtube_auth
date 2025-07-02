from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from .forms import RegistrationForm

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False                # create inactive until “verified”
            user.save()
            # store for verify step
            request.session['pending_user_id'] = user.id
            messages.success(request, "Registration successful! Please verify your account.")
            return redirect('verify')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def verify_view(request):
    user_id = request.session.get('pending_user_id')
    if user_id:
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, "Account verified! You can now log in.")
        # clear session key
        del request.session['pending_user_id']
        return redirect('login')
    # if someone hits /verify/ directly
    return render(request, 'accounts/verify.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, "Please verify your account first.")
                return redirect('verify')
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')
