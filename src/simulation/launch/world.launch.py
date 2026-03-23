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
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    world_file_name = "tb3_charging.world"
    robot_name = "turtlebot3_waffle" 
    
    simulation_dir = get_package_share_directory('simulation') 
    robot_description_dir = get_package_share_directory('turtlebot3_gazebo') 
    world_dir = get_package_share_directory('simulation') 
    map_dir = get_package_share_directory('simulation') 
    config_dir = get_package_share_directory('simulation') 
    
    world = os.path.join(world_dir, 'worlds', world_file_name)
    robot = os.path.join(robot_description_dir,'models',robot_name, 'model.sdf')
    default_rviz_config_path = os.path.join(simulation_dir, 'rviz', 'config.rviz')
    map = os.path.join( map_dir,'maps','charging_map2.yaml')
    nav2_params = os.path.join(config_dir,'config','nav2_params.yaml')
    docking_server_params = os.path.join(config_dir,'config','docking_server_params.yaml') #not used for now, can consider making docking params separate from nav2 params

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
        arguments=['-entity', 'turtlebot3_waffle', '-topic', 'robot_description','-x', '0.5', '-y', '2', '-z', '0'],
        output='screen',
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[os.path.join(simulation_dir, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    laser_odometry = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('rf2o_laser_odometry'), 'launch', 'rf2o_laser_odometry.launch.py')
        )
    )
    
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )
    
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map}, {'use_sim_time': True}]
    )
    
    nav2_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('nav2_bringup'),'launch','bringup_launch.py')
            ),
            launch_arguments={
                'map': map,
                'use_sim_time': 'true',
                'params_file': nav2_params}.items(),
    )
    
    apriltag_detection_pipeline = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(simulation_dir, 'launch', 'april_tag_detection_pipeline.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'image': '/camera/image_raw',
            'camera_info': '/camera/camera_info',
            'image_rect': '/camera/image_rect',
            'parent_frame': 'camera_rgb_optical_frame'}.items()
    )
    
    docking_server = Node(
        package='opennav_docking',
        executable='opennav_docking',
        name='docking_server',
        output='screen',
        parameters=[nav2_params,
                    {'use_sim_time': True}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_docking',
        output='screen',
        parameters=[{'autostart': True}, {'node_names': ['docking_server']}],
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
        laser_odometry,
        rviz_node,
        #map_server_node,
        #slam_launch,
        nav2_launch,
        apriltag_detection_pipeline,
        docking_server,
        lifecycle_manager,
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()
