import os
from ament_index_python.packages import get_package_share_directory

import launch
from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    config_dir = get_package_share_directory('mrca_navigation') 
    
    apriltag_ros_params =  os.path.join(config_dir,'config','apriltag_ros_params.yaml')

    
    rectify_node = Node(
        package='image_proc',
        executable='rectify_node',
        name='rectify_node',
        remappings=[
            ('image', LaunchConfiguration('image')),
            ('image_rect',LaunchConfiguration('image_rect')),
            ('camera_info', LaunchConfiguration('camera_info')), 
        ],
        parameters=[{
            'queue_size': 5,
            'interpolation': 1,
            'use_sim_time': LaunchConfiguration('use_sim_time'),
            'image_transport': 'raw'
        }],
    )
    
    apriltag_tracker_node = ComposableNode(
        package ='apriltag_ros',
        plugin = 'AprilTagNode',
        name ='apriltag',
        remappings=[
            ('image_rect', LaunchConfiguration('image_rect')),
            ('camera_info', LaunchConfiguration('camera_info'))
        ],
        parameters=[apriltag_ros_params,{'use_sim_time':LaunchConfiguration('use_sim_time') }],
        extra_arguments=[
            {'use_intra_process_comms':True}
        ]
    )
    
    apriltag_tracker_container = ComposableNodeContainer(
        package='rclcpp_components',
        name='apriltag_container',
        namespace='',
        executable='component_container_mt',
        composable_node_descriptions=[
            apriltag_tracker_node,
        ],
        output='screen'
    )
    
    detected_dock_pose = Node(
        package='mrca_navigation',
        executable= 'detected_dock_pose_publisher_node', 
        name = 'detected_dock_pose_node',
        parameters=[{
            'parent_frame': LaunchConfiguration('parent_frame'),
            'child_frame': LaunchConfiguration('child_frame'),
            'publish_rate': 10.0,
        }],
    )

    
    ld = launch.LaunchDescription([
        DeclareLaunchArgument
            (name='use_sim_time', 
            default_value='True',
            description='Flag to enable use_sim_time'
        ),
        DeclareLaunchArgument(
            name='image',
            default_value='/camera/image_raw', 
            description='Raw image topic'),
        DeclareLaunchArgument(
            name='image_rect',
            default_value='/camera/image_rect', 
            description='Rectified image topic'),
        DeclareLaunchArgument(
            name='camera_info',
            default_value='/camera/camera_info', 
            description='Camera info topic'),
        DeclareLaunchArgument(
            name='parent_frame',
            default_value='camera_rgb_optical_frame', 
            description='Parent frame of tf'),
        DeclareLaunchArgument(
            name='child_frame',
            default_value='tag36h11:0', 
            description='Child frame of tf'),
        rectify_node,
        apriltag_tracker_container,
        detected_dock_pose,
        
    ])
    return ld


if __name__ == '__main__':
    generate_launch_description()