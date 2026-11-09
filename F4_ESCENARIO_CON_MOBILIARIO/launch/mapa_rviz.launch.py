"""F4: map_server + lifecycle_manager (autostart) + TF estático identidad map->world + RViz2.
Uso: ros2 launch <ruta>/launch/mapa_rviz.launch.py [mapa:=piso_amueblado] [rviz:=true|false] [config:=piso_amueblado|piso_amueblado_zoom]
map y world coinciden (coordenadas del CAD); NO se aplica ningún desplazamiento: el origen del mapa ya va en el YAML."""
import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, TextSubstitution
from launch_ros.actions import Node

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("mapa", default_value="piso_amueblado"),
        DeclareLaunchArgument("rviz", default_value="true"),
        DeclareLaunchArgument("config", default_value="piso_amueblado"),
        Node(package="nav2_map_server", executable="map_server", name="map_server", output="screen",
             parameters=[{"yaml_filename": [TextSubstitution(text=D + "/mapa/"), LaunchConfiguration("mapa"), TextSubstitution(text=".yaml")]}]),
        Node(package="nav2_lifecycle_manager", executable="lifecycle_manager", name="lifecycle_manager_mapa", output="screen",
             parameters=[{"autostart": True, "node_names": ["map_server"]}]),
        Node(package="tf2_ros", executable="static_transform_publisher", name="tf_map_world",
             arguments=["--frame-id", "map", "--child-frame-id", "world"]),
        Node(package="rviz2", executable="rviz2", name="rviz2", arguments=["-d", [TextSubstitution(text=D + "/config/"), LaunchConfiguration("config"), TextSubstitution(text=".rviz")]], condition=IfCondition(LaunchConfiguration("rviz"))),
    ])
