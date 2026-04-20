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
# - Visualize MRCA robot model in rviz2 with robot state (static joints) and
#   joint state (moving joints)

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare('mrca_visualization'), 'rviz', 'model.rviz']
    )

    node_mrca_description = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('mrca_description'), 'launch/description_launch.py')
        )
    )

    return LaunchDescription([
        node_mrca_description,

        # rviz2
        Node(
            name='rviz',
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config_file], output='screen'
        ),
    ])
