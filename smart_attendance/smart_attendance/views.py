from django.shortcuts import render, redirect
from django.contrib import messages
from students.models import Student
from attendance.models import Attendance
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
import csv

@login_required
def dashboard(request):
    user = request.user
    
    if user.role == 'student':
        # Student Dashboard Logic
        try:
            student = user.student_profile
            attendance_records = Attendance.objects.filter(student=student).order_by('-date', '-time')
            total_days = attendance_records.count()
            present_days = attendance_records.filter(status=True).count()
            attendance_rate = (present_days / total_days * 100) if total_days > 0 else 0
            
            context = {
                'student': student,
                'attendance_records': attendance_records[:10],
                'total_days': total_days,
                'present_days': present_days,
                'attendance_rate': round(attendance_rate, 2),
            }
            return render(request, "dashboard_student.html", context)
        except Student.DoesNotExist:
            messages.warning(request, "Student profile not found. Please complete your registration.")
            return redirect('profile')

    # Admin and Faculty Dashboard Logic (Shared for now, can be specialized later)
    # Get date filter from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())
    else:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()

    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()

    total_students = Student.objects.filter(is_active=True).count()
    attendance_queryset = Attendance.objects.filter(date__range=[start_date, end_date])
    total_attendance = attendance_queryset.count()

    today = timezone.localtime(timezone.now()).date()
    today_attendance = Attendance.objects.filter(date=today).count()

    attendance_rate = (today_attendance / total_students * 100) if total_students > 0 else 0

    recent_attendance = Attendance.objects.filter(
        date__range=[start_date, end_date]
    ).select_related('student').order_by('-created_at')[:10]

    trend_data = []
    for i in range(6, -1, -1):
        date_check = today - timedelta(days=i)
        count = Attendance.objects.filter(date=date_check).count()
        trend_data.append({
            'date': date_check.strftime('%Y-%m-%d'),
            'count': count
        })

    context = {
        'total_students': total_students,
        'total_attendance': total_attendance,
        'today_attendance': today_attendance,
        'absent_today': total_students - today_attendance,
        'attendance_rate': attendance_rate,
        'recent_attendance': recent_attendance,
        'trend_data': trend_data,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }

    return render(request, "dashboard.html", context)

@login_required
def export_attendance_csv(request):
    """Export attendance data as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="attendance_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Student ID', 'Student Name', 'Date', 'Time', 'Confidence Score', 'Status'])

    # Get date filter from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    queryset = Attendance.objects.select_related('student')

    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])
    elif start_date:
        queryset = queryset.filter(date__gte=start_date)
    elif end_date:
        queryset = queryset.filter(date__lte=end_date)

    for attendance in queryset:
        writer.writerow([
            attendance.student.student_id or attendance.student.roll_number,
            attendance.student.name,
            attendance.date,
            attendance.time,
            attendance.confidence_score or '',
            'Present' if attendance.status else 'Absent'
        ])

    return response