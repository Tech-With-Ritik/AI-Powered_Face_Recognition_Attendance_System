from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import StudentSignupForm, CustomUserCreationForm, TeacherProfileForm
from django.contrib import messages

def signup(request):
    if request.method == 'POST':
        role = request.POST.get('role', 'student')
        if role == 'student':
            form = StudentSignupForm(request.POST)
        else:
            form = CustomUserCreationForm(request.POST)
            
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('dashboard')
    else:
        form = StudentSignupForm()
    
    return render(request, 'registration/signup.html', {'form': form})

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = TeacherProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('profile')
    else:
        form = TeacherProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})
