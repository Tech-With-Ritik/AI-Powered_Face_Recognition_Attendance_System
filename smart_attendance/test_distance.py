import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_attendance.settings')
django.setup()

from students.models import Student
import numpy as np

stu = Student.objects.last()
if stu:
    print(f"Student: {stu.name}")
    emb = np.array(stu.embedding)
    print(f"Embedding norm: {np.linalg.norm(emb)}")
    
    # Let's see the metrics DeepFace recommends
    from deepface.commons import distance as dst
    
    # Try calculating with itself
    l2 = dst.find_euclidean_distance(emb, emb)
    cos = dst.find_cosine_distance(emb, emb)
    
    print(f"Self L2 Distance: {l2}")
    print(f"Self Cosine Distance: {cos}")
    
    # Try with a random vector to see magnitude
    rand_emb = np.random.rand(len(emb))
    l2_rand = dst.find_euclidean_distance(emb, rand_emb)
    print(f"Random L2 Distance: {l2_rand}")
    
    # What was our formula?
    conf = 1 / (1 + l2_rand)
    print(f"Score for random: {conf: .2f}")
    
    # Let's try DeepFace represent on the user's media image if it exists
    if stu.image:
        try:
            from deepface import DeepFace
            detected = DeepFace.represent(stu.image.path, model_name="ArcFace", detector_backend="opencv")
            if detected:
                img_emb = np.array(detected[0]["embedding"])
                dist = np.linalg.norm(img_emb - emb)
                print(f"Distance between DB profile and same image represent: {dist:.2f}")
        except Exception as e:
            print(f"Error testing represent: {e}")

else:
    print("No students found.")
