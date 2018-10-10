from apriltags_eth import test

import cv2

im = cv2.resize(cv2.imread('/mnt/hgfs/calibration/test.jpg', 0), (640, 480))

test(im)
