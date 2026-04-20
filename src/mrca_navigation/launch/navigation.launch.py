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
    mrca_navigation_dir = get_package_share_directory('mrca_navigation') 
    map_dir = get_package_share_directory('mrca_navigation') 
    config_dir = get_package_share_directory('mrca_navigation') 
    
    default_rviz_config_path = os.path.join(mrca_navigation_dir, 'rviz', 'config.rviz')
    map = os.path.join( map_dir,'maps','lab_map2.yaml')
    nav2_params = os.path.join(config_dir,'config','nav2_params.yaml')
    slam_toolbox_params = os.path.join(config_dir,'config','slam_toolbox_params.yaml')

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )
    
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}],
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    
    robot_localization_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_node',
        output='screen',
        parameters=[os.path.join(mrca_navigation_dir, 'config/ekf.yaml'), {'use_sim_time': LaunchConfiguration('use_sim_time')}]
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
        launch_arguments={
            'slam_params_file': slam_toolbox_params,
            'use_sim_time': LaunchConfiguration('use_sim_time')}.items()
    )
    
    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{'yaml_filename': map}, {'use_sim_time': LaunchConfiguration('use_sim_time')}]
    )
    
    nav2_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('nav2_bringup'),'launch','bringup_launch.py')
            ),
            launch_arguments={
                'map': map,
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'params_file': nav2_params}.items(),
    )
    
    apriltag_detection_pipeline = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(mrca_navigation_dir, 'launch', 'april_tag_detection_pipeline.launch.py')
        ),
        launch_arguments={
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'image': '/camera/color/image_raw',
            'camera_info': '/camera/color/camera_info',
            'image_rect': '/camera/color/image_rect',
            'parent_frame': 'camera_color_optical_frame'}.items()
    )
    
    docking_server = Node(
        package='opennav_docking',
        executable='opennav_docking',
        name='docking_server',
        output='screen',
        parameters=[nav2_params,
                    {'use_sim_time': LaunchConfiguration('use_sim_time')}],
    )

    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_docking',
        output='screen',
        parameters=[{'autostart': True}, {'node_names': ['docking_server']}],
    )
    
    ld = launch.LaunchDescription([
        DeclareLaunchArgument
            (name='use_sim_time', 
            default_value='False',
            description='Flag to enable use_sim_time'
        ),
        DeclareLaunchArgument(
            name='rvizconfig', 
            default_value=default_rviz_config_path, 
            description='Absolute path to rviz config file'
            ),
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
