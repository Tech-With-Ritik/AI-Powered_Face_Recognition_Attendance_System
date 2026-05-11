from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from students.models import Student

class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'department')

class StudentSignupForm(CustomUserCreationForm):
    student_id = forms.CharField(max_length=20, required=True, label="Student ID / Roll Number")
    branch = forms.CharField(max_length=100, required=True)
    
    class Meta(CustomUserCreationForm.Meta):
        fields = CustomUserCreationForm.Meta.fields + ('student_id', 'branch')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}".strip() or user.username,
                student_id=self.cleaned_data.get('student_id'),
                branch=self.cleaned_data.get('branch'),
                email=user.email,
                phone=user.phone
            )
        return user

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'department']
