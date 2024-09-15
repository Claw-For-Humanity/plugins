import numpy as np
import cv2
import sys
sys.path.append('../plugins/tools')
import tools


class main:
    # NOTE: test 1 - working
    def crop_image_coverage_area(image, bounding_boxes, target_ratio = (1024,512)):
        '''make sure that image is ndarray'''
        img_height, img_width = image.shape[:2]
        
        crop_width, crop_height = target_ratio 
        
        max_coverage = 0
        best_crop = None

        # Brute-force over possible crop positions
        for cx in range(0, img_width - crop_width + 1, 10):  # Increment by 10 pixels for efficiency
            for cy in range(0, img_height - crop_height + 1, 10):
                coverage = 0
                
                for (x, y, x2, y2) in bounding_boxes:
                    crop_x2, crop_y2 = cx + crop_width, cy + crop_height
                    
                    # Check intersecting area
                    overlap_width = max(0, min(crop_x2, x2) - max(cx, x))
                    overlap_height = max(0, min(crop_y2, y2) - max(cy, y))
                    if overlap_width > 0 and overlap_height > 0:
                        coverage += 1
                
                # If this crop has more coverage, update
                if coverage > max_coverage:
                    max_coverage = coverage
                    best_crop = (cx, cy, cx + crop_width, cy + crop_height)
        
        # Crop the image based on best_crop
        if type(best_crop) is not type(None):
            cx, cy, cx2, cy2 = best_crop
            print (f'best_crop is {best_crop}')
            cropped_image = image[cy:cy2, cx:cx2]

            cv2.imwrite('./output/cropped_image_test1.jpg', cropped_image)

            return cropped_image
        
        return None  # In case no valid crop was found


    # NOTE: test2 - working
    def crop_image_full_box(image, bounding_boxes, target_ratio = (1024,512)):
        img_height, img_width = image.shape[:2]
        crop_width, crop_height = target_ratio # fixed
        
        max_coverage = 0
        best_crop = None

        # Brute-force over possible crop positions
        for cx in range(0, img_width - crop_width + 1, 10):  # Increment by 10 pixels for efficiency
            for cy in range(0, img_height - crop_height + 1, 10):
                full_boxes_count = 0
                
                for (x, y, x2, y2) in bounding_boxes:
                    crop_x2, crop_y2 = cx + crop_width, cy + crop_height
                    
                    if cx <= x and cy <= y and x2 <= crop_x2 and y2 <= crop_y2:
                        full_boxes_count += 1
                
                # If this crop has more fully contained boxes, update
                if full_boxes_count > max_coverage:
                    max_coverage = full_boxes_count
                    best_crop = (cx, cy, cx + crop_width, cy + crop_height)
        
        # Crop the image based on best_crop
        if type(best_crop) is not type(None):
            cx, cy, cx2, cy2 = best_crop
            cropped_image = image[cy:cy2, cx:cx2]
            print('best crop is \n')
            print(best_crop)
            cv2.imwrite('./output/cropped_image_test2.jpg', cropped_image)
            return cropped_image
        
        return None  # In case no valid crop was found



