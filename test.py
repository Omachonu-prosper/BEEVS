from deepface import DeepFace
import cv2

def face_exists(image_path):
    try:
        # DeepFace handles face detection with retinaface by default
        detections = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend="retinaface",   # best accuracy
            enforce_detection=False           # prevent errors
        )

        return len(detections) > 0

    except Exception as e:
        print("Error:", e)
        return False


# ----- Usage example -----
image_path = "/home/bknd-bobby/BEEVS/server/beevs/static/images/1a15d9b64e95418ab460417c48f1aab3.jpg"
# image_path = "http://localhost:5000/static/images/576748ff1abf4ef8b0e3eb3694127e65.jpeg"


if face_exists(image_path):
    print("Face detected ✔")
else:
    print("No face detected ❌")
