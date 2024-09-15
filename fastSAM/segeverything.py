# before starting, make sure to edit prompt.py

from fastsam import FastSAM, FastSAMPrompt
import torch 
import cv2
import sys
import time
import os

sys.path.append('/Users/changbeankang/Claw_For_Humanity/HOS_II/plugins/tools')
import tools

class bucket:
    model = None
    DEVICE = None
    current_objects = []
    iou, confidence = None, None


class initialize:
    def init(type,confidence=0.4, iou = 0.9):
        bucket.model = FastSAM(f'./weights/FastSAM-{type}.pt')

        bucket.DEVICE = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )
        bucket.iou = iou
        bucket.confidence = confidence


class main:
    def annotate(everything_results, is_plt=False, is_msk = False, frame=None):
        ''' if is_plot is set True, frame cannot be None and function will return img for cv2.imwrite '''
        i_a = time.perf_counter()

        if is_plt:
            if type(frame) == type(None):
                raise('frame cannot be None when plotting is set true')
        else:
            frame = None

        if type(everything_results) is type(None):
            print('UNUSUAL nothing detected.')
            if is_plt:
                return frame
            else:
                return None

        # debugging purposes (converts ultralytic object to usable string)
        # print(everything_results[0].masks.shape)
        # print(everything_results[0].boxes.shape)
        # print(everything_results[0].boxes[0].xyxy.cpu().numpy())
        
        # objectify objects
        for box in everything_results[0].boxes:
            box = box.xyxy.cpu().numpy()

            for b in box:
                x, y, x2, y2 = map(int, b)
                x_center = (x + x2) // 2
                y_center = (y + y2) // 2
                
                # put boxes and dots if it's for plotting
                if is_plt:
                    cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, (x_center, y_center), radius=5, color=(0, 0, 255), thickness=-1)
                
                bucket.current_objects.append({'fingerprint':tools.fingerprint(),'plot':(x, y, x2, y2)}) # (fingerprint, center of objects)

        if is_msk:
            print('masking...')
            prompt_process = FastSAMPrompt(img, er, device=bucket.DEVICE)
            ann = prompt_process.everything_prompt()
            out_img = prompt_process.plot(
            annotations=ann,
            bboxes= None,
            points= None,
            point_label= None,
            withContours=True
            )
            return out_img
        
        e_a = time.perf_counter()

        print(f'annotation took {e_a - i_a}s')
        
        if is_plt:
            return img
        else:
            return bucket.current_objects

    def inference(img):
        '''img is not a path. cv2.imread() it'''
        print('\nfastsam inference entered')
        i_i = time.perf_counter()
        
        everything_results = bucket.model(
            img,
            device=bucket.DEVICE,
            retina_masks=True,
            imgsz=1024,
            conf=bucket.confidence,
            iou=bucket.iou
        )
        e_i = time.perf_counter()
        print(f'inference took {e_i - i_i}s\n')

        return everything_results


mode = 'x'
initialize.init(mode, confidence=0.7,iou=0.4) # sweet spot is iou = 0.9 & confidence = 0.8 or 0.9


# inference all the files within samples folder
samples_path = '/Users/changbeankang/Claw_For_Humanity/HOS_II/FastSAM-main/SAM_sample'

i = 0

for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    out_path = f'/Users/changbeankang/Claw_For_Humanity/HOS_II/Sample-Images/FastSAM/{mode}/{i}.jpg'

    img = cv2.imread(file_path)
    er = main.inference(img)

    out_img = main.annotate(everything_results=er,
                            is_plt=True,
                            is_msk=False,
                            frame=img)
    
    cv2.imwrite(out_path,out_img)

    i += 1



