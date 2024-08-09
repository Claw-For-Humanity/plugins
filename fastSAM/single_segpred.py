# before starting, make sure to edit prompt.py

from fastsam import FastSAM, FastSAMPrompt
import torch 
import cv2
import sys
import time

sys.path.append('/Users/changbeankang/Claw_For_Humanity/HOS_II/Google-Circularnet-Integration/')
from fingerprint import main as fingerprint

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
    def annotate(everything_results, is_plt, frame=None, debugging = False):
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


        for box in everything_results[0].boxes:
            box = box.xyxy.cpu().numpy()

            for b in box:
                x, y, w, h = map(int, b)
                everything = (x,y,w,h)
                x_center = (x + w) // 2
                y_center = (y + h) // 2
                
                if is_plt:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.circle(frame, (x_center, y_center), radius=5, color=(0, 0, 255), thickness=-1)
                
                bucket.current_objects.append({'fingerprint':fingerprint.generate(),'plot': everything}) # (fingerprint, center of objects)

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



    def inference(img_path, plt, debugging = False):
        '''img_path has to be jpg format'''
        print('\nfastsam inference entered')
    
        if debugging:
            startTime = time.perf_counter()

        IMAGE_PATH = img_path

        everything_results = bucket.model(
            IMAGE_PATH,
            device=bucket.DEVICE,
            retina_masks=True,
            imgsz=1024,
            conf=bucket.confidence,
            iou=0.9,
        )
        if plt and everything_results != None:
            prompt_process = FastSAMPrompt(IMAGE_PATH, everything_results, device=bucket.DEVICE)


            ann = prompt_process.point_prompt(points=[[620, 360]], pointlabel=[1])

            prompt_process.plot(
                annotations=ann,
                output_path='./output/hello1.jpg',
                mask_random_color=True,
                better_quality=True,
                retina=False,
                withContours=True,
            )

        if debugging:
            dTime = time.perf_counter() - startTime
            print(f'inference took {dTime}s')

        print('fastsam inference done\n')

        return everything_results

