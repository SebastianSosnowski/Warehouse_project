import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_share = get_package_share_directory('path_planner_server')
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value='True')
    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file = os.path.join(get_package_share_directory('map_server'), 'config', 'turtlebot_area.yaml')
    nav2_yaml = os.path.join(get_package_share_directory('localization_server'), 'config', 'amcl_config.yaml')

    # Choose correct config files
    bt_navigator_config = PythonExpression([
        "'", os.path.join(package_share, 'config', 'bt_navigator_sim.yaml'),
        "' if '", use_sim_time,
        "' == 'True' else '",
        os.path.join(package_share, 'config', 'bt_navigator_real.yaml'),
        "'"
    ])

    planner_config = PythonExpression([
        "'", os.path.join(package_share, 'config', 'planner_sim.yaml'),
        "' if '", use_sim_time,
        "' == 'True' else '",
        os.path.join(package_share, 'config', 'planner_real.yaml'),
        "'"
    ])

    controller_config = PythonExpression([
        "'", os.path.join(package_share, 'config', 'controller_sim.yaml'),
        "' if '", use_sim_time,
        "' == 'True' else '",
        os.path.join(package_share, 'config', 'controller_real.yaml'),
        "'"
    ])

    recoveries_config = PythonExpression([
        "'", os.path.join(package_share, 'config', 'recoveries_sim.yaml'),
        "' if '", use_sim_time,
        "' == 'True' else '",
        os.path.join(package_share, 'config', 'recoveries_real.yaml'),
        "'"
    ])

    map_server_node = Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}, 
                        {'yaml_filename':map_file}])

    amcl_node = Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[nav2_yaml])

    planner_server_node = Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[planner_config])
            
    controller_server_node = Node(
            name='controller_server',
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[controller_config])
            
    bt_navigator_node = Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[bt_navigator_config])
            
    recovery_node = Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[recoveries_config],
            output='screen')

    lifecycle_manager_node = Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time},
                        {'autostart': True},
                        {'node_names': [
                        'map_server', 
                        'amcl',
                        'planner_server',
                        'controller_server',
                        'bt_navigator',
                        'recoveries_server']}])

    return LaunchDescription([
    use_sim_time_arg,
    map_server_node,
    amcl_node,
    planner_server_node,
    controller_server_node,
    bt_navigator_node,
    recovery_node,
    lifecycle_manager_node
    ])