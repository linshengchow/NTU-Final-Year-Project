# MRCA Navigation

ROS 2 packages for simulation of the navigation stack. For hardware deployment, please use the ```hardware_testing``` branch.  

## Launching Navigation Stack for Simulated Robot (Turtlebot3 Waffle) 

### 1. Launch the navigation stack in a new terminal

```bash
cd ~/Navigation_fyp
source install/setup.bash
ros2 launch simulation view_world.launch.py
```

## Testing Docking 
### 1. Launch the navigation stack

Follow the steps in [Launching Navigation Stack for Simulated Robot](#launching-navigation-stack-for-mrca). 

### 2. Pick a location to place the dock

The dock location can be modified by editing the world file (```tb3_charging.world```). If you do not intend to make any modifications, skip this step and the following step.  

### 3. Ensure that the coordinates of the dock in the dock database (in ```nav2_params.yaml```) match those that were used in the world file.

### 4. Send a docking goal 
```bash
ros2 action send_goal /dock_robot opennav_docking_msgs/action/DockRobot "{
  use_dock_id: true,
  dock_id: 'home_dock',
  dock_type: 'turtlebot_dock',
  max_staging_time: 1000.0,
  navigate_to_staging_pose: true, 
}" --feedback
```
### 5. Send an undocking goal (after successful docking)
```bash
ros2 action send_goal /undock_robot opennav_docking_msgs/action/UndockRobot "{dock_type: 'turtlebot_dock', max_undocking_time: 30.0}"
```
