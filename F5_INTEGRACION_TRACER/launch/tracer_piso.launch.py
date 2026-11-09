"""F5: lado ROS 2 de la demostracion (Gazebo se lanza aparte con scripts/demo_gazebo.sh).
 - watchdog_cmd_vel (0,5 s)           : /cmd_vel -> /cmd_vel_seguro (unica entrada del DiffDrive; sin ordenes recientes = parada)
 - ros_gz_bridge (config/bridge.yaml) : /clock /cmd_vel_seguro /odom /tf /joint_states /scan
 - robot_state_publisher             : TF fijos del robot (base_footprint->base_link->laser, ruedas con /joint_states). NO publica odom->base_footprint (lo hace el DiffDrive de Gazebo)
 - static_transform_publisher        : map->odom = pose inicial del robot (config/inicio.yaml). Es ESTATICO porque odom nace en esa pose; no hay AMCL en F5
 - map_server + lifecycle_manager    : mapa de F4 (solo lectura)   - rviz2 (rviz/tracer_piso.rviz)
Todo con use_sim_time. Publicadores de TF: gz DiffDrive (odom->base_footprint), rsp (resto del robot), static (map->odom)."""
import os, math, yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_launch_description():
    c = yaml.safe_load(open(D + '/config/inicio.yaml')); th = math.radians(c['yaw_deg'])
    urdf = open(D + '/urdf/tracer_agv_rviz.urdf').read(); sim = {'use_sim_time': True}
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='puente_gz', output='screen', parameters=[{'config_file': D + '/config/bridge.yaml'}, sim]),
        ExecuteProcess(cmd=[D + '/scripts/watchdog_cmd_vel.py', '--ros-args', '-r', '__node:=watchdog_cmd_vel', '-p', 'timeout:=0.5', '-p', 'use_sim_time:=true'], output='screen'),
        Node(package='robot_state_publisher', executable='robot_state_publisher', name='robot_state_publisher', output='screen', parameters=[{'robot_description': urdf}, sim]),
        Node(package='tf2_ros', executable='static_transform_publisher', name='tf_map_odom', parameters=[sim],
             arguments=['--x', str(c['x']), '--y', str(c['y']), '--z', '0', '--yaw', str(th), '--frame-id', 'map', '--child-frame-id', 'odom']),
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'yaml_filename': D + '/../F4_ESCENARIO_CON_MOBILIARIO/mapa/piso_amueblado.yaml'}, sim]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_mapa', output='screen',
             parameters=[{'autostart': True, 'node_names': ['map_server']}, sim]),
        Node(package='rviz2', executable='rviz2', name='rviz2', arguments=['-d', D + '/rviz/tracer_piso.rviz'], parameters=[sim], condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
