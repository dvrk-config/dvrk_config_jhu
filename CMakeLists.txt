cmake_minimum_required (VERSION 3.10)
project (dvrk_config_jhu VERSION 2.1.0)

find_package (catkin QUIET)
if (catkin_FOUND)
  catkin_package()
endif ()
