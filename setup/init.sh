# source HIPNUC 9 DOF IMU ROS 2 package workspace
echo "setting up IMU workspace ..."
source ~/workspace/ws_hipnuc/install/setup.bash

# source Pacecat 2D lidar workspace
echo "setting up 2D lidar ROS 2 package workspace ..."
source ~/workspace/ws_bluesea2/install/setup.bash

# source ira laser tools - multi merger package workspace
echo "setting up laser scan merger workspace ..."
source ~/workspace/ws_ira_laser_tools_nakai/install/setup.bash 

# source Orbbec camera workspace and MRCA robot description workspace
echo "setting up Orbbec camera and MRCA robot description workspace ..."
source ~/workspace/ws_fyp_docking/install/setup.bash

# launch all drivers 
echo "launching drivers ..."
ros2 launch ~/workspace/ws_fyp_docking/src/Navigation_fyp/setup/init.launch.py