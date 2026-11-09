#!/usr/bin/env python3
"""F5: genera mundo/piso_amueblado_tracer.sdf = mundo de F4 (SIN modificarlo; se lee) + sistema de sensores (lidar) + TRACER en config/inicio.yaml (+ verdad de terreno opcional).
Uso: generar_mundo.py [--gt] [--sin_robot]"""
import sys, os, math, yaml, re
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
w = open(D + '/../F4_ESCENARIO_CON_MOBILIARIO/mundo/piso_amueblado.sdf').read()
c = yaml.safe_load(open(D + '/config/inicio.yaml'))
gt = '--gt' in sys.argv
w = w.replace('<!-- GENERADO por scripts/generar_mundo.py desde config/mobiliario.yaml. No editar a mano: editar el YAML y regenerar. -->',
              '<!-- F5: GENERADO por F5/scripts/generar_mundo.py = mundo de F4 + sensores + TRACER (config/inicio.yaml). No editar a mano. -->')
w = w.replace('<world name="piso_amueblado">', '<world name="piso_amueblado">')
w = w.replace('<plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>',
              '<plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>\n    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors"><render_engine>ogre2</render_engine></plugin>')
rob = ''
if '--sin_robot' not in sys.argv:
    g = '''
      <plugin filename="gz-sim-odometry-publisher-system" name="gz::sim::systems::OdometryPublisher">
        <odom_frame>world</odom_frame><robot_base_frame>tracer</robot_base_frame><dimensions>3</dimensions><odom_publish_frequency>100</odom_publish_frequency>
        <odom_topic>/gz/odom_gt</odom_topic><tf_topic>/gz/tf_gt</tf_topic>
      </plugin>''' if gt else ''
    rob = '    <include><name>tracer</name><uri>model://tracer_agv</uri><pose>%.4f %.4f 0.002 0 0 %.6f</pose>%s</include>\n' % (c['x'], c['y'], math.radians(c['yaw_deg']), g)
w = w.replace('  </world>', rob + '  </world>')
out = D + '/mundo/piso_amueblado_tracer%s.sdf' % ('_gt' if gt else '')
open(out, 'w').write(w); print(out)
