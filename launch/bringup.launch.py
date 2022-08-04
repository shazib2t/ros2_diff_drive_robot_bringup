# Copyright (c) 2021 Juan Miguel Jimeno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import yaml
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.conditions import IfCondition


def generate_launch_description():
    sensors_launch_path = PathJoinSubstitution(
        [FindPackageShare('ros2_diff_drive_robot_bringup'), 'launch', 'sensors.launch.py']
    )

    joy_launch_path = PathJoinSubstitution(
        [FindPackageShare('ros2_diff_drive_robot_bringup'), 'launch', 'joy_teleop.launch.py']
    )

    description_launch_path = PathJoinSubstitution(
        [FindPackageShare('ros2_diff_drive_robot_description'), 'launch', 'description.launch.py']
    )

    #ekf_config_path = PathJoinSubstitution(
    #    [FindPackageShare('ros2_diff_drive_robot_bringup'), 'config', 'ekf.yaml']
    #)
    ekf_config_path = os.path.join(get_package_share_directory('ros2_diff_drive_robot_bringup'), 'config/ekf.yaml')
    
    
    # Load the parameters specific to your ComposableNode
    with open(ekf_config_path, 'r') as file:
        configParams = yaml.safe_load(file)['ekf_filter_node']['ros__parameters']
    

    return LaunchDescription([
        DeclareLaunchArgument(
            name='base_serial_port', 
            default_value='/dev/ttyACM0',
            description='ros2_diff_drive_robot Base Serial Port'
        ),

       DeclareLaunchArgument(
            name='joy', 
            default_value='false',
            description='Use Joystick'
        ),

        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            name='micro_ros_agent',
            output='screen',
            arguments=['serial', '--dev', LaunchConfiguration("base_serial_port")]
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[configParams]
            #remappings=[("odometry/filtered", "odom")]
            
        ),
        
        #Node(package = "tf2_ros", 
        #     executable = "static_transform_publisher",
        #     output='screen',
        #     arguments = ["0", "0", "0", "0", "0", "0", "map", "base_footprint"]
        #),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(description_launch_path)
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(sensors_launch_path),
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(joy_launch_path),
            condition=IfCondition(LaunchConfiguration("joy")),
        )
        
    ])
