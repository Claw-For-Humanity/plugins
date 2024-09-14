import os
# if using Apple MPS, fall back to CPU for unsupported ops
os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"
import numpy as np
import torch
import matplotlib.pyplot as plt
from PIL import Image
import cv2

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
        sam2_checkpoint = "./checkpoints/sam2_hiera_tiny.pt"
        model_cfg = "sam2_hiera_t.yaml"


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

class main:
    def put_anns(anns, img, borders=True):
        print('Entered annotation generator')
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
        
        return img

    def inference(img_path):
        if bucket.initialized == False:
            print('generator not initialized. Make sure to Initialize!')
            initialize.__init__()
        
        img = Image.open(img_path)
        img = img.resize((1024,1024))
        img = np.array(img.convert("RGB"))

        masks = bucket.mask_generator.generate(img)
        
        print(len(masks))
        print(masks[0].keys())

        masks2 = bucket.mask_generator_2.generate(img)
        
        return masks2, img

# example usage
# image_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/Original'
# output_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/SAM2'

# # initialize
# initialize.__init__()

# # inference
# masks, img = main.inference(image_path)
# out = main.put_anns(masks, img)

# # write image
# cv2.imwrite(output_path, out)




initialize.__init__()

if not bucket.initialized: initialize.__init__()


# inference all the files within samples folder
samples_path = '/home/cfh/Desktop/ClawForHumanity/Sample-Images/Original'

i = 0

for file_name in os.listdir(samples_path):
    file_path = os.path.join(samples_path, file_name)
    
    masks, img = main.inference(file_path)
    out = main.put_anns(masks, img)

    output_path = f'/home/cfh/Desktop/ClawForHumanity/Sample-Images/SAM2/{i}.jpg'



    Image.fromarray(out).save(output_path)

    i += 1