#!/usr/bin/env python

import rospy
import std_msgs.msg
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointCloud2
import yaml
import camera
import copy
import math

'''
this is a subscriber to LiDAR's pointscloud 
and will filter the points not in ROI 
then publish them to sub_pointscloud topic
'''

path = 'cam.yaml'
with open(path) as f:
    data = yaml.load(f)

cameras = {}
publishers = {}
result_tmp = {}

for dic in data['Cameras']:
    cam = camera.Camera(data['Cameras'][dic])
    cameras[dic] = cam
    result_tmp[dic] = []
    publishers[dic] = rospy.Publisher(cam.Lidar1.sub_pointscloud, PointCloud2, queue_size=1) #pointscloud's publish rate is not higher than 10hz

def callback(cloud):
    results = copy.deepcopy(result_tmp)
    
    for point in point_cloud2.read_points(cloud, field_names=('x', 'y', 'z'), skip_nans=True):
        angle = math.atan2(point[1], point[0])  # [-pi,pi]
        for c in results:
            if cameras[c].Lidar1.ROI[0] < angle and cameras[c].Lidar1.ROI[1] > angle:
                results[c].append(point)

    for p in publishers:
        my_header = std_msgs.msg.Header()
        my_header.stamp = cloud.header.stamp - rospy.Time(0, cameras[p].Lidar1.TOI) ######## ? ########## does TOI means -scanning time + TOI?
        my_header.frame_id = cloud.header.frame_id
        my_points = point_cloud2.create_cloud_xyz32(my_header, results[p])
        publishers[p].publish(my_points)

rospy.init_node('LidarDistributor1', anonymous=True)
rospy.Subscriber(data['Lidars']['Lidar1'], PointCloud2, callback) # subscribe to Lidar1's data and process
rospy.spin()