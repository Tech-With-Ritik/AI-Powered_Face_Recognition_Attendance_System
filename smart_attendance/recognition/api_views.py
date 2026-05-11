import base64
import cv2
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .recognize import process_single_frame

class ProcessFrameView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Restrict access to non-student roles
        if request.user.role == 'student':
            return Response({'error': 'Students are not authorized to mark attendance.'}, status=status.HTTP_403_FORBIDDEN)
            
        try:

            image_data = request.data.get('image')
            if not image_data:
                return Response({'error': 'No image data provided'}, status=status.HTTP_400_BAD_REQUEST)

            # Convert base64 to image
            try:
                format, imgstr = image_data.split(';base64,')
                decoded_data = base64.b64decode(imgstr)
                nparr = np.frombuffer(decoded_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception as b64_err:
                return Response({'error': f'Failed to decode image: {str(b64_err)}'}, status=status.HTTP_400_BAD_REQUEST)

            if frame is None:
                return Response({'error': 'Invalid image data (opencv could not decode)'}, status=status.HTTP_400_BAD_REQUEST)

            # Process frame
            try:
                result = process_single_frame(frame)
            except Exception as proc_err:
                return Response({'error': f'Processing error: {str(proc_err)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            if result:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'no_match', 'message': 'No known face detected or no match found'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': f'Server error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
