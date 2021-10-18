#!/usr/bin/env python3

from libs import *
import camera
import rospy
import sys
from cv_bridge import CvBridge

import message_filters
from sensor_msgs.msg import PointCloud2, Image

'''
synchronization between lidar and 1 camera
'''
path = 'cam.yaml'
camera_name = 'Camera1'

with open(path) as f:
    data = yaml.load(f)

cam = camera.Camera(data['Cameras'][camera_name])
r = np.array(cam.Lidar1.rotation)
t = np.array(cam.Lidar1.translation)

imgsize = (data['ImageSize'][0], data['ImageSize'][1])
distance_max = data['MaxDistance']
timegap = data['Tolerance']

cammat = np.array(cam.camera_mat)
discoeff = np.array(cam.distortion) ##### ? ######
new_cammat, valid_pix_roi = cv.getOptimalNewCameraMatrix(cammat, discoeff, imgsize, 0, imgsize)
mtrx_r, rvec = EulerAng2RMatrix(r, 'd')

bridge = CvBridge()

def callback(cloud, image): #images after synchronization
    xyz = ReadXYZ(cloud)
    image = bridge.imgmsg_to_cv2(image, 'bgr8')
    image = cv.resize(image, imgsize)

    # image = cv2.flip(cv.flip(image, 0), 1) # flip?
    image = cv.undistort(image, cammat, discoeff, newCameraMatrix=new_cammat)

    uv = RePorject(image, xyz, new_cammat.T, mtrx_r, t, ) # use old or new cammat to reproject pointscloud?

    for point in uv.T:  # after tanspose [u | v | third]
        color = [0, math.log(point[2])*255/1.5, 255 - math.log(point[2])*255/1.5]  #BGR
        cv.circle(image, (int(point[0]), int(point[1])), 1, color, -1)

    cv.imshow(cam.node, image)
    if cv.waitKey(1) == ord('q'):
        rospy.signal_shutdown("example finished")
        sys.exit()

rospy.init_node(cam.node, anonymous=True)
image_subscribe = message_filters.Subscriber(cam.sub_image, Image)
points_subscribe = message_filters.Subscriber(cam.Lidar1.sub_pointscloud, PointCloud2)
ts = message_filters.ApproximateTimeSynchronizer([points_subscribe, image_subscribe], queue_size=4, slop=timegap)
ts.registerCallback(callback)

rospy.spin()