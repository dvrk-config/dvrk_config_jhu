# Isaac Sim Virtual Patient Cart for JHU da Vinci Si

Configurations and launch files for running the JHU da Vinci Si surgeon console paired with the NVIDIA Isaac Sim virtual patient cart.

- `isaac_sim_patient_cart.yaml`: Runtime simulator configuration (headless, raytraced lighting, simulation rate).
- `ECM_PSM1_PSM2_PSM3.yaml`: Patient-cart scene specification with stereo RTSP camera streaming on localhost.
- `stereo_display_simulator.json`: Stereo display configuration connecting `stereo_display` to the local RTSP stream (`rtsp://127.0.0.1:8554/ECM`).
- `system-MTMR-MTML-IsaacSim-Teleop.json`: CRTK console system teleoperation configuration.
- `launch/daVinciSi_MTML_MTMR_isaac_sim.launch.py`: Unified ROS 2 launch file to launch the simulator, `dvrk_system`, `stereo_display`, `control_panel` on the current workstation.

The system launch accepts only `exercise`, `rqt`, and `headless`. Use the
control panel to home the system and enable teleoperation. Simulator settings
and display calibration are read from the configuration files in this directory.
