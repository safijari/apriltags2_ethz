# from apriltags_eth import AprilTagDetector, test, make_default_detector

# import cv2

# det = make_default_detector()

# im = cv2.resize(cv2.imread('/home/jari/Work/Calibration/test.jpg', 0), (640, 480))

# for tag in det.extract_tags(im):
#     print tag.id
#     print tag.corners

from aprilgrid import AprilGrid
import cv2

grid = AprilGrid(7, 6, 2.0/100, 0.5/100)

im = cv2.imread('/tmp/april.png')
res = grid.compute_observation(im)

for image_point, tgt_point in zip(res.image_points, res.target_points):
    x = int(image_point[0])
    y = int(image_point[1])
    tx = tgt_point[0]
    ty = tgt_point[1]
    print tgt_point
    cv2.circle(im, (x, y), 5, (255 - tx/0.1205*200, 255, ty/0.1406*200), -1)

cv2.imwrite('/tmp/out.png', im)
