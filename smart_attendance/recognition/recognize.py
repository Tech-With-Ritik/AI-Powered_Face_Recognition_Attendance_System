import cv2
import numpy as np
# from deepface import DeepFace  # Moved inside function
from students.models import Student
from attendance.models import Attendance
from django.utils import timezone
from datetime import date, timedelta

from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def process_single_frame(frame, confidence_threshold=0.38):

    """
    Process a single frame from the web API.
    Returns matching student or None.
    """
    students = Student.objects.filter(is_active=True, embedding__isnull=False)
    if not students:
        return None

    embeddings = [student.embedding for student in students]
    
    try:
        from deepface import DeepFace
        # Using a more robust detector backend
        detected = DeepFace.represent(
            frame,
            model_name="ArcFace",
            enforce_detection=True,
            detector_backend="opencv"
        )

        if detected and len(detected) > 0:
            face_embedding = detected[0]["embedding"]
            
            if not face_embedding:
                logger.debug("No embedding generated for detected face")
                return None

            # Cosine Similarity
            distances = []
            for e in embeddings:
                u = np.array(face_embedding)
                v = np.array(e)
                # Ensure no division by zero
                norm_u = np.linalg.norm(u)
                norm_v = np.linalg.norm(v)
                if norm_u == 0 or norm_v == 0:
                    distances.append(1.0) # max distance
                else:
                    cos_sim = np.dot(u, v) / (norm_u * norm_v)
                    distances.append(1 - cos_sim) # cosine distance

            min_distance = min(distances)
            index = int(np.argmin(distances))
            
            # For cosine, distance is 1 - cos_sim, so cos_sim = 1 - min_distance
            # Higher is better, 1.0 is a perfect match
            confidence = float(1 - min_distance)


            if confidence >= confidence_threshold:
                matched_student = students[index]
                
                # Check for duplicate within last hour using localized time
                now = timezone.localtime(timezone.now())
                one_hour_ago = now - timedelta(hours=1)
                today = now.date()

                recent_attendance = Attendance.objects.filter(
                    student=matched_student,
                    date=today,
                    created_at__gte=one_hour_ago
                ).exists()

                if not recent_attendance:
                    attendance = mark_attendance(matched_student, confidence)
                    return {
                        'status': 'success',
                        'student_name': matched_student.name,
                        'student_id': matched_student.student_id,
                        'confidence': round(confidence, 2),
                        'time': now.strftime("%H:%M:%S")
                    }
                else:
                    return {
                        'status': 'duplicate',
                        'student_name': matched_student.name,
                        'message': 'Attendance already marked recently'
                    }

            else:
                logger.debug(f"Face detected but confidence {confidence:.2f} < {confidence_threshold}")
                return {
                    'status': 'no_match',
                    'message': f'Recognition score too low ({confidence:.2f})'
                }

        
    except ValueError as ve:
        # This usually means no face was detected in the frame
        logger.debug(f"Face detection info: {ve}")
        return {
            'status': 'no_face',
            'message': 'No face clearly visible'
        }
    except Exception as e:
        logger.error(f"Process frame unexpected error: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
    
    return None

def recognize_faces(max_frames=50, confidence_threshold=0.45):

    """
    Legacy local recognition (kept for reference or desktop usage).
    """
    # ... existing implementation ...
    # (Leaving it for now but the web API will use process_single_frame)
    pass

def mark_attendance(student, confidence_score=None):
    """
    Mark attendance for a student with optional confidence score.
    """
    today = timezone.localtime(timezone.now()).date()
    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=today,
        defaults={'confidence_score': confidence_score}
    )


    if not created and confidence_score:
        # Update confidence if higher
        if not attendance.confidence_score or confidence_score > attendance.confidence_score:
            attendance.confidence_score = confidence_score
            attendance.save()

    return attendance

def send_attendance_notification(student, attendance, confidence):
    """
    Send email notification for attendance marking.
    """
    if not student.email:
        return

    subject = f'Attendance Marked - {student.name}'
    message = f"""
    Dear {student.name},

    Your attendance has been successfully marked for {attendance.date}.

    Details:
    - Date: {attendance.date}
    - Time: {attendance.time}
    - Confidence Score: {confidence:.2f}
    - Status: Present

    Thank you for using Smart Attendance System.

    Best regards,
    Smart Attendance System
    """

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=True,
        )
        logger.info(f"Attendance notification sent to {student.email}")
    except Exception as e:
        logger.error(f"Failed to send email to {student.email}: {e}")