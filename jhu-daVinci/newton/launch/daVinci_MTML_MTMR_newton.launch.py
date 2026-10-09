"""Run the jhu-daVinci console with the newton patient cart."""

from dvrk_simulator_base.launch import jhu_launch


def generate_launch_description():
    return jhu_launch("jhu-daVinci", "newton")
