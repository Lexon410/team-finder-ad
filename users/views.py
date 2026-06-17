from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, LoginForm, ProfileEditForm
from .models import User
from utils.pagination import paginate_queryset

def register(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'users/register.html', {'form': form})
        user = form.save()
        login(request, user)
        return redirect('projects:project_list')
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            form.add_error(None, 'Неверный имейл или пароль')
            return render(request, 'users/login.html', {'form': form})
        user = form.get_user()
        login(request, user)
        return redirect('projects:project_list')
    return render(request, 'users/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('projects:project_list')

@login_required
def change_password(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'users/change_password.html', {'form': form})
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect('users:user_detail', user_id=request.user.id)
    return render(request, 'users/change_password.html', {'form': form})

def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'users/user-details.html', {'user': user})

@login_required
def edit_profile(request):
    form = ProfileEditForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST':
        if not form.is_valid():
            return render(request, 'users/edit_profile.html', {'form': form})
        form.save()
        return redirect('users:user_detail', user_id=request.user.id)
    return render(request, 'users/edit_profile.html', {'form': form})

def participants_list(request):
    users = User.objects.all()
    page_obj = paginate_queryset(request, users)
    return render(request, 'users/participants.html', {'participants': page_obj})