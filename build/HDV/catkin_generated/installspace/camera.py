#!/usr/bin/env python3

class CamInLidar:
    def __init__(self, data) -> None:
        self.sub_pointscloud = data['sub_pointscloud']
        self.TOI = data['TOI']
        self.ROI = data['ROI']
        self.rotation = data['rotation']
        self.translation = data['translation']

class Camera:
    def __init__(self, data) -> None:
        self.sub_image = data['Topics']['sub_image']
        self.node = data['Topics']['node']
        self.camera_mat = data['CameraInfo']['camera_mat']
        self.distortion = data['CameraInfo']['distortion']
        self.Lidar1 = CamInLidar(data['Lidar1'])

if __name__ == '__main__':
    import yaml

    with open('cam.yaml') as f:
        data = yaml.load(f)
        print(data['Tolerance'], '\n')
    for dic in data['Cameras']:
        print(data['Cameras'][dic] , '\n')
    camera = Camera(data['Cameras']['Camera1'])
    print('camera1: ', camera.__dict__, '\n')
    print('lidar1: ', camera.Lidar1.__dict__)