cmake_minimum_required (VERSION 3.10)
project (dvrk_config_jhu VERSION 2.1.0)

install (
  DIRECTORY jhu-dVRK jhu-daVinci jhu-dVRK-Si
  DESTINATION share
  )
