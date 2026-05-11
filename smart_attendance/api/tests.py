from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from students.models import Student
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os
from PIL import Image
import io
from unittest.mock import patch

User = get_user_model()

class StudentAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role="admin"
        )
        self.client.force_authenticate(user=self.user)

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    @patch('services.face_service.generate_embedding')
    def test_create_student(self, mock_generate_embedding):
        # Mock the embedding generation to return a dummy embedding
        mock_generate_embedding.return_value = [0.1] * 512
        
        url = reverse('student-list')
        # Create a valid image using PIL
        img = Image.new('RGB', (10, 10), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=img_buffer.getvalue(),
            content_type='image/jpeg'
        )
        data = {
            'name': 'API Test Student',
            'student_id': 'API001',
            'email': 'api@example.com',
            'roll_number': '001',
            'branch': 'CS',
            'image': image
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Student.objects.count(), 1)
        self.assertEqual(Student.objects.get().name, 'API Test Student')

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp())
    def test_get_students(self):
        # Create a valid image using PIL
        img = Image.new('RGB', (10, 10), color='blue')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='JPEG')
        img_buffer.seek(0)
        
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=img_buffer.getvalue(),
            content_type='image/jpeg'
        )
        Student.objects.create(
            name='Existing Student',
            student_id='EXIST001',
            email='exist@example.com',
            image=image
        )
        url = reverse('student-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

class AttendanceAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            role="teacher"
        )
        self.client.force_authenticate(user=self.user)

    def test_get_attendance_statistics(self):
        url = reverse('attendance-statistics')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_students', response.data)
        self.assertIn('today_attendance', response.data)