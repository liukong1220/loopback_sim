
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    loopback_dir = get_package_share_directory('nav2_loopback_sim')
    map_yaml_file = LaunchConfiguration('map')
    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=os.path.join(loopback_dir, 'maps', 'warehouse.yaml'),
        description='Static occupancy-grid YAML published on /map.',
    )

    scan_frame_id = LaunchConfiguration('scan_frame_id')
    declare_scan_frame_id_cmd = DeclareLaunchArgument(
        'scan_frame_id',
        default_value='base_scan',
    )

    loopback_sim_cmd = Node(
        package='nav2_loopback_sim',
        executable='loopback_simulator',
        name='loopback_simulator',
        output='screen',
        parameters=[{
            'scan_frame_id': scan_frame_id,
            'command_topic': '/motion_control',
            'map_topic': '/map',
        }],
    )
    static_map = Node(
        package='ats_nav_bringup',
        executable='static_map_publisher.py',
        name='static_map_publisher',
        output='screen',
        parameters=[{
            'map_yaml_file': map_yaml_file,
            'map_topic': '/map',
            'frame_id': 'map',
        }],
    )

    ld = LaunchDescription()
    ld.add_action(declare_scan_frame_id_cmd)
    ld.add_action(declare_map_cmd)
    ld.add_action(static_map)
    ld.add_action(loopback_sim_cmd)
    return ld
