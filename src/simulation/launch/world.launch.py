import os
import sys
import xacro

import launch
from launch.conditions import IfCondition
from launch.substitutions import PythonExpression
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node
from launch.substitutions import Command, LaunchConfiguration
from launch.actions import DeclareLaunchArgument, ExecuteProcess


def generate_launch_description():
    world_file_name = "simple_world.world"
    robot_description_dir = get_package_share_directory('mrca_description')
    world = os.path.join(get_package_share_directory('simulation'), 'worlds', world_file_name)
    robot = os.path.join(robot_description_dir, 'urdf/v1', 'mrca_v1_description.urdf.xacro')
    # robot_urdf = xacro.process(robot_xacro)

    gazebo_ros = get_package_share_directory('gazebo_ros')
    gazebo_client = launch.actions.IncludeLaunchDescription(
	launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')),
        condition=launch.conditions.IfCondition(launch.substitutions.LaunchConfiguration('gui'))
     )
    gazebo_server = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'extra_gazebo_args': '--verbose -s libgazebo_ros_factory.so'
        }.items()
    )


    robot_state_publisher_node = Node(
        name='robot_state_publisher',
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output='both',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}, {'publish_frequency': 30.0}]
    )
    
    joint_state_publisher_node = Node(
        name='joint_state_publisher',
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='log',
        parameters=[{'rate': 30.0}],
        arguments=[robot], #Add this line
    )
    
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'mrca_v1', '-topic', 'robot_description','-x', '0', '-y', '5', '-z', '0.1'],
        output='screen',
    )
    
    ld = launch.LaunchDescription([
        DeclareLaunchArgument(
          'world',
          default_value=[world, ''],
          description='SDF world file'),
        DeclareLaunchArgument(
            name='gui',
            default_value='false'
        ),
        DeclareLaunchArgument(name='model', default_value=robot, description='Absolute path to robot model file'),
        gazebo_server,
        gazebo_client,
        joint_state_publisher_node,
        robot_state_publisher_node,
        spawn_entity,
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()
