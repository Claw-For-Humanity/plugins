# before starting, make sure to edit prompt.py

from fastsam import FastSAM, FastSAMPrompt
import torch 
import cv2
import sys
import time

sys.path.append('/Users/changbeankang/Claw_For_Humanity/HOS_II/plugins/tools')
import tools

class bucket:
    model = None
    DEVICE = None
    current_objects = []
    confidence = None


class initialize:
    def init(confidence=0.8):
        bucket.model = FastSAM('./weights/FastSAM-s.pt')

        bucket.DEVICE = torch.device(
            "cuda"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        bucket.confidence = confidence


class main:
    def annotate(everything_results, is_plt=False, frame=None, debugging = False):
        ''' if is_plot is set True, frame cannot be None'''
        
        print('\nentered annotate')

        if debugging:
            print('debugging enabled')
            startTime = time.perf_counter()

        if is_plt:
            if type(frame) == type(None):
                raise('frame cannot be None when plotting is set true')
        else:
            frame = None

        print(everything_results[0].masks.shape)
        print(everything_results[0].boxes.shape)
        print(everything_results[0].boxes[0].xyxy.cpu().numpy())
        
        for box in everything_results[0].boxes:
            box = box.xyxy.cpu().numpy()

            for b in box:
                x, y, x2, y2 = map(int, b)
                x_center = (x + x2) // 2
                y_center = (y + y2) // 2
                
                if is_plt:
                    cv2.rectangle(frame, (x, y), (x2, y2), (0, 255, 0), 2)
                    cv2.circle(frame, (x_center, y_center), radius=5, color=(0, 0, 255), thickness=-1)
                
                bucket.current_objects.append({'fingerprint':tools.fingerprint(),'plot':(x, y, x2, y2)}) # (fingerprint, center of objects)

        if is_plt:
            print('entered final img write process')
            prompt_process = FastSAMPrompt(frame, everything_results, device=bucket.DEVICE)
            ann = prompt_process.everything_prompt()
            img = prompt_process.plot_to_result(frame, annotations=ann)
            cv2.imwrite('./output/output.jpg', img)

        if debugging:
            dTime = time.perf_counter() - startTime
            print(f'took {dTime} to annotate')
        print('annotation done\n')
        
        return bucket.current_objects



    def inference(img, debugging = False):
        '''img is not a path. cv2.imread() it'''
        print('\nfastsam inference entered')
    
        if debugging:
            startTime = time.perf_counter()


        everything_results = bucket.model(
            img,
            device=bucket.DEVICE,
            retina_masks=True,
            imgsz=1024,
            conf=bucket.confidence,
            iou=0.9,
        )
        

        if debugging:
            dTime = time.perf_counter() - startTime
            print(f'inference took {dTime}s')

        print('fastsam inference done\n')

        if debugging:
            return everything_results, dTime
        else:
            return everything_results
