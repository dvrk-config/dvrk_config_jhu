# JHU console with dvrk_newton

`system-MTMR-MTML-Newton-Teleop.json` uses the JHU physical MTMR and MTML,
including the console foot pedals and head sensor. The ECM and PSM1–PSM3 are
ROS arms supplied by `dvrk_newton`.

The local patient-cart scene renders stereo video at 15 fps (800×600 per eye).
The display detects the scene's video resolution when it connects, so the
`cart_scene` launch argument can select another scene without editing the
display configuration.

The launch file starts the Newton scene, this dVRK system configuration, the
simulator stereo display, and the control panel:

```bash
ros2 launch dvrk_config_jhu daVinci_MTML_MTMR_newton.launch.py
```

The console's physical head sensor is configured in the system JSON and is
separate from `stereo_display_simulator.json`, which displays Newton's stereo
camera stream. The head sensor does not provide the stereo video display.

The launch file uses `dvrk_newton`'s Python runtime resolver. Its bootstrap
script creates `.venv-newton` in the workspace root with system site packages.
Activate it before launching if needed:

```bash
source .venv-newton/bin/activate
```

If the workspace environment has not been created yet, run:

```bash
./src/dvrk/dvrk_newton/scripts/bootstrap_venv.sh
```
