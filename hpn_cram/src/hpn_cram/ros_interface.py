#
# Copyright (c) 2019, Gayane Kazhoyan <kazhoyan@cs.uni-bremen.de>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Institute for Artificial Intelligence/
#       Universitaet Bremen nor the names of its contributors may be used to
#       endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from collections import namedtuple

import json

import graphics.colorNames # pyamber

import rospy
import tf.transformations

import geometry_msgs.msg
import sensor_msgs.msg
import hpn_cram_msgs.srv
import hpn_cram_msgs.msg
import cram_commander.srv

NODE_NAMESPACE = "cram_hpn"
FIXED_FRAME = "map"

ItemGeometry = namedtuple('ItemInfo', ['name', 'dimensions', 'color', 'mass'])
ItemInSpace = namedtuple('ItemInSpace', ['name', 'position', 'rotation_matrix', 'attached_link'])

spawn_world_service = None
set_world_state_service = None
perform_action_service = None


def make_item_geometry_msg(item_info):
    item_geometry = hpn_cram_msgs.msg.ItemGeometry()
    item_geometry.item_name = item_info.name
    item_geometry.item_type = item_info.name
    item_geometry.shape.type = item_geometry.shape.BOX
    item_geometry.shape.dimensions = [dim / 2 for dim in item_info.dimensions]
    item_geometry.color = [x / 256.0 for x in graphics.colorNames.colors[item_info.color]]
    item_geometry.mass = item_info.mass
    return item_geometry


def spawn_world_client(items_infos_list):
    global spawn_world_service
    global set_world_state_service
    global perform_action_service

    request_msg = [make_item_geometry_msg(item_info) for item_info in items_infos_list]

    # rospy.wait_for_service(NODE_NAMESPACE + '/spawn_world')
    try:
        spawn_world_service = rospy.ServiceProxy(NODE_NAMESPACE + '/spawn_world',
                                                 hpn_cram_msgs.srv.SpawnWorld)
        set_world_state_service = rospy.ServiceProxy(NODE_NAMESPACE + '/set_world_state',
                                                     hpn_cram_msgs.srv.SetWorldState)
        perform_action_service = rospy.ServiceProxy(NODE_NAMESPACE + '/perform_designator',
                                                    cram_commander.srv.PerformDesignator)
        response = spawn_world_service(request_msg)
        return response
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e


def make_robot_pose_msg(robot_x_y_theta):
    robot_pose = geometry_msgs.msg.PoseStamped()
    robot_pose.header.frame_id = FIXED_FRAME
    robot_pose.pose.position.x = robot_x_y_theta[0]
    robot_pose.pose.position.y = robot_x_y_theta[1]
    robot_pose.pose.position.z = 0.0
    quaternion_vector = tf.transformations.quaternion_from_euler(0, 0, robot_x_y_theta[2])
    robot_pose.pose.orientation.x = quaternion_vector[0]
    robot_pose.pose.orientation.y = quaternion_vector[1]
    robot_pose.pose.orientation.z = quaternion_vector[2]
    robot_pose.pose.orientation.w = quaternion_vector[3]
    return robot_pose


def make_robot_joint_state_msg(robot_joint_state_dict):
    joint_state_msg = sensor_msgs.msg.JointState()
    for (joint_name, joint_position) in robot_joint_state_dict.items():
        joint_state_msg.name.append(joint_name)
        joint_state_msg.position.append(joint_position)
        joint_state_msg.velocity.append(0.0)
        joint_state_msg.effort.append(0.0)
    return joint_state_msg


def make_item_in_space_msg(item_info):
    item_in_space = hpn_cram_msgs.msg.ItemInSpace()

    item_in_space.item_name = item_info.name

    item_in_space.item_pose = geometry_msgs.msg.PoseStamped()
    item_in_space.item_pose.header.frame_id = item_info.attached_link if item_info.attached_link else FIXED_FRAME
    item_in_space.item_pose.pose.position.x = item_info.position[0]
    item_in_space.item_pose.pose.position.y = item_info.position[1]
    item_in_space.item_pose.pose.position.z = item_info.position[2]
    quaternion_vector = tf.transformations.quaternion_from_matrix(item_info.rotation_matrix)
    item_in_space.item_pose.pose.orientation.x = quaternion_vector[0]
    item_in_space.item_pose.pose.orientation.y = quaternion_vector[1]
    item_in_space.item_pose.pose.orientation.z = quaternion_vector[2]
    item_in_space.item_pose.pose.orientation.w = quaternion_vector[3]

    item_in_space.attached = item_in_space.ROBOT if item_info.attached_link else item_in_space.NOT_ATTACHED

    return item_in_space


def set_world_state_client(robot_x_y_theta, robot_joint_state_dict, items_infos):
    robot_pose_msg = make_robot_pose_msg(robot_x_y_theta)
    robot_info_msg = make_robot_joint_state_msg(robot_joint_state_dict)
    items_infos_msg = [make_item_in_space_msg(item_info) for item_info in items_infos]

    # rospy.wait_for_service(NODE_NAMESPACE + '/set_world_state')
    try:
        # set_world_state_service = rospy.ServiceProxy(NODE_NAMESPACE + '/set_world_state', hpn_cram_msgs.srv.SetWorldState)
        response = set_world_state_service(robot_pose_msg, robot_info_msg, items_infos_msg)
        return response
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e


def make_going_action_msg(robot_x_y_theta):
    pose = make_robot_pose_msg(robot_x_y_theta)
    return '[\"AN\",\"ACTION\",{\"TYPE\":[\"GOING\"],\"TARGET\":[[\"A\",\"LOCATION\",{\"POSE\":' + \
           '[[\"{}\",{},[{},{},{}],[{},{},{},{}]]]}}]]}}]'. \
               format(pose.header.frame_id, pose.header.stamp,
                      pose.pose.position.x, pose.pose.position.y, pose.pose.position.z,
                      pose.pose.orientation.x, pose.pose.orientation.y, pose.pose.orientation.z,
                      pose.pose.orientation.w)


def make_arm_joint_action_msg(left_arm_joint_angles, right_arm_joint_angles):
    return '[\"A\",\"MOTION\",{\"TYPE\":[\"MOVING-ARM-JOINTS\"],\"LEFT-JOINT-STATES\":[[' + \
           '[\"l_shoulder_pan_joint\",{}],[\"l_shoulder_lift_joint\",{}],[\"l_upper_arm_roll_joint\",{}],' \
           '[\"l_elbow_flex_joint\",{}],[\"l_forearm_roll_joint\",{}],[\"l_wrist_flex_joint\",{}],[\"l_wrist_roll_joint\",{}]'. \
               format(left_arm_joint_angles[0], left_arm_joint_angles[1], left_arm_joint_angles[2],
                      left_arm_joint_angles[3], left_arm_joint_angles[4], left_arm_joint_angles[5],
                      left_arm_joint_angles[6]) + \
           ']],\"RIGHT-JOINT-STATES\":[[' \
           '[\"r_shoulder_pan_joint\",{}],[\"r_shoulder_lift_joint\",{}],[\"r_upper_arm_roll_joint\",{}],' \
           '[\"r_elbow_flex_joint\",{}],[\"r_forearm_roll_joint\",{}],[\"r_wrist_flex_joint\",{}],' \
           '[\"r_wrist_roll_joint\",{}]]]}}]'. \
               format(right_arm_joint_angles[0], right_arm_joint_angles[1], right_arm_joint_angles[2],
                      right_arm_joint_angles[3], right_arm_joint_angles[4], right_arm_joint_angles[5],
                      right_arm_joint_angles[6])


def make_move_torso_action_msg(torso_joint_angle):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"MOVING-TORSO\"],\"JOINT-ANGLE\":[{}]}}]'.format(torso_joint_angle[0])


def make_look_action_msg(x_y_z):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"LOOKING\"],\"TARGET\":[' \
           '[\"A\",\"LOCATION\",{{\"POSE\":[[\"map\",0.000000,[{},{},{}],[0.000000,0.000000,0.0,1.0]]]}}]]}}]'.\
        format(x_y_z[0], x_y_z[1], x_y_z[2])


def make_set_gripper_action_msg(arm, position):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"SETTING-GRIPPER\"],\"GRIPPER\":[\"{}\"],\"POSITION\":[{}]}}]'. \
        format(arm, position)


def make_release_gripper_action_msg(arm):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"RELEASING\"],\"GRIPPER\":[\"{}\"]}}]'.format(arm)


def make_grip_action_msg(arm, object_name):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"GRIPPING\"],\"GRIPPER\":[\"{}\"],' \
           '\"OBJECT\":[[\"A\",\"OBJECT\",{{\"NAME\":[\"{}\"]}}]]}}]'. \
        format(arm, object_name)


def make_detect_action_msg(region_name):
    return '[\"A\",\"ACTION\",{{\"TYPE\":[\"DETECTING\"],\"OBJECT\":[' \
           '[\"ALL\",\"OBJECT\",{{\"LOCATION\":[[\"A\",\"LOCATION\",{{\"ON\":[' \
           '[\"A\",\"OBJECT\",{{\"TYPE\":[\"COUNTER-TOP\"],\"URDF-NAME\":[\"{}\"],' \
           '\"OWL-NAME\":[\"kitchen_sink_block_counter_top\"]}}]]}}]]}}]]}}]'. \
        format(region_name)


def parse_return_json_string(json_string):
    parsed_json = json.loads(json_string)
    object_name_pose_dict = {}
    for object_designator_json in parsed_json:
        object_name = object_designator_json[2][u'NAME'][0].lower().encode('ascii', 'ignore')
        object_pose_in_map = object_designator_json[2][u'POSE'][0][2][1]
        object_x_y_z = object_pose_in_map[2]
        object_q1_q2_q3_w = object_pose_in_map[3]
        object_theta = tf.transformations.euler_from_quaternion(object_q1_q2_q3_w)[2]
        object_name_pose_dict[object_name] = [object_x_y_z, object_theta]
    return object_name_pose_dict


def perform_action_client(action_string):
    # rospy.wait_for_service(NODE_NAMESPACE + '/perform_designator')
    try:
        # perform_action_service = rospy.ServiceProxy(NODE_NAMESPACE + '/perform_designator',
        #                                             cram_commander.srv.PerformDesignator)
        response = perform_action_service(action_string)
        return [parse_return_json_string(response.result)] if response.result else []
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e