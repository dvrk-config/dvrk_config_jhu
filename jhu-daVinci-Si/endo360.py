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


    def __init__(self, ral, IO_name, console_name, MTM_name, PSM_name):
        print('> configuring endo for {}'.format(PSM_name))
        self.ral = ral
        self.PSM = dvrk.psm(ral = ral,
                            arm_name = PSM_name)
        self.system = dvrk.system(ral = ral)
        self.console = dvrk.console(ral = ral,
                                    console_name = console_name)
        self.teleop_name = MTM_name + '_' + PSM_name
        self.ready = False
        self.running = False
        self.full_drive_trigger = False

        self.range = 265.0
        self.rest = 20.0
        self.center = 7.0
        self.grab = (self.center - self.range / 2.0) * math.pi / 180.0
        self.start = self.grab + (self.rest * math.pi / 180.0)
        self.end = (self.center + self.range / 2.0) * math.pi / 180.0

        self.coag = crtk.joystick_button(ral, 'IO/' + IO_name + '/coag', 0)
        self.coag.set_callback(self.coag_callback)
        self.clutch = crtk.joystick_button(ral, 'IO/' + IO_name + '/clutch', 0)
        self.clutch.set_callback(self.clutch_callback)


    def clutch_callback(self, value):
        self.update_state()


    def coag_callback(self, value):
        self.update_state()


    def update_state(self):
        print(f'clutch: {self.clutch.value()}, coag: {self.coag.value()}')
        if self.clutch.value() == 1 and self.coag.value() == 1:
            self.running = True


    def full_drive(self):
        ts = 0.0
        while ts == 0.0:
            jp, ts = self.PSM.jaw.setpoint_jp()
            print('.')
        goal = numpy.copy(jp)
        goal[0] = self.grab
        print('grab')
        self.PSM.jaw.move_jp(goal).wait()
        self.system.beep(0.2, 3000.0)
        goal[0] = self.end
        print('end')
        self.PSM.jaw.move_jp(goal).wait()
        self.system.beep(0.2, 3500.0)
        goal[0] = self.grab
        print('grab')
        self.PSM.jaw.move_jp(goal).wait()
        self.system.beep(0.2, 3000.0)
        goal[0] = self.end
        print('end')
        self.PSM.jaw.move_jp(goal).wait()
        self.system.beep(0.2, 3500.0)
        goal[0] = self.start
        print('start')
        self.PSM.jaw.move_jp(goal).wait()
        self.system.beep(0.5, 4000.0)


    def half_drive(self):
        ts = 0.0
        while ts == 0.0:
            jp, ts = self.PSM.jaw.setpoint_jp()
            print('.')
        goal = numpy.copy(jp)
        goal[0] = self.grab
        print('grab')
        self.PSM.jaw.move_jp(goal).wait()
        goal[0] = self.end
        print('end')
        self.PSM.jaw.move_jp(goal).wait()
        goal[0] = self.start
        print('start')
        self.PSM.jaw.move_jp(goal).wait()


    # main method
    def run(self):
        self.ral.check_connections()
        time.sleep(1)

        done = False

        while not done:
            time.sleep(0.001)

            if self.running:
                if self.console.teleop_is_selected(self.teleop_name):
                    self.console.teleop_unselect(self.teleop_name)
                    self.full_drive()
                    self.console.teleop_select(self.teleop_name)
                self.running = False


if __name__ == '__main__':
    # strip ros arguments
    argv = crtk.ral.parse_argv(sys.argv[1:]) # skip argv[0], script name

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--PSM', type = str, required = True,
                        choices = ['PSM1', 'PSM2', 'PSM3'],
                        help = 'PSM name corresponding to ROS topics without namespace.  Use __ns:= to specify the namespace')
    parser.add_argument('-m', '--MTM', type = str, required = True,
                        choices = ['MTML', 'MTMR'],
                        help = 'MTM name corresponding to ROS topics without namespace.  Use __ns:= to specify the namespace')
    parser.add_argument('-i', '--IO', type = str,
                        default = 'IO1', help = 'IO name')
    parser.add_argument('-c', '--console', type = str,
                        default = 'console', help = 'IO name')
    args = parser.parse_args(argv)

    ral = crtk.ral('dvrk_psm_test')
    application = example_application(ral, args.IO, args.console, args.MTM, args.PSM)
    ral.spin_and_execute(application.run)
