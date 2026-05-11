from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def mark_attendance_page(request):
    """
    Renders the page with the webcam feed for marking attendance.
    Only allows access for Admins and Teachers.
    """
    if request.user.role == 'student':
        messages.error(request, "Access Denied: Students are not permitted to scan attendance.")
        return redirect('dashboard')
        
    return render(request, "recognition/mark_attendance.html")
