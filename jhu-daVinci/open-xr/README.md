# OpenXR real patient-cart configuration

`system-SUJ-ECM-PSM1-PSM2-OpenXR-Teleop.json` configures the JHU da Vinci
patient side (SUJ, ECM, PSM1, and PSM2) using the existing cart serial numbers
and FireWire configuration.  It replaces the physical MTMs and physical
console inputs with the `sawOpenXR` component:

- Quest left/right controller poses emulate MTML/MTMR in an `OpenXR_HRSV`
  frame.  Its origin is the live midpoint between the HMD eyes and its axes
  follow the virtual video plane, matching the physical stereo viewer used by
  the standard ECM teleoperation geometry.
- Hold right A or left X and move that controller to reposition the virtual
  video screen.  The global clutch is pressed while either button is held; on
  release, both controller poses use the screen's new reference frame before
  the global clutch is released.
- Otherwise the global clutch is released and operator-present is always
  pressed.  Losing headset focus still asserts both local PSM clutches.
- Pull both thumbsticks toward the user to press the camera event.  Releasing
  either thumbstick releases the camera event.
- Pushing the left/right thumbstick at least 75 percent up/away releases the
  local clutch for PSM2/PSM1 respectively. Returning it below the threshold
  clutches that PSM. Index triggers remain mapped to the PSM jaws/grippers.
- Both PSM teleoperators use a `0.2` translation scale by default.
- The OpenXR index-trigger range is published as 60 degrees (released) to 0
  degrees (fully pulled). Each TeleopPSM uses `gripper_scaling` with a
  20-degree zero and 100-degree maximum. For the PSM tool's 80-degree jaw
  maximum, this maps the trigger linearly to +40 through -20 degrees.

The `stereo_source.json`, `stereo_alignment.json`, and `stereo_display.json`
files in this directory preserve the JHU capture and alignment settings. The
display configuration uses the `headless` sink and publishes
the composited stereo image, including dVRK console overlays, on
`@dvrk:stereo_display:openxr-overlay`. sawOpenXR consumes that post-overlay
3840x1080 side-by-side stream and scales it to the 2560x720 side-by-side frame
expected by the HMD.

Start this OpenXR-specific video pipeline before starting the dVRK system. From
the `jhu-daVinci` directory:

```bash
ros2 launch dvrk_console stereo_video_pipeline.launch.py config_dir:=$PWD/open-xr
```

Do not run the parent directory's video pipeline at the same time: both would
attempt to own the DeckLink inputs and the same source/alignment sockets.

On Ubuntu 24.04, the `saw_openxr` build additionally needs the OpenXR headers
and shader compiler (the other Vulkan and GStreamer development dependencies
are normally already installed with the dVRK build dependencies):

```bash
sudo apt install libopenxr-dev glslang-tools
```

Build the OpenXR library and configuration package, then run the configuration
from this directory so its relative support files can be located:

```bash
cd $HOME/wss/dvrk
source install/setup.bash
colcon build --packages-select saw_openxr dvrk_config_jhu --symlink-install
source install/setup.bash
cd src/dvrk/dvrk_config_jhu/jhu-daVinci
ros2 run dvrk_robot dvrk_system -j open-xr/system-SUJ-ECM-PSM1-PSM2-OpenXR-Teleop.json
```

This is a real-hardware configuration.  Verify the cart serial numbers,
calibration, video source, arm homing, emergency-stop behavior, and all
loss-of-tracking/fail-closed transitions before enabling or operating the
patient-side arms. The PSM translation scale is `0.2` and should be reviewed as
part of that validation.
