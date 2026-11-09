#!/usr/bin/env bash
# F5: puente SOLO PARA PRUEBAS: pose real del modelo en Gazebo (verdad de terreno, OdometryPublisher en el include del mundo) -> /gz/odom_gt (nav_msgs/Odometry).
source /opt/ros/jazzy/setup.bash
exec ros2 run ros_gz_bridge parameter_bridge "/gz/odom_gt@nav_msgs/msg/Odometry[gz.msgs.Odometry" --ros-args -p use_sim_time:=true
