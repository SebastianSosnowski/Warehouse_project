import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    default_map_file = os.path.join(
        get_package_share_directory('map_server'),
        'config',
        'warehouse_map_sim.yaml'
    )

    map_file_arg = DeclareLaunchArgument(
        'map_file',
        default_value=default_map_file,
        description='Path to the map YAML file'
    )

    map_file = LaunchConfiguration('map_file')
    rviz_file = os.path.join(get_package_share_directory('map_server'), 'rviz', 'map_display.rviz')
    # map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'warehouse_map_sim.yaml')
    
    map_server_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': True}, 
                        {'yaml_filename':map_file} 
                       ])
    lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_mapper',
            output='screen',
            parameters=[{'use_sim_time': True},
                        {'autostart': True},
                        {'node_names': ['map_server']}])
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_file])

    return LaunchDescription([
    map_file_arg,
    map_server_node,
    lifecycle_manager_node,
    rviz_node
    ])