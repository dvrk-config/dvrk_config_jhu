cmake_minimum_required (VERSION 3.10)
project (dvrk_config_jhu VERSION 2.1.0)

find_package (ament_cmake QUIET)
if (ament_cmake_FOUND)
  ament_package ()
endif ()

install (
  DIRECTORY jhu-dVRK jhu-daVinci jhu-dVRK-Si
  DESTINATION share
  )
