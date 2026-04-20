import os
import sys
import xacro

import launch
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    imu_dir = get_package_share_directory('hipnuc_imu') 
    robot_description_dir = get_package_share_directory('mrca_description')
    scan_merger_dir = get_package_share_directory('ira_laser_tools')
    camera_dir = get_package_share_directory('orbbec_camera')

    robot_description  = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(robot_description_dir, 'launch', 'description_launch.py')
        )
    )

    imu = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(imu_dir, 'launch', 'imu_spec_msg.launch.py')
        )
    )

    lidar_back_right = launch.actions.ExecuteProcess(
        cmd=['ros2', 'launch', 'bluesea2', 'udp_laser_back_right.launch'],
        output='screen'
    )

    tf_lidar_back_right = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_lidar_back_right',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--yaw', '0', '--pitch', '0', '--roll', '0',
            '--frame-id', 'back_right_2d_lidar_optical_link',
            '--child-frame-id', 'laser_back_right'
        ]
    )

    lidar_front_left = launch.actions.ExecuteProcess(
        cmd=['ros2', 'launch', 'bluesea2', 'udp_laser_front_left.launch'],
        output='screen'
    )

    tf_lidar_front_left = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_lidar_front_left',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--yaw', '0', '--pitch', '0', '--roll', '0',
            '--frame-id', 'front_left_2d_lidar_optical_link',
            '--child-frame-id', 'laser_front_left'
        ]
    )

    scan_merger = launch.actions.ExecuteProcess(
        cmd=['ros2', 'launch', 'ira_laser_tools', 'laserscan_multi_merger.launch'],
        output='screen'
    )

    camera  = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(camera_dir, 'launch', 'gemini2.launch.py')
        )
    )
  
    
    ld = launch.LaunchDescription([
        SetEnvironmentVariable('RCUTILS_LOGGING_SEVERITY_THRESHOLD','ERROR'),
        imu,
        lidar_back_right,   
        tf_lidar_back_right,
        robot_description,
        lidar_front_left,
        tf_lidar_front_left,
        scan_merger,
        camera,

        ])
    return ld


if __name__ == '__main__':
    generate_launch_description()