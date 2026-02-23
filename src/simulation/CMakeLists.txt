 ################################################################################
# Set minimum required version of cmake, project name and compile options
################################################################################
cmake_minimum_required(VERSION 3.5)
project(simulation)

################################################################################
# Find ament packages and libraries for ament and system dependencies
################################################################################
find_package(ament_cmake REQUIRED)
find_package(gazebo_ros REQUIRED)
find_package(rf2o_laser_odometry REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(turtlebot3_gazebo REQUIRED)
find_package(opennav_docking REQUIRED)
find_package(opennav_docking_msgs REQUIRED)
find_package(opennav_docking_bt REQUIRED)
find_package(opennav_docking_core REQUIRED)


exec_program("python3 -m pip install -r ${CMAKE_CURRENT_SOURCE_DIR}/requirements.txt")
exec_program("python3 ${CMAKE_CURRENT_SOURCE_DIR}/fuel_utility.py download -m XRayMachine -m IVStand -m BloodPressureMonitor -m BPCart -m BMWCart -m CGMClassic -m StorageRack -m Chair -m InstrumentCart1 -m Scrubs -m PatientWheelChair -m WhiteChipChair -m TrolleyBed -m SurgicalTrolley -m PotatoChipChair -m VisitorKidSit -m FemaleVisitorSit -m AdjTable -m MopCart3 -m MaleVisitorSit -m Drawer -m OfficeChairBlack -m ElderLadyPatient -m ElderMalePatient -m InstrumentCart2 -m MetalCabinet -m BedTable -m BedsideTable -m AnesthesiaMachine -m TrolleyBedPatient -m Shower -m SurgicalTrolleyMed -m StorageRackCovered -m KitchenSink -m Toilet -m VendingMachine -m ParkingTrolleyMin -m PatientFSit -m MaleVisitorOnPhone -m FemaleVisitor -m MalePatientBed -m StorageRackCoverOpen -m ParkingTrolleyMax -d ${CMAKE_CURRENT_SOURCE_DIR}/fuel_models --verbose")

################################################################################
# Install
################################################################################

install(DIRECTORY launch models fuel_models worlds src config rviz maps
	DESTINATION share/${PROJECT_NAME}
)

ament_export_dependencies(ament_cmake)
ament_export_dependencies(gazebo_ros)
ament_export_dependencies(rclcpp)
ament_export_dependencies(geometry_msgs)
ament_export_dependencies(tf2)
ament_export_dependencies(tf2_ros)

################################################################################
# Macro for ament package
################################################################################
ament_package()

################################################################################
# Adding executables
################################################################################
add_executable(detected_dock_pose_publisher_node src/detected_dock_pose_publisher.cpp)
ament_target_dependencies(
detected_dock_pose_publisher_node
  rclcpp
  geometry_msgs
  tf2
  tf2_ros
)
install(TARGETS detected_dock_pose_publisher_node
  DESTINATION lib/${PROJECT_NAME}
)