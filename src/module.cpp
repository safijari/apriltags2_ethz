#include <iostream>
#include "apriltags/TagDetector.h"
//#include "apriltags/Tag16h5.h"
//#include "apriltags/Tag25h7.h"
//#include "apriltags/Tag25h9.h"
//#include "apriltags/Tag36h9.h"
#include "apriltags/Tag36h11.h"
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>
#include "opencv2/opencv.hpp"

void detectorTest(pybind11::array_t<uint8_t, pybind11::array::c_style | pybind11::array::forcecast> array)
{
  AprilTags::TagDetector* detector;
  AprilTags::TagCodes m_tagCodes = AprilTags::tagCodes36h11;

  detector = new AprilTags::TagDetector(m_tagCodes, 2);
  cv::Mat image = cv::Mat::zeros(array.shape()[0], array.shape()[1], CV_8U);
  // image.data = array.data();

  for (int i = 0; i < image.rows; ++i) {
    for (int j = 0; j < image.cols; ++j) {
      image.at<uchar>(i, j) = *array.data(i, j);
    }
  }

  vector<AprilTags::TagDetection> detections = detector->extractTags(image);

  for (auto det : detections) {
    cout << " Id: " << det.id << std::endl;
  }

  delete detector;
}

PYBIND11_MODULE(apriltags_eth, m) {
  m.def("test", &detectorTest);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
