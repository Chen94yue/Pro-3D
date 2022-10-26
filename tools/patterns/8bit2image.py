import cv2
import sys
import os
import glob
import numpy as np

def trans8bit24bit(image1, image2, image3):
    g = cv2.imread(image1)
    g = cv2.cvtColor(g, cv2.COLOR_BGR2GRAY)
    r = cv2.imread(image2)
    r = cv2.cvtColor(r, cv2.COLOR_BGR2GRAY)
    b = cv2.imread(image3)
    b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)
    image = np.zeros((1140, 912, 3), dtype=np.uint8)
    image[:,:,0] = b
    image[:,:,1] = g
    image[:,:,2] = r
    return image

if __name__ == "__main__":
    image_files = glob.glob(os.path.join(sys.argv[1], '*'))
    image_files.sort()
    # print(image_files)
    batch = []
    index = 0
    out_path = sys.argv[2]
    for i in image_files:
        batch.append(i)
        if len(batch) == 3:
            image1, image2, image3 = batch
            out_image = trans8bit24bit(image1, image2, image3)
            out_name = 'output_%02d.bmp'%index
            index += 1
            cv2.imwrite(os.path.join(out_path, out_name), out_image)
            batch = []
    if len(batch) > 0:
        while len(batch) > 0 and len(batch) < 3:
            batch.append(batch[-1])
        image1, image2, image3 = batch 
        out_image = trans8bit24bit(image1, image2, image3)
        out_name = 'output_%02d.bmp'%index
        index += 1
        cv2.imwrite(os.path.join(out_path, out_name), out_image)
