# Copyright (c) 2024 Nanyang Technological University, 
# Rehabilitation Research Institute of Singapore (RRIS)
# All Rights Reserved.

# NOTICE: All information contained herein is, and remains the property of
# Rehabilitation Research Institute of Singapore. The intellectual and technical
# concepts contained herein are proprietary to Rehabilitation Research Institute
# of Singapore and may be covered by Singapore and Foreign Patents, patents in
# process, and are protected by trade secret or copyright law. Dissemination of
# this information or reproduction of this material is strictly forbidden unless
# prior written permission is obtained from Rehabilitation Research Institute of
# Singapore. Access to the source code contained herein is hereby forbidden to
# anyone except current Rehabilitation Research Institute of Singapore employees,
# managers or contractors who have executed Confidentiality and Non-disclosure
# agreements explicitly covering such access.

# The copyright notice above does not evidence any actual or intended publication
# or disclosure of this source code, which includes information that is
# confidential and/or proprietary, and is a trade secret, of Rehabilitation
# Research Institute of Singapore. ANY REPRODUCTION, MODIFICATION, DISTRIBUTION,
# PUBLIC PERFORMANCE, OR PUBLIC DISPLAY OF OR THROUGH USE OF THIS SOURCE CODE
# WITHOUT THE EXPRESS WRITTEN CONSENT OF COMPANY IS STRICTLY PROHIBITED, AND IN
# VIOLATION OF APPLICABLE LAWS AND INTERNATIONAL TREATIES. THE RECEIPT OR
# POSSESSION OF THIS SOURCE CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR
# IMPLY ANY RIGHTS TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO
# MANUFACTURE, USE, OR SELL ANYTHING THAT IT MAY DESCRIBE, IN WHOLE OR IN PART.
#
# Author: scy
# - Publish robot state (static joints) and joint state (moving joints)

import os
import xacro

from ament_index_python.packages import get_package_share_directory

from launch_ros.actions import Node
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    # Build URDF via xacro
    # Load the URDF into a parameter
    robot_description_dir = get_package_share_directory('mrca_description')
    xacro_path = os.path.join(robot_description_dir, 'urdf/v1', 'mrca_v1_description.urdf.xacro')
    urdf = xacro.process(xacro_path)

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',
            description='Use simulation time'
        ),

        # Robot state publisher
        Node(
            name='robot_state_publisher',
            package="robot_state_publisher",
            executable="robot_state_publisher",
            output='both',
            parameters=[{'robot_description': urdf},
                        {'publish_frequency': 30.0}],
            # arguments=['--ros-args', '--log-level', 'error'],
        ),

        # Joint state publisher
        Node(
            name='joint_state_publisher',
            package='joint_state_publisher',
            executable='joint_state_publisher',
            output='log',
            parameters=[{'rate': 30.0}],
            arguments=['--ros-args', '--log-level', 'error'],
        ),
    ])
