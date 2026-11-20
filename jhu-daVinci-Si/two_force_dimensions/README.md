# Two Omega.7 masters with the da Vinci Si patient cart

`system-daVinciSi-ForceDimension.json` configures the real JHU Si patient cart
over `udpfw`, with the existing ECM, PSM1/2/3, and Si SUJ configuration and
calibration files from the parent directory.

| Master | Omega.7 serial | PSM assignment |
| --- | --- | --- |
| MTML | 11773 | PSM2 |
| MTMR | 11311 | PSM1, switchable to PSM3 |

The patient-side serials are ECM 438610, PSM1 334809, PSM2 586288, and
PSM3 698534. `omega7-MTML-MTMR.json` binds the masters by serial number.
Both use one `mtsForceDimension` component.

Each device's `base_frame` in `omega7-MTML-MTMR.json` maps its SDK axes to
the upright screen frame: `x_user = -y_device`, `y_user = z_device`, and
`z_user = -x_device`. Positive user axes are screen right, screen down, and
away from the viewer. The transform has zero translation and no screen tilt.
This includes a 180-degree rotation about image Z to reverse image X and Y
while preserving depth. It rotates measured poses and velocities; the wrapper applies the inverse
transform to position commands and rotates wrenches consistently.

The MTML serial 11773 is retained from the configuration already in this
directory. Verify it against the new device before running, and update
`omega7-MTML-MTMR.json` if needed. MTMR serial 11311 matches the existing
Force Dimension configuration in `../../jhu-dVRK-Si/omega7-11311.json`.

The wrapper initializes and validates each Omega directly through the SDK.
Both devices set `force_initialization: false`: when `drdIsInitialized(id)`
is true, the wrapper reuses that initialization without repeating AutoInit or
CheckInit. Otherwise it runs `drdAutoInit(id)` followed by `drdCheckInit(id)`.
Each device has its own initialization thread, so both can home concurrently
without blocking the component's startup or command processing. Measurements
remain invalid and the operating state busy until initialization finishes.
The devices move and sweep their endstops during full initialization; keep
their workspaces clear. Initialization or validation failure leaves the
affected device faulted and unhomed, with invalid measurements. A `home` state
command reuses a successful initialization, including when the console sends
`enable` followed by `home` after powering the system back on. To request full
recalibration, send `unhome` then `home`; `force_initialization: true` forces
the full sequence on every application launch only. A failed validation is
always retried in full on the next `home`. Free requests received during
homing take effect when it ends; a disable request keeps the device disabled
after homing.

SDK 3.17.7 exposes no public DRD function to save this initialization to disk
and restore it after a power cycle. Reusing an initialized, still-powered
device avoids repeated homing between application runs. A reset or power cycle
can require initialization again.

For standalone initialization, the serial-selectable helper is also available
after building this package. Stop `dvrk_system` and
other Force Dimension clients first. Initialization moves the selected device;
validation sweeps its endstops. Keep its workspace clear.

```bash
ros2 run dvrk_config_jhu force_dimension_autoinit --list
ros2 run dvrk_config_jhu force_dimension_autoinit --serial 11311
# Or initialize and validate both, sequentially:
ros2 run dvrk_config_jhu force_dimension_autoinit --serial 11311 --serial 11773
```

The helper calls `drdAutoInit(id)` unconditionally, then `drdCheckInit(id)`,
`drdStop(true, id)`, and closes the connection. The SDK's example selects only
the first device with `drdOpen()`; this helper matches serials instead. The
wrapper now performs both steps directly; it never invokes this helper or
the SDK example as a subprocess.
The helper defaults to the installed Linux x86_64 SDK 3.17.7 shared library;
use `--library /path/to/libdrd.so` for another installation. It exits after
initialization and validation, without the example's interactive force loop.

`sawGenericInput-dVRK-console.json` uses the existing PCsensor pedals through
`sawGenericInput` / `mtsEvdev`. Its exclusive evdev capture maps `KEY_A` to
clutch, `KEY_B` to camera, and `KEY_C` to operator present. Hold the operator
present pedal to permit teleoperation; releasing it clears operator presence.
The device selector matches `PCsensor FootSwitch Keyboard`, USB `3553:b001`.
The user running the system needs access to its `/dev/input` device.

Install sawGenericInput's device-specific udev rule once on the workstation:

```bash
cd ~/wss/dvrk
sudo install -m 0644 src/cisst-saw/sawGenericInput/core/share/udev/70-saw-evdev-pcsensor.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
```

Unplug/replug the pedals, then restart the launch. This grants the active local
desktop user access to the pedal keyboard node and creates
`/dev/input/saw-pcsensor-pedals`; it does not grant access to other keyboards.
Verify with `getfacl /dev/input/saw-pcsensor-pedals`. This `uaccess` rule relies
on an active local seat session; SSH-only operation requires separate
administrator-managed access. If input still fails, stop `dvrk_system` to
release its exclusive grab, then use
`evtest /dev/input/saw-pcsensor-pedals` to check for `KEY_A`, `KEY_B`, and
`KEY_C` press/release events.

While the camera pedal is held, MTMR controls the ECM using
`TELEOP_ECM_ONE_HAND`, which uses changes in that master's local pose and
does not perform the two-hand MTM workspace check. Two-hand ECM
teleoperation would also require measured physical offsets between the two
devices; the current zero-translation transforms only align their axes.
The transforms belong in the Force Dimension device configuration, rather
than the `MTM_GENERIC` arm entries in the system file.

The PSM teleoperation settings follow the existing Omega.7 example:
scale 0.4, `align_MTM: false`, `start_gripper_threshold: 0.0`, and gripper
angles `zero: 0.25`, `max: 0.492` radians. These gripper values are carried
over to the new MTML and need checking on that device.

SDI capture uses DeckLink input 0 for the left eye and input 1 for the right
eye, at 1920x1080, `1080i5994`, with bottom-field deinterlacing. The geometry
and color correction values come from `../sdi/stereo_alignment.json`;
color correction is in a separate file to match the current video schema.
`control_panel` displays the aligned stream through
`@dvrk:stereo_alignment:stereo`. The launch file starts `dvrk_system`,
`stereo_source`, `stereo_alignment`, and `control_panel`.

Build the configuration package once after adding or updating these files:

```bash
cd ~/wss/dvrk
colcon build --packages-select sawForceDimensionSDKCore dvrk_config_jhu --symlink-install
source install/setup.bash
```

Then launch from the workspace root or any other directory:

```bash
ros2 launch dvrk_config_jhu davinci_si_force_dimension.launch.py
```

To start the components individually, use separate terminals in this directory:

```bash
(cd .. && ros2 run dvrk_robot dvrk_system -j two_force_dimensions/system-daVinciSi-ForceDimension.json)
ros2 run dvrk_data stereo_source -c stereo_source.json
ros2 run dvrk_data stereo_alignment -c stereo_alignment.json --color-adjustment stereo_color_adjustment.json
ros2 run dvrk_console control_panel -c control_panel.json
```

Run `dvrk_system` with the parent `jhu-daVinci-Si` directory as its working
directory. RobotIO searches that directory for the potentiometer lookup
tables independently of the system's configuration search path.
`settings.path: ["two_force_dimensions"]` locates the Omega and pedal files.
The launch file finds the installed configuration and sets the working
directory automatically. Keep this directory alongside the parent cart
configuration.

The required components are `sawForceDimensionSDK` with its SDK/USB access,
`sawGenericInput` with evdev access, `dvrk_robot`, `dvrk_data`,
`dvrk_console`, and GStreamer's DeckLink plugin. The files have been checked
without starting the hardware; device initialization, motion directions,
new-master gripper calibration, pedal behavior, and SDI routing still need
verification on the system.
