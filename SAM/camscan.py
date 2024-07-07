import cv2

class scan:

    def list_available_cameras(max_cameras=10):
        available_cameras = []
        for i in range(max_cameras):
            print(f'\nindex is {i}')
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

