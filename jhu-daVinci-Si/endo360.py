#!/usr/bin/env python

# Author: Anton Deguet
# Date: 2015-02-22

# (C) Copyright 2015-2025 Johns Hopkins University (JHU), All Rights Reserved.

# --- begin cisst license - do not edit ---

# This software is provided "as is" under an open source license, with
# no warranty.  The complete license can be found in license.txt and
# http://www.cisst.org/cisst/license.txt.

# --- end cisst license ---

# Start a single arm using
# > rosrun dvrk_robot dvrk_system -j <system-file>
# Run test script:
# > rosrun dvrk_python dvrk_arm_test.py -a <arm-name>

import argparse
import crtk
import dvrk
import math
import numpy
import sys
import time

# example of application using arm.py
class example_application:
    def __init__(self, ral, arm_name):
        print('> configuring dvrk_psm_test for {}'.format(arm_name))
        self.ral = ral
        self.arm = dvrk.psm(ral = ral,
                            arm_name = arm_name)

    # main method
    def run(self):
        self.ral.check_connections()
        time.sleep(1)

        done = False

        jp, _ = self.arm.jaw.setpoint_jp()
        goal = numpy.copy(jp)

        # self.arm.move_jp(goal).wait()

        range = 265
        rest = 20
        center = 7
        grab = (center - range / 2.0) * math.pi / 180.0
        start = grab + (rest * math.pi / 180.0)
        end = (center + range / 2.0) * math.pi / 180.0
        while not done:
            i = input('Press "q", "1" or "2" and [enter] to continue\n')
            if i == 'q':
                done = True
            elif i == '1':
                print("half drive")
                goal[0] = grab
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = end
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = start
                self.arm.jaw.move_jp(goal).wait()
            elif i == '2':
                print("full drive")
                goal[0] = grab
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = end
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = grab
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = end
                self.arm.jaw.move_jp(goal).wait()
                goal[0] = start
                self.arm.jaw.move_jp(goal).wait()


if __name__ == '__main__':
    # strip ros arguments
    argv = crtk.ral.parse_argv(sys.argv[1:]) # skip argv[0], script name

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--arm', type=str, required=True,
                        choices=['PSM1', 'PSM2', 'PSM3'],
                        help = 'arm name corresponding to ROS topics without namespace.  Use __ns:= to specify the namespace')
    args = parser.parse_args(argv)

    ral = crtk.ral('dvrk_psm_test')
    application = example_application(ral, args.arm)
    ral.spin_and_execute(application.run)
