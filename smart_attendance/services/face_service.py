# from deepface import DeepFace  # Moved inside function


def generate_embedding(image_path):
    from deepface import DeepFace
    embedding = DeepFace.represent(
        img_path=image_path,
        model_name="ArcFace",
        detector_backend="opencv"
    )


    return embedding[0]["embedding"]