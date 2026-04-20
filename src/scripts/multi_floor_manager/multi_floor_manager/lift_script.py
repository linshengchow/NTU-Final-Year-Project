import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from rclpy.action import ActionClient
from rclpy.duration import Duration

from nav2_msgs.srv import LoadMap
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from opennav_docking_msgs.action import DockRobot
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import Odometry

import time
import math
from enum import Enum, auto

class State(Enum):
    WAITING_FOR_NAVIGATE_TO_POSE = auto()
    WAITING_TO_ENTER_LIFT = auto()
    WAITING_FOR_MAP_CHANGE = auto()
    WAITING_TO_SET_INITIAL_POSE = auto()
    WAITING_TO_DOCK = auto()
    WAITING_TO_EXIT_LIFT = auto()
    DOCKING_COMPLETED = auto()
    DONE = auto()
    
class MultiFloorManager(Node):
    def __init__(self):
        super().__init__('multi_floor_manager')
        self.declare_parameter('map_url', '/home/mrca/workspace/ws_fyp_docking/src/Navigation_fyp/src/mrca_navigation/maps/b4_map.yaml')
        self.declare_parameter('lift_entry_staging_pose', [0.0, -1.7, 3.14159])
        self.declare_parameter('lift_pose', [-1.0, -1.7, 3.14159])
        self.declare_parameter('new_map_initial_pose', [0.5, 2.0, 0.0])
        self.declare_parameter('lift_exit_pose', [0.0, 0.0, 0.0])
        self.declare_parameter('docking_dock_id', 'home_dock')
        self.declare_parameter('docking_dock_type', 'MRCA_dock')
        self.declare_parameter('docking_max_staging_time', 1000.0)
        self.declare_parameter('docking_navigate_to_staging_pose', True)
        
        self.map_url = self.get_parameter('map_url').get_parameter_value().string_value
        self.lift_entry_staging_pose = self.get_parameter('lift_entry_staging_pose').get_parameter_value().double_array_value
        self.lift_pose = self.get_parameter('lift_pose').get_parameter_value().double_array_value
        self.new_map_initial_pose = self.get_parameter('new_map_initial_pose').get_parameter_value().double_array_value
        self.lift_exit_pose = self.get_parameter('lift_exit_pose').get_parameter_value().double_array_value
        self.docking_dock_id = self.get_parameter('docking_dock_id').get_parameter_value().string_value
        self.docking_dock_type = self.get_parameter('docking_dock_type').get_parameter_value().string_value
        self.docking_max_staging_time = self.get_parameter('docking_max_staging_time').get_parameter_value().double_value
        self.docking_navigate_to_staging_pose = self.get_parameter('docking_navigate_to_staging_pose').get_parameter_value().bool_value

        # Initialize the LoadMap service client
        self.client = self.create_client(LoadMap, '/map_server/load_map')
        while not self.client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Load map service not available, waiting again...')
        self.request = LoadMap.Request()
        
        # Subscribe to the execution control topic
        self.proceed_flag_subsriber = self.create_subscription(String, '/execute', self.subscriber_callback, 10)
        self.proceed_flag = ' '
        self.state = State.WAITING_FOR_NAVIGATE_TO_POSE
        print("MultiFloorManager initialized, waiting for navigate to pose...")
        
        # Initialize the BasicNavigator
        self.basic_navigator = BasicNavigator()
        self.basic_navigator.waitUntilNav2Active()
    
        # Initialise SetParameters service client 
        self.set_parameters_client = self.create_client(SetParameters, '/controller_server/set_parameters')
        while not self.set_parameters_client.wait_for_service(timeout_sec=2.0):
            self.get_logger().info('Set parameters service not available, waiting again...')
        self.set_parameters_request = SetParameters.Request()
        
        # Initialise docking client 
        self.docking_client = ActionClient(self, DockRobot, '/dock_robot')
        self.docking_client.wait_for_server()
        
    def send_change_map_request(self, map_url):
        self.request.map_url = map_url
        future = self.client.call_async(self.request)
        rclpy.spin_until_future_complete(self, future)
        map_change_response = future.result()
        if map_change_response.result == 0:
            self.get_logger().info('Map change successful')
        elif map_change_response.result == 1:
            self.get_logger().error('Map does not exist')
        elif map_change_response.result == 2:
            self.get_logger().error('Invalid map data')
        elif map_change_response.result == 3:
            self.get_logger().error('Invalid map metadata')
        elif map_change_response.result == 255:
            self.get_logger().error('Undefined failure')
    
    def subscriber_callback(self,msg): 
        self.proceed_flag = msg.data
        self.get_logger().info(f'Received: {self.proceed_flag}') 
        
    def set_initial_pose(self, coordinate_array):
        x = coordinate_array[0]
        y = coordinate_array[1]
        theta = coordinate_array[2]
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.basic_navigator.get_clock().now().to_msg()
        initial_pose.pose.position.x = x
        initial_pose.pose.position.y = y
        initial_pose.pose.orientation.w = math.cos(theta / 2.0)
        initial_pose.pose.orientation.z = math.sin(theta / 2.0)
        self.basic_navigator.setInitialPose(initial_pose)
        
    def navigate_to_pose(self, coordinate_array):
        x = coordinate_array[0]
        y = coordinate_array[1]
        theta = coordinate_array[2]
        goal_pose = PoseStamped()
        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.basic_navigator.get_clock().now().to_msg()
        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.orientation.w = math.cos(theta / 2.0)
        goal_pose.pose.orientation.z = math.sin(theta / 2.0)
        
        self.basic_navigator.goToPose(goal_pose)
        i = 0
        while not self.basic_navigator.isTaskComplete():
            i = i + 1
            feedback = self.basic_navigator.getFeedback()
            if feedback and i % 5 == 0:
                print('Estimated time of arrival: ' + '{0:.0f}'.format(
                    Duration.from_msg(feedback.estimated_time_remaining).nanoseconds / 1e9)
                    + ' seconds.')
                    
        result = self.basic_navigator.getResult()
        if result == TaskResult.SUCCEEDED:
            print('Goal succeeded!')
        elif result == TaskResult.CANCELED:
            print('Goal was canceled!')
        elif result == TaskResult.FAILED:
            print('Goal failed!')
        else:
            print('Goal has an invalid return status!')
            
    def send_set_parameters_request(self, min_vel_x):
        param = Parameter()
        param.name = 'FollowPath.min_vel_x'
        param.value = ParameterValue()
        param.value.type = ParameterType.PARAMETER_DOUBLE
        param.value.double_value = min_vel_x
        
        self.set_parameters_request.parameters = [param]
        
        future = self.set_parameters_client.call_async(self.set_parameters_request)
        rclpy.spin_until_future_complete(self, future)
        response = future.result()
        if response.results[0].successful:
            self.get_logger().info(f'min_vel_x successfully set to {min_vel_x}')
        else:
            self.get_logger().error(f'Failed to set min_vel_x: {response.results[0].reason}')

    def send_docking_goal(self,dock_id, dock_type, max_staging_time, navigate_to_staging_pose: bool):
        docking_goal_message = DockRobot.Goal()
        docking_goal_message.use_dock_id = True
        docking_goal_message.dock_id = dock_id
        docking_goal_message.dock_type = dock_type
        docking_goal_message.max_staging_time = max_staging_time
        docking_goal_message.navigate_to_staging_pose = navigate_to_staging_pose
        
        self.get_logger().info(f'Sending docking goal to dock: {docking_goal_message.dock_id} of type: {docking_goal_message.dock_type}')
        self.docking_goal_future = self.docking_client.send_goal_async(docking_goal_message, feedback_callback=self.docking_feedback_callback)
        
        self.docking_goal_future.add_done_callback(self.docking_goal_response_callback)
        
    def docking_goal_response_callback(self, future):
        docking_goal_handle = future.result()
        if not docking_goal_handle.accepted:
            self.get_logger().info('Docking goal rejected')
            return      
        
        self.get_logger().info('Docking goal accepted')
        self._get_result_future = docking_goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_docking_result_callback)
        
    def docking_feedback_callback(self, feedback_msg):
        feedback_msg = feedback_msg.feedback
        if feedback_msg.state == 1:
            self.get_logger().info('Docking state: Navigating to staging pose')
        elif feedback_msg.state == 2:
            self.get_logger().info('Docking state: Initial perception')
        elif feedback_msg.state == 3:   
            self.get_logger().info('Docking state: Controlling')
        elif feedback_msg.state == 4:
            self.get_logger().info('Docking state: Waiting to charge')
        elif feedback_msg.state == 5:
            self.get_logger().info('Docking state: Retrying')
            
    def get_docking_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Docking succeeded!')
            self.state = State.DONE
        else:
            self.get_logger().error(f'Docking failed with error code: {result.error_code}')
         
    def handle_transition(self):
        if self.proceed_flag.lower() == 'terminate':
            self.state = State.DOCKING_COMPLETED
            return
            
        if self.proceed_flag.lower() != 'continue':
            return
            
        if self.state == State.WAITING_FOR_NAVIGATE_TO_POSE:
            self.navigate_to_pose(self.lift_entry_staging_pose)
            
            self.proceed_flag = ' '
            self.state = State.WAITING_TO_ENTER_LIFT
            print("Waiting to enter lift...")
            
        elif self.state == State.WAITING_TO_ENTER_LIFT:
            self.navigate_to_pose(self.lift_pose)
            
            self.proceed_flag = ' '            
            self.state = State.WAITING_FOR_MAP_CHANGE
            print("Waiting for map change...")
            
        elif self.state == State.WAITING_FOR_MAP_CHANGE:
            self.send_change_map_request(self.map_url)
            self.proceed_flag = ' '
            self.state = State.WAITING_TO_SET_INITIAL_POSE
            print("Waiting to set initial pose...")
            
        elif self.state == State.WAITING_TO_SET_INITIAL_POSE:
            self.set_initial_pose(self.new_map_initial_pose)
            self.get_logger().info('Initial pose set')
            self.proceed_flag = ' '
            self.state = State.WAITING_TO_EXIT_LIFT
            self.send_set_parameters_request(-0.5)
            print("Waiting to exit lift...")

        elif self.state == State.WAITING_TO_EXIT_LIFT:
            self.navigate_to_pose(self.lift_exit_pose)
            self.send_set_parameters_request(0.0)
            
            self.proceed_flag = ' '
            self.state = State.WAITING_TO_DOCK
            print("Waiting to dock...")
            
        elif self.state == State.WAITING_TO_DOCK:
            self.send_docking_goal(
                dock_id=self.docking_dock_id,
                dock_type=self.docking_dock_type,
                max_staging_time=self.docking_max_staging_time,
                navigate_to_staging_pose=self.docking_navigate_to_staging_pose
            )
            self.proceed_flag = ' '
            
        elif self.state == State.DOCKING_COMPLETED:
            print("Docking completed, execution finished.")
            self.state = State.DONE
    
def main():
    rclpy.init()
    multi_floor_manager = MultiFloorManager()
    
    while rclpy.ok() and multi_floor_manager.state != State.DONE:

        rclpy.spin_once(multi_floor_manager)
        
        multi_floor_manager.handle_transition()
        
    multi_floor_manager.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
        