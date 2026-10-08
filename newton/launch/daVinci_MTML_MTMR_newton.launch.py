"""Run the JHU console with the Newton virtual patient cart and stereo display."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from dvrk_newton.python_runtime import resolve_newton_python
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, EmitEvent, ExecuteProcess, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


PACKAGE_NAME = "dvrk_config_jhu"


def generate_launch_description():
    newton_python = resolve_newton_python()
    package_share = Path(get_package_share_directory(PACKAGE_NAME))
    newton_share = Path(get_package_share_directory("dvrk_newton"))
    default_config = package_share / "newton" / "newton_patient_cart.yaml"
    system_config = package_share / "newton" / "system-MTMR-MTML-Newton-Teleop.json"
    display_config = package_share / "newton" / "stereo_display_simulator.json"
    cart_scene = package_share / "newton" / "ECM_PSM1_PSM2_PSM3.yaml"

    simulator = ExecuteProcess(
        cmd=[
            LaunchConfiguration("newton_python"),
            str(newton_share / "scripts" / "simulator.py"),
            "--config", LaunchConfiguration("newton_config"),
            "--scene", LaunchConfiguration("cart_scene"),
            "--scene", LaunchConfiguration("exercise"),
            "--headless", LaunchConfiguration("headless"),
        ],
        output="screen",
    )
    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        output="screen",
        cwd=str(package_share.parent / "jhu-daVinci"),
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
            on_exit=[EmitEvent(event=Shutdown(reason="NVIDIA Newton simulator exited"))],
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
            description="Newton patient-cart scene YAML file.",
        ),
        DeclareLaunchArgument(
            "headless", default_value="true",
            description="Run Newton without its desktop viewer window.",
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
            "newton_config", default_value=str(default_config),
            description="Newton runtime YAML configuration.",
        ),
        DeclareLaunchArgument(
            "newton_python",
            default_value=str(newton_python.path),
            description="Python interpreter selected by dvrk_newton's runtime resolver.",
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
