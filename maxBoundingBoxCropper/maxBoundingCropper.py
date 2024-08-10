import numpy as np
import cv2
import sys
sys.path.append('/Users/changbeankang/Claw_For_Humanity/HOS_II/plugins/tools/')
import tools


class main:
    # NOTE: test 1 - working
    def crop_image_test1(width_height, image, bounding_boxes):
        img_width, img_height = width_height[0], width_height[1]
        crop_width, crop_height = 1024, 512 
        
        max_coverage = 0
        best_crop = None

        # Brute-force over possible crop positions
        for cx in range(0, img_width - crop_width + 1, 10):  # Increment by 10 pixels for efficiency
            for cy in range(0, img_height - crop_height + 1, 10):
                coverage = 0
                
                for (x, y, x2, y2) in bounding_boxes:
                    crop_x2, crop_y2 = cx + crop_width, cy + crop_height
                    
                    # Check intersection
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
    def crop_image_test2(width_height, image, bounding_boxes):
        img_width, img_height = width_height[0], width_height[1]
        crop_width, crop_height = 1024,512
        
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




## debugging
a = [{'fingerprint': 'd0ohc3q1', 'plot': (468, 413, 553, 494)}, {'fingerprint': '7j8maf0n', 'plot': (690, 453, 770, 532)}, {'fingerprint': 'qzqa9zvw', 'plot': (103, 869, 192, 967)}, {'fingerprint': 'gk2gssec', 'plot': (0, 643, 207, 796)}, {'fingerprint': 'j8n8w4uy', 'plot': (0, 867, 28, 969)}, {'fingerprint': 'chwj53sw', 'plot': (926, 0, 963, 80)}, {'fingerprint': 'qrjzdab6', 'plot': (74, 1416, 268, 1468)}, {'fingerprint': 'r3llbko7', 'plot': (0, 643, 215, 968)}]

bounding_list = tools.converter(a)

img = cv2.imread('/Users/changbeankang/Claw_For_Humanity/HOS_II/Google-Circularnet-Integration/output/output.jpg')

cropped_test1 = main.crop_image_test1((1080,1920), img, bounding_list)
cropped_test2 = main.crop_image_test2((1080,1920), img, bounding_list)
