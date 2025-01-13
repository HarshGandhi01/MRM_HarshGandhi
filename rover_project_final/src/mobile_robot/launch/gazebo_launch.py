import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():

    # Robot and file parameters
    robotXacroname = 'rover'
    namePackage = 'mobile_robot'
    modelFileRelativePath = 'model/rover.xacro'
    worldFileRelativePath = 'model/world.world'

    # Construct file paths
    pathModelFile = os.path.join(get_package_share_directory(namePackage), modelFileRelativePath)
    pathWorldFile = os.path.join(get_package_share_directory(namePackage), worldFileRelativePath)

    # Process the Xacro file to generate robot description
    robotDescription = xacro.process_file(pathModelFile).toxml()

    # Include Gazebo launch file
    gazebo_rosPackageLaunch = PythonLaunchDescriptionSource(
        os.path.join(get_package_share_directory(namePackage), 'launch', 'gazebo.launch.py')
    )
    gazeboLaunch = IncludeLaunchDescription(
        gazebo_rosPackageLaunch,
        launch_arguments={'world': pathWorldFile}.items()
    )

    # Nodes for spawning the model and publishing the robot state
    spawnModelNode = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', robotXacroname],
        output='screen'
    )
    nodeRobotStatePublisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robotDescription, 'use_sim_time': True}]
    )

    # Create and populate launch description
    launchDescriptionObject = LaunchDescription()
    launchDescriptionObject.add_action(gazeboLaunch)
    launchDescriptionObject.add_action(spawnModelNode)
    launchDescriptionObject.add_action(nodeRobotStatePublisher)

    return launchDescriptionObject

