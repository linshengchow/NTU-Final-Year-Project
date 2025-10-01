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
    robot_name = "sam_bot_description.urdf" 
    # robot_name = "mrca_v1_description.urdf.xacro"
    robot_description_dir = get_package_share_directory('simulation') #for sambot
    # robot_description_dir = get_package_share_directory('mrca_description') #for mrca_v1
    world = os.path.join(get_package_share_directory('simulation'), 'worlds', world_file_name)
    robot = os.path.join(robot_description_dir, 'src','description',robot_name ) #for sambot
    # robot = os.path.join(robot_description_dir, 'urdf','v1',robot_name )
    default_rviz_config_path = os.path.join(robot_description_dir, 'rviz', 'config.rviz')
    # robot_urdf = xacro.process(robot_xacro)

    gazebo_ros = get_package_share_directory('gazebo_ros')
    gazebo_client = launch.actions.IncludeLaunchDescription(
	launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzclient.launch.py')),
        condition=launch.conditions.IfCondition(launch.substitutions.LaunchConfiguration('gui'))
     )
    gazebo_server = launch.actions.IncludeLaunchDescription(
        launch.launch_description_sources.PythonLaunchDescriptionSource(
            os.path.join(gazebo_ros, 'launch', 'gzserver.launch.py'))
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )
    
    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        arguments=[robot], #Add this line
    )
    
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'sam_bot', '-topic', 'robot_description','-x', '0', '-y', '0.5', '-z', '0.1'],
        output='screen',
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    
    robot_localization_node = Node(
    package='robot_localization',
    executable='ekf_node',
    name='ekf_node',
    output='screen',
    parameters=[os.path.join(robot_description_dir, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
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
        DeclareLaunchArgument
            (name='use_sim_time', 
            default_value='True',
            description='Flag to enable use_sim_time'
        ),
        DeclareLaunchArgument(
            name='model', 
            default_value=robot, 
            description='Absolute path to robot model file'
        ),
        DeclareLaunchArgument(
            name='rvizconfig', 
            default_value=default_rviz_config_path, 
            description='Absolute path to rviz config file'
            ),
        gazebo_server,
        gazebo_client,
        joint_state_publisher_node,
        robot_state_publisher_node,
        spawn_entity,
        robot_localization_node,
        rviz_node,
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()
