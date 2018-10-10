cmake_minimum_required(VERSION 2.8)
set(CMAKE_CXX_FLAGS "-fpermissive -std=c++0x")

project(ethz_apriltag2)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake/)

find_package(Eigen3 REQUIRED)
find_package(OpenCV REQUIRED)
# find_package(PythonLibs REQUIRED)
# MESSAGE( " *** PYTHON_INCLUDE_DIRS : " ${PYTHON_INCLUDE_DIRS} )
# MESSAGE( " *** PYTHON_LIBRARIES : " ${PYTHON_LIBRARIES} )


add_definitions(-fPIC -O3)
include_directories(include /usr/include/eigen3)

#library
file(GLOB SOURCE_FILES "src/*.cc")
add_library(${PROJECT_NAME}  ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})

#add_python_export_library(aslam_cameras_april_python python/aslam_cameras_april
#  src/module.cpp)
add_subdirectory(pybind11)
pybind11_add_module(apriltags_eth src/module.cpp)
# target_link_libraries(example ${PYTHON_LIBRARIES} ${PROJECT_NAME})
target_link_libraries(apriltags_eth ${PROJECT_NAME})

#demo
if(NOT APPLE)
  add_executable(apriltags_demo src/example/apriltags_demo.cpp src/example/Serial.cpp)
  target_link_libraries(apriltags_demo ${PROJECT_NAME} v4l2)
endif()
