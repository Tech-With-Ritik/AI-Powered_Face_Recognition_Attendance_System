from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from students.models import Student
from students.serializers import StudentSerializer
from attendance.models import Attendance
from attendance.serializers import AttendanceSerializer
from accounts.models import User
from accounts.serializers import UserSerializer, UserCreateSerializer

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active students"""
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's attendance"""
        today = timezone.now().date()
        queryset = self.get_queryset().filter(date=today)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get attendance statistics"""
        total_students = Student.objects.filter(is_active=True).count()
        today_attendance = Attendance.objects.filter(
            date=timezone.now().date()
        ).count()
        weekly_attendance = Attendance.objects.filter(
            date__gte=timezone.now().date() - timedelta(days=7)
        ).count()

        data = {
            'total_students': total_students,
            'today_attendance': today_attendance,
            'weekly_attendance': weekly_attendance,
            'attendance_rate': (today_attendance / total_students * 100) if total_students > 0 else 0
        }
        return Response(data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Get current user profile"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)