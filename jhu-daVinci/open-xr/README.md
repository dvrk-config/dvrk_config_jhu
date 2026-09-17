# OpenXR da Vinci patient-cart configuration

This directory contains configuration files connecting the JHU da Vinci patient
cart (SUJ, ECM, PSM1, and PSM2) to a Quest/OpenXR surgeon console:

- `system-SUJ-ECM-PSM1-PSM2-OpenXR-Teleop.json` configures the patient-side
  hardware with `sawOpenXR`, pairing MTMR to PSM1 and MTML to PSM2;
- `stereo_source.json`, `stereo_alignment.json`, and `stereo_display.json`
  configure the stereo video pipeline using the `headless` sink, publishing
  composited stereo with dVRK console overlays on
  `@dvrk:stereo_display:openxr-overlay`;
- `sawOpenXR-dvrk-socket.json` receives that composited stream for `sawOpenXR`.

Refer to external package documentation for general setup:

- [`sawOpenXR`](https://github.com/adeguet1/sawOpenXR) is the authoritative
  source for headset setup, video behavior, and controller mappings (clutches,
  camera, jaw control, and video screen repositioning).
- [`sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit)
  provides `dvrk_system` and patient cart hardware control.

The local system JSON is the authoritative record of which MTM is paired with
which PSM and of the teleoperation parameters for this cart.

## Run

From the `jhu-daVinci` directory, start the OpenXR stereo video pipeline in one
terminal:

```bash
ros2 launch dvrk_console stereo_video_pipeline.launch.py config_dir:=$PWD/open-xr
```

> **Note**: Do not run the parent directory's video pipeline at the same time:
> both would attempt to own the DeckLink inputs and the same video sockets.

In a second terminal, start the dVRK system:

```bash
ros2 run dvrk_robot dvrk_system -j open-xr/system-SUJ-ECM-PSM1-PSM2-OpenXR-Teleop.json
```

This is a real-hardware configuration. Verify cart serial numbers, calibration,
video source, arm homing, emergency-stop behavior, and loss-of-tracking
fail-closed behavior before operation.
