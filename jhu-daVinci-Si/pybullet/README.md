# JHU da Vinci Si console with PyBullet

This setup uses the physical Si masters, MTML-side pedals, udpfw IO, and Goovis HID head sensor. PyBullet supplies the ECM and PSM1–PSM3 through ROS. MTMR controls PSM1; MTML controls PSM2 and PSM3.

The stereo video feeds the Goovis side-by-side display with a -150 px offset. The scene retains the corresponding Newton setup's camera resolution and frame rate. The display detects the stream resolution automatically.

From the workspace root:

```bash
./src/dvrk/dvrk_pybullet/scripts/bootstrap_venv.sh --yes
colcon build --symlink-install --packages-select dvrk_simulator_base dvrk_pybullet dvrk_config_jhu
source install/setup.bash
ros2 launch dvrk_config_jhu daVinciSi_MTML_MTMR_pybullet.launch.py
```

The remaining dVRK workspace, including `dvrk_robot`, `dvrk_console`, and `dvrk_model`, must already be built and sourced. The launch starts the ROS frontend, separate PyBullet simulation and camera workers, dvrk_system with the hardware calibration directory, stereo display, and control panel. Closing the simulator or dvrk_system shuts down the launch.

The workspace `.venv-pybullet` is selected by the runtime resolver; activating it is optional. Set `DVRK_PYBULLET_PYTHON` to select another worker interpreter if needed. The launch accepts only `exercise` (default `tray_cubes.yaml`), `rqt` (default `false`), and `headless` (default `true`). Use the control panel to home the system and enable teleoperation. Edit the configuration files in this directory for simulator and display settings.

`pybullet_patient_cart.yaml` selects EGL rendering. Set `renderer: tiny` for CPU rendering. The scene and stereo display use the same `@dvrk:simulator:stereo_source` socket. Run one simulator for this console at a time.
