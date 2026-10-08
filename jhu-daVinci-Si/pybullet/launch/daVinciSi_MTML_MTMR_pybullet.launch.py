"""Run the JHU da Vinci Si console with the PyBullet virtual patient cart and stereo display."""

from pathlib import Path
import sys

from ament_index_python.packages import get_package_share_directory
from dvrk_pybullet.python_runtime import resolve_pybullet_python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, ExecuteProcess, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


PACKAGE_NAME = "dvrk_config_jhu"


def generate_launch_description():
    pybullet_python = resolve_pybullet_python()
    package_share = Path(get_package_share_directory(PACKAGE_NAME))
    pybullet_share = Path(get_package_share_directory("dvrk_pybullet"))
    calibration_directory = package_share.parent / "jhu-daVinci-Si"
    pybullet_directory = calibration_directory / "pybullet"
    default_config = pybullet_directory / "pybullet_patient_cart.yaml"
    system_config = pybullet_directory / "system-MTMR-MTML-PyBullet-Teleop.json"
    display_config = pybullet_directory / "stereo_display_simulator.json"
    cart_scene = pybullet_directory / "ECM_PSM1_PSM2_PSM3.yaml"

    simulator = ExecuteProcess(
        cmd=[
            sys.executable,
            str(pybullet_share / "scripts" / "simulator.py"),
            "--config", LaunchConfiguration("pybullet_config"),
            "--scene", LaunchConfiguration("cart_scene"),
            "--scene", LaunchConfiguration("exercise"),
            "--gui", LaunchConfiguration("gui"),
        ],
        additional_env={"DVRK_PYBULLET_PYTHON": LaunchConfiguration("pybullet_python")},
        output="screen",
    )
    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        output="screen",
        cwd=str(calibration_directory),
        arguments=["--json-config", str(system_config)],
    )
    stereo_display = Node(
        package="dvrk_console",
        executable="stereo_display",
        name="stereo_display",
        output="screen",
        arguments=["-c", LaunchConfiguration("display_config")],
    )
    control_panel = Node(
        package="dvrk_console",
        executable="control_panel",
        name="control_panel",
        output="screen",
    )
    start_system = Node(
        package="dvrk_simulator_base",
        executable="start_dvrk_system",
        output="screen",
        arguments=["--console", LaunchConfiguration("console")],
    )
    rqt_monitor = ExecuteProcess(
        cmd=["rqt"],
        additional_env={
            "DVRK_RQT_ARMS": "ECM,PSM1,PSM2,PSM3",
            "DVRK_RQT_CONSOLE": LaunchConfiguration("console"),
        },
        condition=IfCondition(LaunchConfiguration("rqt")),
        output="screen",
    )

    stop_with_simulator = RegisterEventHandler(
        OnProcessExit(
            target_action=simulator,
            on_exit=[EmitEvent(event=Shutdown(reason="NVIDIA PyBullet simulator exited"))],
        )
    )
    stop_with_system = RegisterEventHandler(
        OnProcessExit(
            target_action=dvrk_system,
            on_exit=[EmitEvent(event=Shutdown(reason="dvrk_system exited"))],
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            "exercise", default_value="tray_cubes.yaml",
            description="Exercise scene YAML path or installed exercise filename.",
        ),
        DeclareLaunchArgument(
            "cart_scene", default_value=str(cart_scene),
            description="PyBullet patient-cart scene YAML file.",
        ),
        DeclareLaunchArgument(
            "gui", default_value="false",
            description="Open PyBullet's desktop viewer window.",
        ),
        DeclareLaunchArgument(
            "console", default_value="console",
            description="dVRK console ROS namespace.",
        ),
        DeclareLaunchArgument(
            "rqt", default_value="false",
            description="Start rqt for console and arm monitoring.",
        ),
        DeclareLaunchArgument(
            "pybullet_config", default_value=str(default_config),
            description="PyBullet runtime YAML configuration.",
        ),
        DeclareLaunchArgument(
            "display_config", default_value=str(display_config),
            description="Stereo display configuration for the Goovis side-by-side output.",
        ),
        DeclareLaunchArgument(
            "pybullet_python",
            default_value=str(pybullet_python.path),
            description="PyBullet worker interpreter; the ROS frontend uses the launch interpreter.",
        ),
        simulator,
        stereo_display,
        control_panel,
        dvrk_system,
        start_system,
        rqt_monitor,
        stop_with_simulator,
        stop_with_system,
    ])
