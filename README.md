# Smart Attendance System with Face Recognition

The Smart Attendance System is a web-based attendance management solution built with Django and advanced facial recognition technologies. It replaces traditional manual attendance tracking with an automated, secure, and accurate system that recognizes students in real time using a webcam.

## Key Features

- **Real-time Face Recognition**
  - Uses webcam capture and OpenCV for face detection.
  - Recognizes students with the ArcFace model through the DeepFace framework.
  - Marks attendance automatically with date and time.

- **Reliable Attendance Validation**
  - Prevents proxy attendance and duplicate entries.
  - Ensures each student is recorded accurately only once per session.

- **Role-Based Access Control**
  - Separate access levels for Admin, Faculty, and Students.
  - Secure login for each user type.

- **Student Management**
  - Supports student registration and profile management.
  - Allows administrators and faculty to manage student records.

- **Attendance Management**
  - Easy attendance tracking and report generation.
  - Filtering and analytics to monitor attendance trends.
  - CSV export for data sharing and record keeping.

- **Interactive Dashboard**
  - Provides analytics and visual summaries.
  - Helps institutions review attendance performance efficiently.

- **Secure and Lightweight**
  - Built on Django with SQLite for quick deployment.
  - Uses secure authentication and database storage.

## Technology Stack

- Django
- DeepFace
- ArcFace
- OpenCV
- HTML, CSS, JavaScript
- SQLite

## Benefits

- Improves attendance accuracy and reliability.
- Reduces manual effort and administrative overhead.
- Increases transparency in student attendance.
- Supports modern biometric attendance workflows.

## Getting Started

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install required packages.
4. Configure the `.env` file with your environment variables.
5. Run migrations and start the Django server.

## Notes

- Do not include the `.env` file in source control.
- Ensure the webcam is available and accessible for real-time recognition.
- Use the admin interface to manage students and attendance settings.

---

This project is designed to help educational institutions modernize attendance tracking using secure face recognition technology.