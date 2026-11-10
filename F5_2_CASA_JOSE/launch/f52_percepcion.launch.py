"""F5.2: percepcion y localizacion. Gazebo se lanza aparte (scripts/demo_f52.sh). Reutiliza SIN modificar: F5/config/bridge.yaml, urdf, watchdog, F4/mapa.
Diferencia con F5: NO hay static_transform_publisher map->odom. map->odom lo publica SOLO nav2_amcl.
Unico publicador por TF: gz DiffDrive (odom->base_footprint), robot_state_publisher (resto del robot), AMCL (map->odom).
La verdad de terreno (/gz/odom_gt, frame 'world') NO entra en TF: solo la lee monitor_precision.py (no contamina el localizador)."""
import os, math, yaml
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))       # F5_2_CASA_JOSE
F5 = D + '/../F5_INTEGRACION_TRACER'

def generate_launch_description():
    c = yaml.safe_load(open(F5 + '/config/inicio.yaml')); th = math.radians(c['yaw_deg'])
    urdf = open(F5 + '/urdf/tracer_agv_rviz.urdf').read(); sim = {'use_sim_time': True}
    # pose inicial de AMCL = F5/config/inicio.yaml + desplazamiento opcional (para probar convergencia con una pose inicial equivocada)
    ex = float(os.environ.get('F52_ERR_X', 0)); ey = float(os.environ.get('F52_ERR_Y', 0)); eyaw = math.radians(float(os.environ.get('F52_ERR_YAW_DEG', 0)))   # desplazamiento de PRUEBA de la pose inicial de AMCL
    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true'),
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='puente_gz', output='screen', parameters=[{'config_file': F5 + '/config/bridge.yaml'}, sim]),
        # verdad de terreno: puente aparte, solo ROS (no TF)
        Node(package='ros_gz_bridge', executable='parameter_bridge', name='puente_verdad', output='screen', arguments=['/gz/odom_gt@nav_msgs/msg/Odometry[gz.msgs.Odometry'], parameters=[sim]),
        ExecuteProcess(cmd=[F5 + '/scripts/watchdog_cmd_vel.py', '--ros-args', '-r', '__node:=watchdog_cmd_vel', '-p', 'timeout:=0.5', '-p', 'use_sim_time:=true'], output='screen'),
        Node(package='robot_state_publisher', executable='robot_state_publisher', name='robot_state_publisher', output='screen', parameters=[{'robot_description': urdf}, sim]),
        Node(package='nav2_map_server', executable='map_server', name='map_server', output='screen',
             parameters=[{'yaml_filename': F5 + '/../F4_ESCENARIO_CON_MOBILIARIO/mapa/piso_amueblado.yaml'}, sim]),
        Node(package='nav2_amcl', executable='amcl', name='amcl', output='screen',
             parameters=[D + '/config/amcl.yaml', sim, {'initial_pose.x': c['x'] + ex, 'initial_pose.y': c['y'] + ey, 'initial_pose.z': 0.0, 'initial_pose.yaw': th + eyaw}]),
        Node(package='nav2_lifecycle_manager', executable='lifecycle_manager', name='lifecycle_manager_loc', output='screen',
             parameters=[{'autostart': True, 'node_names': ['map_server', 'amcl'], 'bond_timeout': 0.0}, sim]),
        Node(package='rviz2', executable='rviz2', name='rviz2', arguments=['-d', D + '/rviz/f52.rviz'], parameters=[sim], condition=IfCondition(LaunchConfiguration('rviz'))),
    ])
