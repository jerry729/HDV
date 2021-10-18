#!/usr/bin/env python

from numpy.lib.type_check import imag
import yaml
import cv2 as cv
import math
from genpy import message
from sensor_msgs import point_cloud2
import numpy as np


def ReadXYZ(cloud):
    '''
    Since coordinate info is the only needed in the PointCloud2 messages when project

    @cloud: PointCloud2 Message
    @return: a numpy matrix, 0 axis is N points and 1 axis is [x,y,z] coordinates
    '''
    xyz = np.zeros((cloud.width, 3))
    i = 0
    for point in point_cloud2.read_points(cloud, ('x', 'y', 'z'), True):
        for j in range(3):
            xyz[i][j] = point[j]
        i += 1

    return xyz

def RePorject(image, xyz, cam_mat, R, T, distance=None):
    '''
    [intrinsic] [R|T] pointscloud --> pixel uv coordinates with size of image.
    [R T] from iterative closet point(ICP), drop the points too far from lidar

    @image xyz cam_mat R T distance
    @return: [u|v|distance]
    '''

    col = image.shape[0]
    row = image.shape[1]
    
    # remove the points project to the back of the camera ?
   
    # ? why remove points whose distance is too far 
    dis = np.sqrt(np.sum(xyz ** 2, axis=1)) # for every xyz row vector in matrix, get the Euclidian norm # not keep dim
    if dis is not None:
        index_keep = np.where(dis <= distance)
        xyz = xyz[index_keep]
        dis = dis[index_keep]

    # extrinsic transformation
    afterRT = np.dot(xyz, R) + T #### why not R.T #####
    #intrinsic transformation
    replane = np.dot(afterRT, cam_mat)
    u = replane[:, 0]/replane[:, 2]
    v = replane[:, 1]/replane[:, 2]

    idx = np.where((u > 1) & (u < col) & (v > 1) & (v < row))
    u = u[idx]
    v = v[idx]
    dis = dis[idx]

    results = np.c_[u, v, dis].T
    return results

def EulerAng2RMatrix(theta, angle_type='r'):
    if angle_type == 'd':
        for i in range(3):
            theta[i] = math.radians(theta[i])

    r_x = np.array([[1, 0, 0],
                    [0, math.cos(theta[0]), -math.sin(theta[0])]
                    [0, math.sin(theta[0]), math.cos(theta[0])]])

    r_y = np.array([[math.cos(theta[1]), 0, math.sin(theta[1])]
                    [0, 1, 0, 0]
                    [-math.sin(theta[1]), 0, math.cos(theta[1])]])

    r_z = np.array([[math.cos(theta[2]), -math.sin(theta[2]), 0]
                    [math.sin(theta[2]), math.cos(theta[2]), 0]
                    [0, 0, 1]])

    R = np.dot(r_z,np.dot(r_y, r_x)) # first rotate around x then y, z
    
    # rotation matrix to rotation vector # rotation vector，a 3D vector，direction= rotation axis，length= roration angle
    rvec = np.zeros((1,3),dtype=np.float64)
    rvec, jacob = cv.Rodrigues(R, rvec)

    return R, rvec


####### ? ######
def RMatrix2EulerAng(R):
    pass