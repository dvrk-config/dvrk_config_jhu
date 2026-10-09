"""Run the JHU da Vinci Si console with the Isaac Sim virtual patient cart and stereo display."""

from pathlib import Path
from tempfile import gettempdir
import sys

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, ExecuteProcess, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from dvrk_simulator_base.rqt_perspective import write_monitor_perspective


PACKAGE_NAME = "dvrk_config_jhu"


def generate_launch_description():
    package_share = Path(get_package_share_directory(PACKAGE_NAME))
    isaac_share = Path(get_package_share_directory("dvrk_isaac_sim"))
    calibration_directory = package_share.parent / "jhu-daVinci-Si"
    isaac_directory = calibration_directory / "isaac_sim"
    default_config = isaac_directory / "isaac_sim_patient_cart.yaml"
    system_config = isaac_directory / "system-MTMR-MTML-IsaacSim-Teleop.json"
    display_config = isaac_directory / "stereo_display_simulator.json"
    cart_scene = isaac_directory / "ECM_PSM1_PSM2_PSM3.yaml"

    simulator = ExecuteProcess(
        cmd=[
            sys.executable,
            str(isaac_share / "scripts" / "simulator.py"),
            "--config", str(default_config),
            "--scene", str(cart_scene),
            "--scene", LaunchConfiguration("exercise"),
            "--headless", LaunchConfiguration("headless"),
        ],
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
        arguments=["-c", str(display_config)],
    )
    control_panel = Node(
        package="dvrk_console",
        executable="control_panel",
        name="control_panel",
        output="screen",
    )
    perspective = write_monitor_perspective(
        Path(gettempdir()) / "dvrk_config_jhu" / "monitor.perspective",
        ("ECM", "PSM1", "PSM2", "PSM3"),
        include_console=True,
    )
    rqt_monitor = ExecuteProcess(
        cmd=["rqt", "--perspective-file", str(perspective)],
        additional_env={
            "DVRK_RQT_ARMS": "ECM,PSM1,PSM2,PSM3",
            "DVRK_RQT_CONSOLE": "console",
        },
        condition=IfCondition(LaunchConfiguration("rqt")),
        output="screen",
    )

    stop_with_simulator = RegisterEventHandler(
        OnProcessExit(
            target_action=simulator,
            on_exit=[EmitEvent(event=Shutdown(reason="Isaac Sim simulator exited"))],
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
            "headless", default_value="true",
            description="Run Isaac Sim without its desktop viewer window.",
        ),
        DeclareLaunchArgument(
            "rqt", default_value="false",
            description="Start rqt for console and arm monitoring.",
        ),
        simulator,
        stereo_display,
        control_panel,
        dvrk_system,
        rqt_monitor,
        stop_with_simulator,
        stop_with_system,
    ])
