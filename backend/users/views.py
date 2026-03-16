from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.db.models import Sum
import re

from orders.models import Order

@login_required
def dashboard(request):
    user_orders = Order.objects.filter(user=request.user)
    order_count = user_orders.count()
    total_spent = user_orders.aggregate(total=Sum('total_price'))['total'] or 0

    return render(request, 'dashboard.html', {
        'order_count': order_count,
        'total_spent': round(total_spent, 2),
    })

def register(request):

    context = {
        'username_value': '',
        'email_value': '',
    }

    if request.method == "POST":

        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        context['username_value'] = username
        context['email_value'] = email

        if not username or not email or not password:
            context['error'] = 'Please fill username, email, and password.'
            return render(request, 'register.html', context)

        try:
            validate_email(email)
        except ValidationError:
            context['error'] = 'Please enter a valid email address.'
            return render(request, 'register.html', context)

        if User.objects.filter(username__iexact=username).exists():
            context['error'] = 'Username already exists. Try another username.'
            return render(request, 'register.html', context)

        if User.objects.filter(email__iexact=email).exists():
            context['error'] = 'This email is already registered.'
            return render(request, 'register.html', context)

        if len(password) < 8:
            context['error'] = 'Password must be at least 8 characters.'
            return render(request, 'register.html', context)

        if not re.search(r'[A-Z]', password):
            context['error'] = 'Password must include at least one uppercase letter.'
            return render(request, 'register.html', context)

        if not re.search(r'\d', password):
            context['error'] = 'Password must include at least one number.'
            return render(request, 'register.html', context)

        if not re.search(r'[^A-Za-z0-9]', password):
            context['error'] = 'Password must include at least one special character.'
            return render(request, 'register.html', context)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        return redirect('login')

    return render(request, 'register.html', context)


def user_login(request):

    context = {
        'username_value': '',
    }

    wants_json = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        context['username_value'] = username

        if not username or not password:
            if wants_json:
                return JsonResponse({'ok': False, 'error': 'Please enter username and password.'}, status=400)
            context['error'] = 'Please enter username and password.'
            return render(request, 'login.html', context)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if wants_json:
                return JsonResponse({'ok': True, 'redirect_url': '/users/dashboard/'})
            return redirect('dashboard')

        if wants_json:
            return JsonResponse({'ok': False, 'error': 'Username or password is wrong.'}, status=401)
        context['error'] = 'Username or password is wrong.'
        return render(request, 'login.html', context)

    return render(request, 'login.html', context)

def user_logout(request):
    logout(request)
    return redirect('/users/login/')