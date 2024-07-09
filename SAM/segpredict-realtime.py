from fastsam import FastSAM, FastSAMPrompt
from camscan import scan
import torch 
import cv2
import time
import random
import string



model = FastSAM('./weights/FastSAM-s.pt')

avail_cam = scan.list_available_cameras(10)
print (f'camera available is {avail_cam}')
print(f'using cam port {avail_cam[0]}\n')

cap = cv2.VideoCapture(int(avail_cam[1]))

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "mps"
    if torch.backends.mps.is_available()
    else "cpu"
)

print(f'current architecture is {DEVICE}\n')


def fingerprint_generator():
    characters = string.ascii_lowercase + string.digits
    fingerprint = ''.join(random.choice(characters) for _ in range(8))
    return fingerprint


while cap.isOpened():
    
    current_objects = []


    ret, frame = cap.read()

    start = time.perf_counter()

    everything_results = model(
        frame,
        device=DEVICE,
        retina_masks=True,
        imgsz=1024,
        conf=0.7, # confidence here
        iou=0.9,
    )
    print(f"\n\noutput is\n{everything_results}")

    if everything_results is not None:

        print(everything_results[0].masks.shape)
        print(everything_results[0].boxes.shape)
        print(everything_results[0].boxes[0].xyxy.cpu().numpy())



        for box in everything_results[0].boxes:
            box = box.xyxy.cpu().numpy()

            for b in box:
                x, y, w, h = map(int, b)
                x_center = (x + w) // 2
                y_center = (y + h) // 2
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                # Draw a circle at the center of the bounding box
                cv2.circle(frame, (x_center, y_center), radius=5, color=(0, 0, 255), thickness=-1)
                current_objects.append({fingerprint_generator(),(x_center,y_center)}) # (fingerprint, center of objects)
    
            
        prompt_process = FastSAMPrompt(frame, everything_results, device=DEVICE)

        # # everything prompt
        ann = prompt_process.everything_prompt()

    # # bbox prompt
    # # bbox default shape [0,0,0,0] -> [x1,y1,x2,y2]
    # bboxes default shape [[0,0,0,0]] -> [[x1,y1,x2,y2]]
    # ann = prompt_process.box_prompt(bbox=[200, 200, 300, 300])
    # ann = prompt_process.box_prompt(bboxes=[[200, 200, 300, 300], [500, 500, 600, 600]])

    # text prompt
    # ann = prompt_process.text_prompt(text='a photo of a dog')

    # # point prompt
    # # points default [[0,0]] [[x1,y1],[x2,y2]]
    # # point_label default [0] [1,0] 0:background, 1:foreground
    # ann = prompt_process.point_prompt(points=[[620, 360]], pointlabel=[1])

    # point prompt
    # points default [[0,0]] [[x1,y1],[x2,y2]]
    # point_label default [0] [1,0] 0:background, 1:foreground
    # ann = prompt_process.point_prompt(points=[[620, 360]], pointlabel=[1])
    


        end = time.perf_counter()
        total = end-start
        print(f'took {total}ms to inference')
        fps = 1/total
        print(f'fps is {fps}\n')

        img = prompt_process.plot_to_result(frame, annotations=ann)
        # img = prompt_process.point_prompt(points=[[620, 360]], pointlabel=[1])

        cv2.imshow('Processed Frame with masks', img)

    cv2.imshow('Processed Frame', frame)
    print(f'current object is {current_objects}')


    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
cap.release()