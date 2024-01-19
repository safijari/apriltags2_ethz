cmake_minimum_required(VERSION 2.8)
set(CMAKE_CXX_FLAGS "-fpermissive -std=c++0x")

project(ethz_apriltag2)

set(CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${PROJECT_SOURCE_DIR}/cmake/)

# find_package(Eigen3 REQUIRED) # TODO: figure out eigen in container
find_package(OpenCV REQUIRED)

add_definitions(-fPIC -O3)
include_directories(include /usr/include/eigen3)

#library
file(GLOB SOURCE_FILES "src/*.cc")
add_library(${PROJECT_NAME}  ${SOURCE_FILES})

target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS})

add_subdirectory(pybind11)
pybind11_add_module(apriltags_eth src/module.cpp)
target_link_libraries(apriltags_eth PRIVATE ${PROJECT_NAME})