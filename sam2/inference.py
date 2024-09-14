import os
# if using Apple MPS, fall back to CPU for unsupported ops
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import time

from sam2.build_sam import build_sam2
from sam2.automatic_mask_generator import SAM2AutomaticMaskGenerator


# select the device for computation
if torch.cuda.is_available():
    device = torch.device("cuda")
elif torch.backends.mps.is_available():
    device = torch.device("mps")
else:
    device = torch.device("cpu")
print(f"using device: {device}")

if device.type == "cuda":
    # use bfloat16 for the entire notebook
    torch.autocast("cuda", dtype=torch.bfloat16).__enter__()
    # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
    if torch.cuda.get_device_properties(0).major >= 8:
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
elif device.type == "mps":
    print(
        "\nSupport for MPS devices is preliminary. SAM 2 is trained with CUDA and might "
        "give numerically different outputs and sometimes degraded performance on MPS. "
        "See e.g. https://github.com/pytorch/pytorch/issues/84936 for a discussion."
    )


    np.random.seed(3)


class bucket:
    initialized = False
    sam2 = None
    mask_generator = None
    
    mask_generator_2 = None

class initialize:
    def __init__():
        print('initializing...')
        # sam2_hiera_b_+ for sam2_hiera_base_plus.pt
        sam2_checkpoint = "./checkpoints/sam2_hiera_base_plus.pt"
        model_cfg = "sam2_hiera_b+.yaml"


        print('building sam')
        bucket.sam2 = build_sam2(model_cfg, sam2_checkpoint, device=device, apply_postprocessing=False)
        print('sam built')
        bucket.mask_generator = SAM2AutomaticMaskGenerator(bucket.sam2)
        
        print('building mask generator 2')
        bucket.mask_generator_2 = SAM2AutomaticMaskGenerator(
        model=bucket.sam2,
        points_per_side=64,
        points_per_batch=128,
        pred_iou_thresh=0.7,
        stability_score_thresh=0.92,
        stability_score_offset=0.7,
        crop_n_layers=1,
        box_nms_thresh=0.7,
        crop_n_points_downscale_factor=2,
        min_mask_region_area=25.0,
        use_m2m=True,
        )

        bucket.initialized = True
        
        print('mask generator is generated')
        print('initialized.\n')

class main:
    def put_anns(anns, img, borders=True):
        a_it=time.perf_counter()
        if len(anns) == 0:
            return
        
        # Sort annotations by area
        sorted_anns = sorted(anns, key=lambda x: x['area'], reverse=True)
        
        # Ensure img is in float32 format for proper blending
        img = img.astype(np.float32) / 255.0  # Normalize to [0, 1] range

        for ann in sorted_anns:
            m = ann['segmentation']
            
            # Ensure the mask is of the same size as the image
            if m.shape[:2] != img.shape[:2]:
                print("Mask size doesn't match the image size.")
                continue
            
            # Generate random color for the mask
            color_mask = np.random.random(3)  # Generate random RGB color
            
            # Create a boolean mask and apply it to the original image
            img[m] = img[m] * 0.5 + color_mask * 0.5  # Blend the mask with the image

            if borders:
                # Find and draw contours for the mask
                contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
                contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
                cv2.drawContours(img, contours, -1, (0, 0, 255), thickness=1)  # Draw borders in red

        # Convert float32 image back to 8-bit format for display
        img = (img * 255).astype(np.uint8)
        print(f'a_dt is {time.perf_counter()-a_it}s')
        return img

    def inference(img_path):
        if bucket.initialized == False:
            print('generator not initialized. Make sure to Initialize!')
            initialize.__init__()
        
        print('entered inference')
        img = Image.open(img_path)
        img = img.resize((1024,1024))
        img = np.array(img.convert("RGB"))

        t = time.perf_counter()

        masks2 = bucket.mask_generator_2.generate(img)
        
        print(f'i_dt is {time.perf_counter() - t}s')

        return masks2, img



initialize.__init__()


# inference all the files within samples folder
samples_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/Original'

i = 0

for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    
    masks, img = main.inference(file_path)
    out = main.put_anns(masks, img)

    output_path = f'/home/cfh/Desktop/ClawForHumanity/Sample-Images/SAM2/hiera_base_+/{i}.jpg'



    Image.fromarray(out).save(output_path)

    i += 1


# i_dt = inference dt & a_dt = annotation dt
# all images has been compressed to 1024,1024 for lowering vram usage

# hiera-large
# dt is 35.07073205300003s
# dt is 36.02778265799998s
# dt is 33.807334415000014s
# dt is 34.258599558000014s
# dt is 33.17206638400012s
# dt is 31.748574888999883s
# dt is 33.91574639500004s
# dt is 34.58468069100013s
# dt is 33.333218749000025s
# dt is 32.170059461000164s

# hiera-tiny
# dt is 35.13341342000058s
# dt is 32.64092135499959s
# dt is 32.32062802699966s
# dt is 33.11702046699975s
# dt is 33.283237670000744s
# dt is 32.616562632999376s
# dt is 33.37883453999984s
# dt is 33.03903981399981s
# dt is 32.811151501000495s
# dt is 32.12016739400042s

# hiera-small 
# i_dt is 35.65913728099986s
# i_dt is 35.24803240100027s
# i_dt is 33.7598168909999s
# i_dt is 34.304170647999854s
# i_dt is 33.931696245999774s
# i_dt is 32.3495373400001s
# i_dt is 33.45447230099944s
# i_dt is 33.663282902999526s
# i_dt is 33.9859660989996s
# i_dt is 34.715470559000096s

# hiera-base-plus
# i_dt is 35.188555478000126s
# i_dt is 35.50063874100124s
# i_dt is 36.51252420200035s
# i_dt is 36.4709503189988s
# i_dt is 34.79876738500025s
# i_dt is 34.087960912998824s
# i_dt is 35.12954371299929s
# i_dt is 33.797845246999714s
# i_dt is 33.72583334800038s
# i_dt is 35.47843969200039s