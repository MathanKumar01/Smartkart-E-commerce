from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def register(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        user.save()

        return redirect('login')

    return render(request, 'register.html')
def user_login(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    return redirect('/users/login/')