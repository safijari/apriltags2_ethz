from apriltags_eth import AprilTagDetector, test, make_default_detector

import cv2

det = make_default_detector()

im = cv2.resize(cv2.imread('/home/jari/Work/Calibration/test.jpg', 0), (640, 480))

for tag in det.extract_tags(im):
    print tag.id
    print tag.corners
