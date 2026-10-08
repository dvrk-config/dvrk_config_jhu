# JHU da Vinci Si console with Newton

This setup uses the Si system's physical MTML (28989), MTMR (30924), MTML-side
foot pedals, `udpfw` IO, and Goovis HID head sensor (`hid/goovis-hd.json`).
Newton supplies the ECM and PSM1–PSM3 through ROS. The console pairs MTMR with
PSM1 and MTML with PSM2/PSM3, matching the existing Si system configuration.

The Goovis display uses one `side_by_side` window and the Si display's
`display_horizontal_offset_px: -150` setting. It reads Newton's stereo Unix
socket directly; the hardware HDMI/SDI capture and stereo alignment processes
are not required for simulated video. `eye_size: auto` detects the stream
resolution. The default scene retains the example's 800×600 per eye at 15 fps.
The display offset can be adjusted in `stereo_display_simulator.json` for the
rendered resolution and the operator's view.

From the workspace root, bootstrap and build:

```bash
./src/dvrk/dvrk_newton/scripts/bootstrap_venv.sh --yes
colcon build --symlink-install --packages-select dvrk_simulator_base dvrk_newton dvrk_config_jhu
source install/setup.bash
ros2 launch dvrk_config_jhu daVinciSi_MTML_MTMR_newton.launch.py
```

The rest of the dVRK workspace, including `dvrk_robot`, `dvrk_console`, and
`dvrk_model`, must already be built and sourced. The launch starts the Newton
ROS frontend and its separate simulation worker, dvrk_system with the Si
calibration directory, stereo display, control panel, and start_dvrk_system.

The workspace `.venv-newton` is selected automatically for the simulation
worker. Activating it is optional; the ROS frontend uses the launch Python.
Override `newton_python` if needed. Other launch arguments are `exercise`
(default `tray_cubes.yaml`), `cart_scene`, `headless`, `console`, `rqt`,
`newton_config`, and `display_config`.

This configuration controls the physical masters and console inputs. The
patient-cart arms and SUJ are supplied by simulation rather than hardware.
