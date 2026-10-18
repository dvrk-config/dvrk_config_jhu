"""Run the OpenXR console with the real JHU daVinci Si patient cart."""

from pathlib import Path
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _launch_setup(context):
    jhu_share = Path(get_package_share_directory("dvrk_config_jhu"))
    openxr_dir = jhu_share.parent / "jhu-daVinci-Si" / "open-xr"
    if not openxr_dir.is_dir():
        openxr_dir = Path(__file__).resolve().parent.parent / "jhu-daVinci-Si" / "open-xr"

    system_config = openxr_dir / "system-OpenXR-daVinciSi.json"
    if not system_config.is_file():
        system_config = openxr_dir / "system-SUJ-ECM-PSM1-PSM2-PSM3-OpenXR-Teleop.json"

    video_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            str(Path(get_package_share_directory("dvrk_console")) / "launch" / "stereo_video_pipeline.launch.py")
        ),
        launch_arguments={"config_dir": str(openxr_dir)}.items(),
        condition=IfCondition(LaunchConfiguration("video")),
    )

    dvrk_system = Node(
        package="dvrk_robot",
        executable="dvrk_system",
        output="screen",
        cwd=str(openxr_dir),
        arguments=["--json-config", str(system_config)],
    )

    return [video_launch, dvrk_system]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("video", default_value="true", description="Start OpenXR stereo video pipeline"),
        OpaqueFunction(function=_launch_setup),
    ])
