# before starting, make sure to edit prompt.py

from fastsam import FastSAM, FastSAMPrompt
import torch 
import cv2
import sys
import time
import os

sys.path.append('..')
from plugins.tools import tools

class bucket:
    model = None
    DEVICE = None
    current_objects = []
    confidence = None


class initialize:
    def init(confidence=0.8):
        bucket.model = FastSAM('./weights/FastSAM-x.pt')

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

        if debugging:
            startTime = time.perf_counter()

        if is_plt:
            if type(frame) == type(None):
                raise('frame cannot be None when plotting is set true')
        else:
            frame = None

        # print(everything_results[0].masks.shape)
        # print(everything_results[0].boxes.shape)
        # print(everything_results[0].boxes[0].xyxy.cpu().numpy())
        
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
            prompt_process = FastSAMPrompt(frame, everything_results, device=bucket.DEVICE)
            ann = prompt_process.everything_prompt()
            img = prompt_process.plot_to_result(frame, annotations=ann)
            return img

        if debugging:
            dTime = time.perf_counter() - startTime
            print(f'took {dTime} to annotate')
        
        return bucket.current_objects



    def inference(img, debugging = False):
        '''img is not a path. cv2.imread() it'''
    
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

        return everything_results

initialize.init(0.9)

# inference all the files within samples folder
samples_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/Original'

i = 0
model = 's' # x s

for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    
    output_path = f'/home/cfh/Desktop/ClawForHumanity/Sample-Images/FastSAM/{model}/{i}.jpg'
    img = cv2.imread(file_path)
    er = main.inference(img, True)

    out = main.annotate(er, True, img, debugging=True)

    cv2.imwrite(output_path, out)

    i += 1



# x
# inference took 1.5599915129996589s
# inference took 0.149836483999934s
# inference took 0.1308417729997018s
# inference took 0.1455205689999275s
# inference took 0.13117899999997462s
# inference took 0.13650289499946666s
# inference took 0.18033718500009854s
# inference took 0.1367902129995855s
# inference took 0.1383324830003403s
# inference took 0.1368249500001184s

# s
# inference took 1.6261243779999859s
# inference took 0.15214019300037762s
# inference took 0.13081800300005852s
# inference took 0.14513954399990325s
# inference took 0.11584269699960714s
# inference took 0.13429836700015585s
# inference took 0.1711912789996859s
# inference took 0.13169535999986692s
# inference took 0.15734263800004555s
# inference took 0.14123509999990347s
