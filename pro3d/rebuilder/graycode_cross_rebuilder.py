'''
Author: chenyue93 chenyue21@jd.com
Date: 2022-10-20 18:51:38
LastEditors: chenyue93 chenyue21@jd.com
LastEditTime: 2022-10-20 19:41:26
FilePath: /BasePipeline/pro3d/rebuilder/graycode_cross_rebuilder.py
Description: 

Copyright (c) 2022 by chenyue93 chenyue21@jd.com, All Rights Reserved. 
'''
import numpy as np
import cv2

from .base_rebuilder import BaseRebuilder
from .builder import REBUILDER
from ..utils.load_calibrate import load_calibrate_param

class StereoRig:
    def __init__(self, res1, res2, intrinsic1, intrinsic2, distCoeffs1, distCoeffs2, R, T, F=None, E=None, reprojectionError=None):
        self.res1 = res1
        self.res2 = res2
        self.intrinsic1 = np.array(intrinsic1)
        self.intrinsic2 = np.array(intrinsic2)
        self.distCoeffs1 = np.array(distCoeffs1) if distCoeffs1 is not None else np.zeros(5) # Convert to numpy.ndarray
        self.distCoeffs2 = np.array(distCoeffs2) if distCoeffs2 is not None else np.zeros(5)
        self.R = np.array(R)
        self.T = np.array(T).reshape((-1,1))              
        self.F = np.array(F) if F is not None else None
        self.E = np.array(E) if E is not None else None
        self.reprojectionError = reprojectionError
    
    def getCenters(self):
        """
        Calculate camera centers in world coordinates.
        
        Anyway first camera will always be centered in zero (returned anyway).
        
        Returns
        -------
        numpy.ndarray
            3D coordinates of first camera center (always zero).
        numpy.ndarray
            3D coordinates of second camera center.
        """
        Po1, Po2 = self.getProjectionMatrices()
        C1 = np.zeros(3)    # World origin is set in camera 1
        C2 = -np.linalg.inv(Po2[:,:3]).dot(Po2[:,3])
        return C1, C2
    
    def getProjectionMatrices(self):
        """
        Calculate the projection matrices of camera 1 and camera 2.
        
        Returns
        -------
        numpy.ndarray
            The 3x4 projection matrix of the first camera.
        numpy.ndarray
            The 3x4 projection matrix of the second camera.
        """
        Po1 = np.hstack( (self.intrinsic1, np.zeros((3,1))) )
        Po2 = self.intrinsic2.dot( np.hstack( (self.R, self.T) ) )
        return Po1, Po2

    def getBaseline(self):
        """
        Calculate the norm of the vector from camera 1 to camera 2.
        
        Returns
        -------
        float
            Length of the baseline in world units.
        """
        C1, C2 = self.getCenters()
        return np.linalg.norm(C2) # No need to do C2 - C1 as C1 is always zero (origin of world system)


def _lowLevelRectify(rig):
    """
    Get basic rectification using Fusiello et al.
    for *internal* purposes only.
    
    This assumes that camera is coincident with world origin.
    Please refer to the rectification module for general
    image rectification.
    
    See Also
    --------
    :func:`simplestereo.rectification.fusielloRectify`
    """
    
    # Get baseline vector
    _, B = rig.getCenters()
    # Find new directions
    v1 = B                          # New x direction
    v2 = np.cross([0,0,1], v1)      # New y direction
    v3 = np.cross(v1,v2)            # New z direction
    # Normalize
    v1 = v1 / np.linalg.norm(v1)    # Normalize x
    v2 = v2 / np.linalg.norm(v2)    # Normalize y
    v3 = v3 / np.linalg.norm(v3)    # Normalize z
    # Create rotation matrix
    R = np.array( [ v1, v2, v3 ] )
    
    # Build rectification transforms
    R1 = ( R ).dot( np.linalg.inv(rig.intrinsic1) )
    R2 = ( R ).dot( np.linalg.inv(rig.R) ).dot( np.linalg.inv(rig.intrinsic2) )
    
    return R1, R2, R



@REBUILDER.register_module()
class GraycodeCrossRebuilder(BaseRebuilder):

    def __init__(self, calibrate_param_file, proj_shape, downsample_ratio):
        super(GraycodeCrossRebuilder, self).__init__()
        img_shape, rotation, translation, cam_int, cam_dist, proj_int, proj_dist = \
            load_calibrate_param(calibrate_param_file)
        self.rig = StereoRig(
            img_shape, 
            proj_shape,
            cam_int, proj_int, cam_dist, proj_dist, rotation, translation)
        self.Rectify1, self.Rectify2, commonRotation = _lowLevelRectify(self.rig)
        self.R_inv = np.linalg.inv(commonRotation)
        self.R_inv = np.hstack( ( np.vstack( (self.R_inv,np.zeros((1,3))) ), np.zeros((4,1)) ) )
        self.R_inv[3,3] = 1
        widthC, heightC = self.rig.res1
        self.index = np.zeros((heightC, widthC, 2))
        for x in range(widthC):
            for y in range(heightC):
                self.index[y,x,0] = x
                self.index[y,x,1] = y
        self.ratio = downsample_ratio
        self.index = self.index[::self.ratio,::self.ratio,:]
        # self.index = self.index 
        self.points = np.zeros((heightC, widthC, 3))

    def rebuild(self, pp):
        pc = self.index
        # Consider pixel center (negligible difference, anyway...)
        pc = pc + 0.5
        pp = pp + 0.5
        pc = cv2.undistort(pc, self.rig.intrinsic1, self.rig.distCoeffs1)
        pp = cv2.undistort(pp, self.rig.intrinsic1, self.rig.distCoeffs1)
        # Apply rectification
        pc = cv2.perspectiveTransform(pc, self.Rectify1)
        pp = cv2.perspectiveTransform(pp, self.Rectify2)
        # Add ones as third coordinate
        pc = np.concatenate((pc,np.ones((pc.shape[0], pc.shape[1], 1))),axis=2).astype(np.float32)
        # Get world points
        disparity = np.abs(pp[:,:,[0]] - pc[:,:,[0]])
        pw = self.rig.getBaseline()*(pc/disparity)
        # Cancel common orientation applied to first camera
        # to bring points into camera coordinate system
        finalPoints = cv2.perspectiveTransform(pw, self.R_inv)# .reshape(-1, 3)
        self.points[::self.ratio,::self.ratio,:] = finalPoints
        return self.points