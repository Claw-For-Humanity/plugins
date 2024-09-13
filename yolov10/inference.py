import cv2
import tempfile
from ultralytics import YOLOv10
import numpy as np
from PIL import Image
import os


def yolov10_inference(image, video, model_id, image_size, conf_threshold):
    model = YOLOv10.from_pretrained(f'jameslahm/{model_id}')
    if image:
        results = model.predict(source=image, imgsz=image_size, conf=conf_threshold)
        annotated_image = results[0].plot()
        return annotated_image[:, :, ::-1], None
    else:
        video_path = tempfile.mktemp(suffix=".webm")
        with open(video_path, "wb") as f:
            with open(video, "rb") as g:
                f.write(g.read())

        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        output_video_path = tempfile.mktemp(suffix=".webm")
        out = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'vp80'), fps, (frame_width, frame_height))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            results = model.predict(source=frame, imgsz=image_size, conf=conf_threshold)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)

        cap.release()
        out.release()

        return None, output_video_path


def yolov10_inference_for_examples(image, model_path, image_size, conf_threshold):
    annotated_image, _ = yolov10_inference(image, None, model_path, image_size, conf_threshold)
    return annotated_image


# inference all the files within samples folder
samples_path = '/Users/changbeankang/Claw_For_Humanity/HOS_II/yolov10-main/SAM_sample/'

i = 0

for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    
    output_path = f'/Users/changbeankang/Claw_For_Humanity/HOS_II/yolov10-main/output/10x/{i}.png'
    # n s m b l x
    a = yolov10_inference_for_examples(file_path,
                               "yolov10x",
                               640,
                               0.25)
    
    Image.fromarray(a).save(output_path)

    i += 1



