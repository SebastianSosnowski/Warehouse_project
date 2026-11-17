import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression, Command
from launch.conditions import UnlessCondition
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    package_share = get_package_share_directory('path_planner_server')
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value='True')
    use_sim_time = LaunchConfiguration("use_sim_time")

    map_server_share = get_package_share_directory('map_server')
    sim_map = os.path.join(map_server_share,'config','warehouse_map_sim.yaml')
    real_map = os.path.join(map_server_share,'config','warehouse_map_real.yaml')
    map_file = PythonExpression([
        "'", sim_map,
        "' if '", use_sim_time,
        "' == 'True' else '", real_map,
        "'"
    ])

    robot_description_share = get_package_share_directory(
        'rb1_ros2_description'
    )

    robot_description_file = os.path.join(
        robot_description_share,
        'xacro',
        'rb1_ros2_base.urdf.xacro'
    )

    robot_description = ParameterValue(
        Command([
            'xacro ',
            robot_description_file,
            ' robot_name:=rb1'
        ]),
        value_type=str
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='rb1_robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }],
        remappings=[
            ('/robot_description', '/rb1_robot_description'),
            ('/joint_states', '/rb1/joint_states')
        ],
        condition=UnlessCondition(use_sim_time)
    )

    localization_share = get_package_share_directory('localization_server')
    amcl_config_sim = os.path.join(localization_share, 'config', 'amcl_config_sim.yaml')
    amcl_config_real = os.path.join(localization_share, 'config', 'amcl_config_real.yaml')

    amcl_config = PythonExpression([
        "'", amcl_config_sim,
        "' if 'warehouse_map_sim' in '",
        map_file,
        "' else '",
        amcl_config_real,
        "'"
    ])

    rviz_file = os.path.join(get_package_share_directory('path_planner_server'), 'rviz', 'navigation.rviz')

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
            parameters=[
                amcl_config,
                {'use_sim_time': use_sim_time}
            ])

    planner_server_node = Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[
                planner_config,
                {'use_sim_time': use_sim_time}]
                )
            
    controller_server_node = Node(
            name='controller_server',
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[
                controller_config,
                {'use_sim_time': use_sim_time}])
            
    bt_navigator_node = Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[
                bt_navigator_config,
                {'use_sim_time': use_sim_time}])
            
    recovery_node = Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='recoveries_server',
            parameters=[
                recoveries_config,
                {'use_sim_time': use_sim_time}],
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

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-d', rviz_file])

    return LaunchDescription([
    use_sim_time_arg,
    map_server_node,
    amcl_node,
    planner_server_node,
    controller_server_node,
    bt_navigator_node,
    recovery_node,
    lifecycle_manager_node,
    robot_state_publisher_node,
    rviz_node
    ])