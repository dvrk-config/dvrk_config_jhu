# OpenXR da Vinci Si patient-cart configuration

These files configure the JHU da Vinci Si patient cart with `sawOpenXR` as
the surgeon-console input. The Si ECM and PSM serial numbers and `udpfw` IO
configuration match the neighboring patient-cart configurations. MTMR maps
to PSM1 and PSM3; MTML maps to PSM2. PSM1 and PSM3 share the right-hand
OpenXR local clutch event.

Start the stereo video pipeline with this directory before starting the dVRK
system:

```bash
ros2 launch dvrk_console stereo_video_pipeline.launch.py config_dir:=$PWD/open-xr
ros2 run dvrk_robot dvrk_system -j open-xr/system-SUJ-ECM-PSM1-PSM2-PSM3-OpenXR-Teleop.json
```

This is a real-hardware configuration. Verify serial numbers, calibration,
video routing, homing, emergency-stop behavior, and loss-of-tracking
fail-closed behavior before operation.
