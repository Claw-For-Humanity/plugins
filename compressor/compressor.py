import cv2
from PIL import Image
import numpy as np
import sys
sys.path.append('../plugins/maxBoundingCropper')
from maxBoundingCropper import main as cropper

def resize_with_padding(np_img, target_resolution=(1024, 512), background_color=(0, 0, 0)):
    """
    If you're using this for circularnet, make sure to write it and re-read the file.
    Resize an image to fit within a target resolution, maintaining the aspect ratio, and pad if necessary.
    
    Parameters:
        np_img (numpy.ndarray): Input image in NumPy array format.
        target_resolution (tuple): Desired resolution (width, height).
        background_color (tuple): Color for the padding, default is black (0, 0, 0).
        
    Returns:
        padded_img (numpy.ndarray): The resized image with padding.
    """
    # Extract target dimensions
    target_width, target_height = target_resolution
    
    # Get original dimensions
    orig_height, orig_width = np_img.shape[:2]
    
    # Calculate the aspect ratios of the input and the target resolution
    orig_aspect = orig_width / orig_height
    target_aspect = target_width / target_height
    
    # Determine new dimensions based on aspect ratio
    if orig_aspect > target_aspect:
        # Image is wider, fit width
        new_width = target_width
        new_height = int(target_width / orig_aspect)
    else:
        # Image is taller, fit height
        new_height = target_height
        new_width = int(target_height * orig_aspect)
    
    # Resize the image while maintaining aspect ratio
    resized_img = cv2.resize(np_img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    
    # Create a new image with the target size and the background color
    padded_img = np.full((target_height, target_width, 3), background_color, dtype=np.uint8)
    
    # Calculate top-left corner to center the resized image
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    
    # Place the resized image onto the padded background
    padded_img[y_offset:y_offset + new_height, x_offset:x_offset + new_width] = resized_img
    
    return padded_img

def size_handler(np_img, target_size, boxes, turn= True):
    '''img has to be numpy array'''
    (orig_height, orig_width) = np_img.shape[:2] # make ure that the img is np.arrary'ed
    (target_height, target_width) = target_size
    
    # rotating part
    if turn and target_height>target_width:
        if orig_width>orig_height:
            print('rotating...')
            # np array -> pillow -> rotate -> np array
            np_img = np.array(Image.fromarray(np_img).rotate(-90, expand=True))
    
    elif turn and target_width> target_height:
        if orig_height>orig_width:
            print('rotating...')
            # np array -> pillow -> rotate -> np array
            np_img = np.array(Image.fromarray(np_img).rotate(-90, expand=True))

    else: pass

    # padding part
    np_img = resize_with_padding(np_img, (1024,int(orig_width/(orig_height/1024))))
    np_img = cropper.crop_image_full_box(
                    image= np_img,
                    bounding_boxes= boxes
                    )
    
    return np_img
    