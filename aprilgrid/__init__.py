from tagFamilies import t36h11
from apriltags_eth import make_default_detector
from collections import namedtuple

# NOTE: all of this ultimately only works with t36h11, you have been warned

DetectionResult = namedtuple('DetectionResult',
                             ['success', 'image_points',
                              'target_points'])


class AprilGrid(object):
    def __init__(self, rows, columns, size, spacing, family=t36h11):  # spacing is a fraction
        assert size != 0.0
        assert spacing != 0.0
        self.rows = rows
        self.columns = columns
        self.size = size
        self.spacing = spacing
        self.detector = make_default_detector()

    def is_detection_valid(self, detection, image):
        d = detection
        h, w = image.shape[0:2]
        for cx, cy in d.corners:
            if cx < 0 or cx > w:
                return False
            if cy < 0 or cy > h:
                return False
        if not d.good:
            return False
        if d.id >= self.rows * self.columns:  # original code divides this by 4????
            return False

        return True

    def get_tag_corners_for_id(self, tag_id):
        # order is lower left, lower right, upper right, upper left
        # Note: tag_id of lower left tag is 0, not 1
        a = self.size  # https://user-images.githubusercontent.com/5337083/41458381-be379c6e-7086-11e8-9291-352445140e88.png
        b = self.spacing * a
        tag_row = (tag_id) // (self.rows - 1)
        tag_col = (tag_id) % self.columns
        left = bottom = lambda i: i*(a + b)
        right = top = lambda i: (i + 1) * a + (i) * b
        return [
            (left(tag_col), bottom(tag_row)),
            (right(tag_col), bottom(tag_row)),
            (right(tag_col), top(tag_row)),
            (left(tag_col), top(tag_row))
        ]

    def compute_observation(self, image):
        # return imagepoints and the coordinates of the corners
        # 1. remove non good tags
        detections = self.detector.extract_tags(image)

        # Duplicate ID search
        ids = {}
        for d in detections:
            if d.id in ids:
                raise Exception(
                    "There may be two physical instances of the same tag in the image")
            ids[d] = True

        filtered = [d for d in detections if self.is_detection_valid(d, image)]

        image_points = []
        target_points = []

        filtered.sort(key=lambda x: x.id)

        # TODO: subpix refinement?

        for f in filtered:
            target_points.extend(self.get_tag_corners_for_id(f.id))
            image_points.extend(f.corners)

        success = True if len(filtered) > 0 else False

        return DetectionResult(success, image_points, target_points)
