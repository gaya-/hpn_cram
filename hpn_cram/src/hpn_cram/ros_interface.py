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

import graphics.colorNames # pyamber

import rospy
import tf.transformations

import geometry_msgs.msg
import sensor_msgs.msg
import hpn_cram_msgs.srv
import hpn_cram_msgs.msg

NODE_NAMESPACE = "cram_hpn"
FIXED_FRAME = "map"

ItemGeometry = namedtuple('ItemInfo', ['name', 'dimensions', 'color', 'mass'])
ItemInSpace = namedtuple('ItemInSpace', ['name', 'position', 'rotation_matrix', 'attached_link'])


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
    request_msg = [make_item_geometry_msg(item_info) for item_info in items_infos_list]

    rospy.wait_for_service(NODE_NAMESPACE + '/spawn_world')
    try:
        spawn_world_service = rospy.ServiceProxy(NODE_NAMESPACE + '/spawn_world', hpn_cram_msgs.srv.SpawnWorld)
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

    rospy.wait_for_service(NODE_NAMESPACE + '/set_world_state')
    try:
        set_world_state_service = rospy.ServiceProxy(NODE_NAMESPACE + '/set_world_state', hpn_cram_msgs.srv.SetWorldState)
        response = set_world_state_service(robot_pose_msg, robot_info_msg, items_infos_msg)
        return response
    except rospy.ServiceException, e:
        print "Service call failed: %s"%e