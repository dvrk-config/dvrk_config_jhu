"""Run the Si cart with two Omega.7 masters, PCsensor pedals, and SDI video."""

from pathlib import Path

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import TimerAction
from launch_ros.actions import Node


def generate_launch_description():
    config_relative = Path("jhu-daVinci-Si") / "two_force_dimensions"
    package_share = Path(get_package_share_directory("dvrk_config_jhu"))
    config_dir = package_share.parent / config_relative
    if not (config_dir / "system-daVinciSi-ForceDimension.json").is_file():
        config_dir = Path(__file__).resolve().parent.parent / config_relative

    def config(name):
        return str(config_dir / name)

    return LaunchDescription([
        Node(
            package="dvrk_robot",
            executable="dvrk_system",
            output="screen",
            # RobotIO resolves potentiometer lookup tables from the working directory.
            cwd=str(config_dir.parent),
            arguments=["-j", config("system-daVinciSi-ForceDimension.json")],
        ),
        Node(
            package="dvrk_data",
            executable="stereo_source",
            output="screen",
            arguments=["-c", config("stereo_source.json")],
        ),
        TimerAction(period=2.0, actions=[
            Node(
                package="dvrk_data",
                executable="stereo_alignment",
                output="screen",
                arguments=[
                    "-c", config("stereo_alignment.json"),
                    "--color-adjustment", config("stereo_color_adjustment.json"),
                ],
            ),
        ]),
        TimerAction(period=4.0, actions=[
            Node(
                package="dvrk_console",
                executable="control_panel",
                output="screen",
                arguments=["-c", config("control_panel.json")],
            ),
        ]),
    ])
