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
  pybind11::class_<AprilTags::TagDetector>(m, "AprilTagDetector")
    .def(pybind11::init<AprilTags::TagCodes, size_t>())
    .def("extract_tags", [](const AprilTags::TagDetector& a,
                            pybind11::array_t<uint8_t,
                            pybind11::array::c_style | pybind11::array::forcecast> image)
         {
           cv::Mat cv_image = cv::Mat::zeros(image.shape()[0], image.shape()[1], CV_8U);

           for (size_t i = 0; i < cv_image.rows; ++i) {
             for (size_t j = 0; j < cv_image.cols; ++j) {
               cv_image.at<uchar>(i, j) = *image.data(i, j);
             }
           }

           return a.extractTags(cv_image);
         });

  m.def("make_default_detector", [](){
      AprilTags::TagCodes m_tagCodes = AprilTags::tagCodes36h11;
      return AprilTags::TagDetector(m_tagCodes, 2);
    })
  .def("getRelativeTransform", [](const AprilTags::TagDetection& tag, double tag_size, double fx, double fy, double px, double py){
      Eigen::Matrix4d pose = tag.getRelativeTransform(tag_size,fx,fy,px,py);
      std::vector<double> out;
      for (int r = 0; r < 4; ++r){
        for (int c = 0; c < 4; ++c){
            out.push_back(pose(r,c));
        }
      }
      return out;
    });

  pybind11::class_<AprilTags::TagDetection>(m, "AprilTagDetection")
    .def_readwrite("id", &AprilTags::TagDetection::id)
    .def_readwrite("good", &AprilTags::TagDetection::good)
    .def_readwrite("code", &AprilTags::TagDetection::code)
    .def_readwrite("obs_code", &AprilTags::TagDetection::obsCode)
    .def_readwrite("hamming_distance", &AprilTags::TagDetection::hammingDistance)
    .def_readwrite("rotation", &AprilTags::TagDetection::rotation)
    .def_property_readonly("corners", [](const AprilTags::TagDetection& a){
        std::vector<std::pair<float, float> > out;
        for (int i = 0; i < 4; i++) {
          out.push_back(a.p[i]);
        }
        return out;
      })
    .def_readwrite("cxy", &AprilTags::TagDetection::cxy)
    .def_readwrite("observed_perimeter", &AprilTags::TagDetection::observedPerimeter);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
