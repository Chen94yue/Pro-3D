import cv2
import numpy as np
import os


class PatternGenerater:

    '''
    description: 
    param {*} self
    param {*} proj_height: 光机的纵向分辨率
    param {*} gen_row: 生成横向条纹pattern
    param {*} proj_width: 光机的横向分辨率
    param {*} gen_col: 生成纵向条纹pattern
    param {*} gray_code: 生成格雷码
    param {*} gray_code_L: 格雷码的波长
    param {*} gray_code_step: 格雷码的步长
    param {*} phase_shifting: 生成相移码
    param {*} phase_shifting_step: 相移码的步长
    param {*} phase_shifting_L: 相移码的波长(可以是列表，若为列表则使用多频外差)
    param {*} gamma: 相移码的gamma矫正系数
    param {*} dithering: 采用图像抖动算法生成1bit相移图
    param {*} dithering_method: 图像抖动方法, “Ordered”或者“Error”
    param {*} save_path: 图像保存路径
    return {*}
    '''

    def __init__(self,
                 proj_height,
                 gen_row,
                 proj_width,
                 gen_col,
                 gray_code,
                 gray_code_L,
                 gray_code_step,
                 phase_shifting,
                 phase_shifting_step,
                 phase_shifting_L,
                 gamma=1,
                 dithering=False,
                 dithering_method='Ordered',
                 save_path='.'
                 ) -> None:
        self.proj_height = proj_height
        self.gen_row = gen_row
        self.proj_width = proj_width
        self.gen_col = gen_col
        self.gray_code = gray_code
        self.gray_code_L = gray_code_L
        self.gray_code_step = gray_code_step
        self.phase_shifting = phase_shifting
        self.phase_shifting_step = phase_shifting_step
        self.phase_shifting_L = phase_shifting_L
        if isinstance(self.phase_shifting_L, int):
            self.phase_shifting_L = [self.phase_shifting_L]
        self.gamma = gamma
        self.dithering = dithering
        self.dithering_method = dithering_method
        self.save_path = save_path

    '''
    description: 生成pattern
    param {*} self
    return {*}
    '''
    def gen_patterns(self):
        self.pattern_number = 0
        if self.gray_code:
            self.gen_phase_shifting()
        if self.phase_shifting:
            self.gen_gray_code()
    
    def gen_gray_code(self):
        graycode_images = []
        gc_height = int((self.proj_height-1)/self.gray_code_L)+1
        gc_width = int((self.proj_width-1)/self.gray_code_L)+1
        graycode = cv2.structured_light_GrayCodePattern.create(gc_width, gc_height)
        patterns = graycode.generate()[1]
        print(patterns[0])
        print(patterns[0].shape)
        for pat in patterns[0::2]:
            img = np.zeros((self.proj_height, self.proj_width), np.uint8)
            for y in range(self.proj_height):
                for x in range(self.proj_width):
                    img[y, x] = pat[int(y/self.gray_code_L), int(x/self.gray_code_L)]
            graycode_images.append(img)            
        if self.gen_col:
            for image in graycode_images[:len(graycode_images)//2]:
                image_name = 'pattern_%03d.png'%self.pattern_number
                save_path = os.path.join(self.save_path,image_name)
                cv2.imwrite(save_path, image)
                self.pattern_number += 1
        if self.gen_row:
            for image in graycode_images[len(graycode_images)//2:]:
                image_name = 'pattern_%03d.png'%self.pattern_number
                save_path = os.path.join(self.save_path,image_name)
                cv2.imwrite(save_path, image)
                self.pattern_number += 1


    def gen_phase_shifting(self):
        phase_images = []
        if self.gen_col:
            for L in self.phase_shifting_L:
                for index in range(self.phase_shifting_step):
                    dx = np.array(range(self.proj_width))
                    vec = 0.5*(np.cos(2*np.pi*dx/L - 2*np.pi*index/self.phase_shifting_step)+1)
                    vec = 255*(vec**self.gamma)
                    img = np.zeros((self.proj_height, self.proj_width))
                    img[:,:] = vec
                    phase_images.append(img.astype(np.uint8))
        if self.gen_row:
            for L in self.phase_shifting_L:
                for index in range(self.phase_shifting_step):
                    dy = np.array(range(self.proj_height))
                    vec = 0.5*(np.cos(2*np.pi*dy/L - 2*np.pi*index/self.phase_shifting_step)+1)
                    vec = 255*(vec**self.gamma)
                    print(vec)
                    img = np.zeros((self.proj_height, self.proj_width))
                    img[:,:] = np.expand_dims(vec,1)
                    phase_images.append(img.astype(np.uint8))


        for ps_image in phase_images:
            image_name = 'pattern_%03d.png'%self.pattern_number
            save_path = os.path.join(self.save_path,image_name)
            cv2.imwrite(save_path, ps_image)
            self.pattern_number += 1

if __name__ == "__main__":
    generater = PatternGenerater(
        proj_height=1140,
        gen_row=True,
        proj_width=912,
        gen_col=True,
        gray_code=True,
        gray_code_L=50,
        gray_code_step=5,
        phase_shifting=True,
        phase_shifting_step=3,
        phase_shifting_L=100,
    )
    generater.gen_patterns()