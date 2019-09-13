cmake_minimum_required(VERSION 2.8.3)
project(hpn_cram_msgs)

set(MSG_DEPS
  std_msgs
  geometry_msgs
  shape_msgs
  sensor_msgs)

find_package(catkin REQUIRED COMPONENTS
  message_generation
  ${MSG_DEPS})

add_message_files(FILES
  ItemGeometry.msg
  ItemInSpace.msg)

add_service_files(FILES
  SpawnWorld.srv
  SetWorldState.srv)

generate_messages(DEPENDENCIES ${MSG_DEPS})

catkin_package(CATKIN_DEPENDS
  message_runtime
  ${MSG_DEPS})
