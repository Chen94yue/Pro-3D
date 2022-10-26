import cv2
import sys
import os
import glob
import numpy as np

def bit1tobit8(images):
    assert len(images) == 8
    image_8bit = np.zeros((1140, 912), dtype=np.uint8)
    for i, image_path in enumerate(images):
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = image // 255
        image_8bit += image * 2**i
    return image_8bit

def trans8bit24bitin1bit(images):
    g = bit1tobit8(images=images[:8])
    r = bit1tobit8(images=images[8:16])
    b = bit1tobit8(images=images[16:24])
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
        if len(batch) == 24:
            out_image = trans8bit24bitin1bit(batch)
            # print(out_image)
            out_name = 'output_%02d.bmp'%index
            index += 1
            cv2.imwrite(os.path.join(out_path, out_name), out_image)
            batch = []
    while len(batch) > 0 and len(batch) < 24:
        batch.append(batch[-1]) 
    out_image = trans8bit24bitin1bit(batch)
    out_name = 'output_%02d.bmp'%index
    index += 1
    cv2.imwrite(os.path.join(out_path, out_name), out_image)