# MRCA Navigation

ROS 2 packages for the MRCA deployment and navigation stack.

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
