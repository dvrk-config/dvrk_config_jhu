cmake_minimum_required (VERSION 3.16)
project (dvrk_config_jhu VERSION 2.5.0)

find_package (ament_cmake QUIET)
if (ament_cmake_FOUND)
  ament_package ()
endif ()

install (
  DIRECTORY jhu-dVRK jhu-daVinci jhu-dVRK-Si jhu-daVinci-Si
  DESTINATION share
  )

install (
  DIRECTORY newton pybullet
  DESTINATION share/${PROJECT_NAME}
  PATTERN "launch" EXCLUDE
  PATTERN "*.launch.py" EXCLUDE
  PATTERN "*.pyc" EXCLUDE
  )

install (
  FILES newton/launch/daVinci_MTML_MTMR_newton.launch.py
  DESTINATION share/${PROJECT_NAME}/launch
  )

install (
  FILES jhu-daVinci-Si/newton/launch/daVinciSi_MTML_MTMR_newton.launch.py
  DESTINATION share/${PROJECT_NAME}/launch
  )

install (
  FILES pybullet/launch/daVinci_MTML_MTMR_pybullet.launch.py
        jhu-daVinci-Si/pybullet/launch/daVinciSi_MTML_MTMR_pybullet.launch.py
  DESTINATION share/${PROJECT_NAME}/launch
  )
