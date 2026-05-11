from django.test import TestCase
from django.contrib.auth import get_user_model
from students.models import Student
from attendance.models import Attendance
from django.utils import timezone
from datetime import date

User = get_user_model()

class StudentModelTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="John Doe",
            student_id="12345",
            email="john@example.com",
            roll_number="001",
            branch="Computer Science"
        )

    def test_student_creation(self):
        self.assertEqual(self.student.name, "John Doe")
        self.assertEqual(self.student.student_id, "12345")
        self.assertEqual(str(self.student), "John Doe (12345)")

class AttendanceModelTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Jane Doe",
            student_id="67890",
            email="jane@example.com"
        )
        self.attendance = Attendance.objects.create(
            student=self.student,
            confidence_score=0.85
        )

    def test_attendance_creation(self):
        self.assertEqual(self.attendance.student, self.student)
        self.assertEqual(self.attendance.date, date.today())
        self.assertEqual(self.attendance.confidence_score, 0.85)
        self.assertTrue(self.attendance.status)

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            role="admin"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.role, "admin")
        self.assertTrue(self.user.check_password("testpass123"))

class FaceRecognitionTest(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            name="Test Student",
            student_id="TEST001",
            email="test@example.com",
            embedding=[0.1, 0.2, 0.3]  # Mock embedding
        )

    def test_student_with_embedding(self):
        students_with_embeddings = Student.objects.filter(
            is_active=True,
            embedding__isnull=False
        )
        self.assertEqual(students_with_embeddings.count(), 1)
        self.assertEqual(students_with_embeddings.first(), self.student)