import cv2
import sys
sys.path.append('D:\Linux\code\Pro-3D')
from pro3d.decoder import build_decoder
import glob
import numpy as np
import torch

decoder_cfg = dict(
    type='ComplementaryGraycode',
    ps_img_num=3,
    gc_img_num=5,
    bg_thr=0,
    wavelength=100,
    downsample_ratio=0,
    col_only=False,
    cuda=False
)

if __name__ == "__main__":
    decoder = build_decoder(decoder_cfg)
    image_files = glob.glob('D:\Linux\code\Pro-3D\demo\decode\patterns\*')
    patterns = []
    for image_path in image_files:
        image = cv2.imread(image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        patterns.append(image)
    patterns = np.array(patterns)
    patterns_tensor = torch.tensor(patterns, dtype=torch.float32)
    map = decoder(patterns_tensor)
    col_map = map[:,:,0]
    col_map = col_map.numpy()
    cv2.imwrite('decode_col.png', col_map/(np.max(col_map))*255)
    row_map = map[:,:,1]
    row_map = row_map.numpy()
    cv2.imwrite('decode_row.png', row_map/(np.max(row_map))*255)

