
import os

from ament_index_python.packages import PackageNotFoundError, get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    loopback_dir = get_package_share_directory('nav2_loopback_sim')
    default_map = os.path.join(loopback_dir, 'maps', 'warehouse.yaml')
    try:
        bringup_dir = get_package_share_directory('ats_sentry_bringup')
        rmuc_2027_map = os.path.join(bringup_dir, 'map', 'rmuc_2027.yaml')
        if os.path.isfile(rmuc_2027_map):
            default_map = rmuc_2027_map
    except PackageNotFoundError:
        pass
    map_yaml_file = LaunchConfiguration('map')
    declare_map_cmd = DeclareLaunchArgument(
        'map',
        default_value=default_map,
        description='Static occupancy-grid YAML published on /map.',
    )

    scan_frame_id = LaunchConfiguration('scan_frame_id')
    declare_scan_frame_id_cmd = DeclareLaunchArgument(
        'scan_frame_id',
        default_value='base_scan',
    )

    # cmd_vel_arbiter 是 /cmd_vel/selected 的唯一 publisher：loopback 与实机、
    # MuJoCo、Gazebo 共享同一条「执行端只消费 selected」的速度出口契约。
    # 串口链不存在，require_serial_link 置 False，速度仍须经仲裁。
    cmd_vel_arbiter_cmd = Node(
        package='ats_cmd_vel_arbiter',
        executable='cmd_vel_arbiter_node',
        name='cmd_vel_arbiter',
        output='screen',
        parameters=[{
            'manual_cmd_vel_topic': '/cmd_vel',
            'autonomy_cmd_vel_topic': '/cmd_vel/autonomy_raw',
            'selected_cmd_vel_topic': '/cmd_vel/selected',
            'require_serial_link': False,
        }],
    )

    loopback_sim_cmd = Node(
        package='nav2_loopback_sim',
        executable='loopback_simulator',
        name='loopback_simulator',
        output='screen',
        parameters=[{
            'scan_frame_id': scan_frame_id,
            'command_topic': '/cmd_vel/selected',
            'enable_stamped_cmd_vel': False,
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
    ld.add_action(cmd_vel_arbiter_cmd)
    ld.add_action(loopback_sim_cmd)
    return ld
