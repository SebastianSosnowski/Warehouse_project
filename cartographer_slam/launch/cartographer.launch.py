import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value='True')
    use_sim_time = LaunchConfiguration("use_sim_time")

    cartographer_config_dir = os.path.join(get_package_share_directory('cartographer_slam'), 'config')
    configuration_basename = PythonExpression([
        "'cartographer_sim.lua' if '",
        use_sim_time,
        "' == 'True' else 'cartographer_real.lua'"
    ])

    rviz_file = os.path.join(get_package_share_directory('cartographer_slam'), 'rviz', 'mapping.rviz')

    # configuration_basename = "cartographer_sim.lua"
    cartographer_node = Node(
            package='cartographer_ros', 
            executable='cartographer_node', 
            name='cartographer_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-configuration_directory', cartographer_config_dir,
                       '-configuration_basename', configuration_basename],
    )
    occupancy_grid_node = Node(
            package='cartographer_ros',
            executable='cartographer_occupancy_grid_node',
            output='screen',
            name='occupancy_grid_node',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=['-resolution', '0.05', '-publish_period_sec', '1.0'],
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': use_sim_time}],
        arguments=['-d', rviz_file])

    return LaunchDescription([
    use_sim_time_arg,
    cartographer_node,
    occupancy_grid_node,
    rviz_node
    ])