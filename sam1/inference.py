import numpy as np
import torch
import matplotlib.pyplot as plt
import cv2
import sys
import os
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import time

class bucket:
    sam = None
    mask_generator = None

    mask_generator_2 = None

class initialize:
    def __init__():
        # NOTE: make sure to match
        sam_checkpoint = "./checkpoints/sam_vit_b_01ec64.pth"
        model_type = "vit_b"

        device = "cuda"

        bucket.sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        bucket.sam.to(device=device)

        bucket.mask_generator = SamAutomaticMaskGenerator(bucket.sam)

        bucket.mask_generator_2 = SamAutomaticMaskGenerator(
            model=bucket.sam,
            points_per_side=32,
            pred_iou_thresh=0.86,
            stability_score_thresh=0.92,
            crop_n_layers=1,
            crop_n_points_downscale_factor=2,
            min_mask_region_area=100,  # Requires open-cv to run post-processing
        )


class main:
    def put_anns(anns, img):
        if len(anns) == 0:
            return img  # If no annotations, return the original image     
        
        img = cv2.resize(img, (1024, 1024))


        # Sort annotations by area in descending order
        sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)

        # Ensure the image is in the correct format (if not already)
        if img.ndim == 2:  # Convert grayscale to RGB if needed
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        
        # Loop over each annotation
        for ann in sorted_anns:
            m = ann['segmentation']
            color_mask = (np.random.random(3) * 255).astype(np.uint8)  # Random color for the mask
            
            # Apply the color to the segmentation area (blend mask with the image)
            img[m] = 0.65 * img[m] + 0.35 * color_mask
        
        return img

    
    def inference(path):
        t = time.perf_counter()
        image = cv2.imread(path)
        image = cv2.resize(image, (1024, 1024))

        cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # masks = bucket.mask_generator.generate(image)

        # print(len(masks))
        # print(masks[0].keys())

        masks2 = bucket.mask_generator_2.generate(image)
        print(f'dt is {time.perf_counter() - t}s ')
        return masks2, image


initialize.__init__()

samples_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/Original'

i = 0


for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    
    masks, img = main.inference(file_path)
    out = main.put_anns(masks, img)

    output_path = f'/home/cfh/Desktop/ClawForHumanity/Sample-Images/SAM1/b/{i}.jpg'

    Image.fromarray(out).save(output_path)
    
    i += 1

# h
# dt is 6.943109198999991s 
# dt is 6.959831734999852s 
# dt is 6.846012916000063s 
# dt is 7.126972299000045s 
# dt is 6.510799383000176s 
# dt is 7.117172609999898s 
# dt is 7.198983992999956s 
# dt is 6.731889238000122s 
# dt is 6.722828619999973s 
# dt is 6.780375588999959s 

# l
# dt is 5.996864676000314s 
# dt is 6.175624694999897s 
# dt is 5.35310410000011s 
# dt is 5.663109910000003s 
# dt is 5.4695304920001035s 
# dt is 5.941191685999911s 
# dt is 6.0481560150001314s 
# dt is 5.321949326000322s 
# dt is 5.416836884000077s 
# dt is 5.514925596000012s 

# b
# dt is 4.866891351000049s 
# dt is 4.548444743000346s 
# dt is 4.3452622390000215s 
# dt is 4.464858382999864s 
# dt is 4.429919185000017s 
# dt is 4.636144599999625s 
# dt is 4.630619443999876s 
# dt is 4.496518705000199s 
# dt is 4.341225991000101s 
# dt is 4.2592791530000795s 