from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'student_id', 'email', 'phone', 'roll_number', 'branch', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        # Handle embedding generation during creation
        from services.face_service import generate_embedding
        student = super().create(validated_data)
        if student.image:
            try:
                embedding = generate_embedding(student.image.path)
                student.embedding = embedding
                student.save()
            except Exception as e:
                # If embedding fails, delete the student and raise error
                student.delete()
                raise serializers.ValidationError(f"Failed to process image: {str(e)}")
        return student