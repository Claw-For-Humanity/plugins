from datetime import datetime
import cv2
import random
import string


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

def fingerprint():
        '''return random string composed of 8 characters randomly selected from a-z, 0-9'''
        characters = string.ascii_lowercase + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(8))
        return random_string


def sam_to_coordinates(fastSam, is_fastSam_xywh=False):
        '''converts fastSam output dictionary into list and returns lists of x,y,w,h'''
        output_list = []

        for i in range(len(fastSam)):
            output_list.append(fastSam[i]['plot'])

        if is_fastSam_xywh:
            for (x, y, w, h) in output_list:
                x2 = x + w
                y2 = y + h
                output_list.append((x, y, x2, y2))
            pass

        print(f'\n\n{len(output_list)} boxes found')
        print(f'output list is {output_list}\n\n')

        return output_list
    
def find_largest_area(rectangles):
    if not rectangles:
        return None  
    
    largest_rectangle = max(rectangles, key=lambda r: r[2] * r[3])
    
    return largest_rectangle