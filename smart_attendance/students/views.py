from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentForm
from accounts.models import User
from services.face_service import generate_embedding
import base64
from django.core.files.base import ContentFile



@login_required
def add_student(request):
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES)
        
        # Handle captured image from live scan
        captured_image = request.POST.get('captured_image')
        if captured_image:
            try:
                format, imgstr = captured_image.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f"{request.POST.get('student_id', 'temp')}_scan.{ext}")
                request.FILES['image'] = data
                # Re-initialize form with the injected image
                form = StudentForm(request.POST, request.FILES)
            except Exception as e:
                messages.error(request, f"Error processing live scan: {str(e)}")

        if form.is_valid():
            student = form.save()
            
            # --- Automatic User Account Creation ---
            username = student.student_id or student.roll_number
            if username:
                try:
                    # check if user already exists
                    if not User.objects.filter(username=username).exists():
                        password = f"{username}@SAS"
                        user = User.objects.create_user(
                            username=username,
                            email=student.email,
                            password=password,
                            role='student',
                            first_name=student.name.split()[0] if student.name else "",
                        )
                        student.user = user
                        student.save()
                        messages.info(request, f'Login Account created: User: {username} | Pass: {password}')
                    else:
                        messages.warning(request, f'User account with username {username} already exists.')
                except Exception as ue:
                    messages.error(request, f"Student profile saved, but failed to create user account: {str(ue)}")
            # ----------------------------------------

            try:
                embedding = generate_embedding(student.image.path)
                student.embedding = embedding
                student.save()
                messages.success(request, f'Student {student.name} registered successfully!')
                return redirect("dashboard")
            except Exception as e:
                # Note: We don't delete student here anymore because account might be partially created
                messages.error(request, f'Failed to process image: {str(e)}')
                return redirect("students:student_list")

        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudentForm()

    return render(request, "add_student.html", {'form': form})

@login_required
def student_list(request):
    students = Student.objects.all().order_by('-created_at')
    return render(request, "student_list.html", {'students': students})

@login_required
def edit_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        form = StudentForm(request.POST, request.FILES, instance=student)
        
        # Handle captured image from live scan in edit mode
        captured_image = request.POST.get('captured_image')
        if captured_image:
            try:
                format, imgstr = captured_image.split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f"{student.student_id}_update.{ext}")
                request.FILES['image'] = data
                # Re-initialize form with the injected image
                form = StudentForm(request.POST, request.FILES, instance=student)
            except Exception as e:
                messages.error(request, f"Error processing live scan update: {str(e)}")

        if form.is_valid():
            student = form.save()
            if 'image' in request.FILES:
                try:
                    embedding = generate_embedding(student.image.path)
                    student.embedding = embedding
                    student.save()
                    messages.success(request, f'Student {student.name} updated with new biometric data.')
                except Exception as e:
                    messages.error(request, f'Failed to process new image: {str(e)}')
            else:
                messages.success(request, f'Student {student.name} updated successfully.')
            return redirect("students:student_list")

    else:
        form = StudentForm(instance=student)
    
    return render(request, "add_student.html", {'form': form, 'edit_mode': True})

@login_required
def delete_student(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == "POST":
        name = student.name
        student.delete()
        messages.success(request, f'Student {name} deleted successfully.')
        return redirect("students:student_list")
    
    return redirect("students:edit_student", pk=pk)