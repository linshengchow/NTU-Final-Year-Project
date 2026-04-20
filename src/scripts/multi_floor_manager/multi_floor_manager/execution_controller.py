import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from nav2_msgs.srv import LoadMap
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseWithCovarianceStamped, PoseStamped
from nav_msgs.msg import Odometry

import time
import math

class ExecutionController(Node):
    def __init__(self):
        super().__init__('execution_controller')
        self.publisher = self.create_publisher(String, '/execute', 10)
        
    def send_message(self, msg):
        message = String()
        message.data = msg
        self.publisher.publish(message)
        self.get_logger().info(f'Published: {msg}')
        
def main():
    rclpy.init()
    execution_controller = ExecutionController()
    
    proceed_flag = ' '
    while proceed_flag.lower() != 'n':
        proceed_flag = input("Type 'y' to continue execution or 'n' to terminate: ")
        if proceed_flag.lower() == 'y': 
            execution_controller.send_message('continue')
            proceed_flag = ' '
        elif proceed_flag.lower() == 'n':
            execution_controller.send_message('terminate')
            break
        else:
            print("Invalid input. Please type 'y' to continue or 'n' to terminate.")
    execution_controller.destroy_node()
    rclpy.shutdown()
        
if __name__ == '__main__':
    main()