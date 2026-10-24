import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    localization_share = get_package_share_directory('localization_server')
    map_server_share = get_package_share_directory('map_server')

    default_map_file = os.path.join(
        map_server_share,
        'config',
        'warehouse_map_sim.yaml'
    )

    map_file_arg = DeclareLaunchArgument(
        'map_file',
        default_value=default_map_file,
        description='Path to the map YAML file'
    )

    map_file = LaunchConfiguration('map_file')

    is_sim = PythonExpression([
        "'warehouse_map_sim' in '",
        map_file,
        "'"
    ])

    use_sim_time = ParameterValue(is_sim, value_type=bool)

    amcl_config_sim = os.path.join(
        localization_share, 'config', 'amcl_config_sim.yaml'
    )
    amcl_config_real = os.path.join(
        localization_share, 'config', 'amcl_config_real.yaml'
    )

    amcl_config = PythonExpression([
        "'", amcl_config_sim,
        "' if 'warehouse_map_sim' in '",
        map_file,
        "' else '",
        amcl_config_real,
        "'"
    ])

    map_server_node = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_file,
            'use_sim_time': use_sim_time
        }]
    )

    amcl_node = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[
            amcl_config,
            {'use_sim_time': use_sim_time}
        ]
    )

    lifecycle_manager_node = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'autostart': True,
            'node_names': ['map_server', 'amcl']
        }]
    )

    rviz_config = os.path.join(
        localization_share,
        'rviz',
        'amcl_display.rviz'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': use_sim_time}]
    )

    return LaunchDescription([
        map_file_arg,
        map_server_node,
        amcl_node,
        lifecycle_manager_node,
        rviz_node
    ])