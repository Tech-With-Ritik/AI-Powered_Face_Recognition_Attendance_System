from django.urls import path
from .views import mark_attendance_page
from .api_views import ProcessFrameView

app_name = 'recognition'

urlpatterns = [
    path('mark/', mark_attendance_page, name='mark_attendance'),
    path('api/process-frame/', ProcessFrameView.as_view(), name='process_frame'),
]
