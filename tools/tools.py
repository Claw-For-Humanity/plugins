from datetime import datetime
import cv2


def search_cam(max_ports=10):
    '''only use this as a debugging/
        running this everytime is not recommended.'''
    print('[LOG]: searching cam ports')
    available_ports = []
    for port in range(max_ports):
        camera = cv2.VideoCapture(port)
        if camera.isOpened():
            available_ports.append(port)
            camera.release()
    return available_ports

def current_time():
    '''returns current yyyymmddhhmmss in string'''
    now = datetime.now()
    year_month_time = now.strftime("%Y%m%d%H%M%S")
    
    return str(year_month_time)
