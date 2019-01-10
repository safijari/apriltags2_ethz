# apriltags2_eth
Shameless copy of the apriltags code from https://github.com/ethz-asl/kalibr with a new pybind11 wrapper.
Tested only on `linux`.

# How to Use This: A Woefully Insufficient Guide
To self educate, the `test.py` and `aprilgrid/__init__.py` files are good starting points. 
Also check [here](https://github.com/safijari/apriltags2_ethz/blob/master/src/module.cpp#L38) to understand
the wrapper as well as the underlying objects better.

Currently it's ergonomic only to create a detector for the `t36h11` family. To do that, you can do
```
from apriltags_eth import make_default_detector

detector = make_default_detector()
```

This creates an instance of the type `AprilTagDetector`. Calling the `extract_tags` function on
an `opencv` image will return a list of `AprilTagDetection` objects which contain the following fields 
(not a comprehensive list):
```
id: the id/number of the tag
good: if the detection was high confidence
corners: an array of 4 corners, each corner represented by a tuple e.g. [(x1, y1), (x2, y2) ...]
```
