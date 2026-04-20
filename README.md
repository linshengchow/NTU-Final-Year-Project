# MRCA Navigation

ROS 2 packages for deployment of the navigation stack on MRCA Hardware. 

## Launching Navigation Stack for MRCA

### 1. Launch all necessary drivers

```bash
cd ~/workspace/ws_fyp_docking/src/Navigation_fyp/setup
bash init.sh
```

This launches the IMU driver, LiDAR drivers for both LiDARs, LiDAR scan merger, LiDAR TF, camera driver, and the MRCA URDF.

### 2. Launch the navigation stack in a new terminal

```bash
cd ~/workspace/ws_fyp_docking
source install/setup.bash
ros2 launch mrca_navigation navigation.launch.py
```

## Testing Multifloor Navigation

### 1. Start the robot

Place the robot at any arbitrary location in B2 or B4 near the lift lobby.

### 2. Launch the navigation stack

Follow the steps in [Launching Navigation Stack for MRCA](#launching-navigation-stack-for-mrca).

### 3. Open two new terminals and source the workspace

In each terminal, run:

```bash
cd ~/workspace/ws_fyp_docking
source install/setup.bash
```

### 4. Run the multi-floor manager

The configuration file depends on the travel direction. The example below is for the B2 to B4 case.

In the first terminal, run:

```bash
ros2 run multi_floor_manager multi_floor_manager --ros-args --params-file ~/workspace/ws_fyp_docking/src/Navigation_fyp/src/scripts/multi_floor_manager/multi_floor_manager/config/map_changer_up_to_down.yaml
```

In the second terminal, run:

```bash
ros2 run multi_floor_manager execution_controller
```

The execution controller manages each stage of the multi-floor navigation task. When you are ready to continue to the next stage, type `y` in the execution controller terminal.

## Testing Docking 
### 1. Launch the navigation stack

Follow the steps in [Launching Navigation Stack for MRCA](#launching-navigation-stack-for-mrca). 

### 2. Pick a location to place the Apriltag

### 3. Ensure that the coordinates of the dock in the dock database more or less match the physical location of the Apriltag.

The dock database already contains a few different dock locations, and you may refer to the full report to replicate the physical placement of the Apriltag. 

### 4. Send a docking goal 
```bash
ros2 action send_goal /dock_robot opennav_docking_msgs/action/DockRobot "{
  use_dock_id: true,
  dock_id: 'home_dock',
  dock_type: 'MRCA_dock',
  max_staging_time: 1000.0,
  navigate_to_staging_pose: true, 
}" --feedback
```
### 5. Send an undocking goal (after successful docking)
```bash
ros2 action send_goal /undock_robot opennav_docking_msgs/action/UndockRobot "{dock_type: 'MRCA_dock', max_undocking_time: 30.0}"
```
