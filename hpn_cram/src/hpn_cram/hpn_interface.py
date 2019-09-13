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

import numpy # for tolist()

import ros_interface # for ItemGeometry and all the functions

ALREADY_SPAWNED = False

DEFAULT_MASS = 0.2

def spawn_objects(bodies):
    body_infos = []
    for (body_name, body_object) in bodies.items():
        dimensions = (body_object.value.shapeBBox[1] - body_object.value.shapeBBox[0]).tolist()
        color = body_object.value.properties['color']
        info = ros_interface.ItemGeometry(name=body_name, dimensions=dimensions, color=color, mass=DEFAULT_MASS)
        body_infos.append(info)
    success = ros_interface.spawn_world_client(body_infos)
    return success


def set_world_state(signature, environment_bodies):
    global ALREADY_SPAWNED
    if not ALREADY_SPAWNED:
        spawn_objects(environment_bodies)
        ALREADY_SPAWNED = True

    poses = signature[0]
    item_in_space_infos = []
    for (object_name, object_pose) in poses:
        position = [object_pose.value.x, object_pose.value.y, object_pose.value.z] # object_pose.body.point
        rotation_matrix = numpy.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        info = ros_interface.ItemInSpace(name=object_name,
                                         position=position,
                                         rotation_matrix=rotation_matrix,
                                         attached_link='')
        item_in_space_infos.append(info)

    object_in_hand_list = signature[1]
    for object_in_hand_tuple in object_in_hand_list:
        link = ''
        if object_in_hand_tuple[0] == 'left':
            link = 'l_wrist_roll_link'
        elif object_in_hand_tuple[0] == 'right':
            link = 'r_wrist_roll_link'
        else:
            raise Exception("Unknown attachment link " + object_in_hand_tuple[0])
        if object_in_hand_tuple[1]:
            attached_object_name = object_in_hand_tuple[1][0]
            attached_object_grasp = object_in_hand_tuple[1][1]
            if attached_object_grasp and attached_object_grasp != 'none':
                attached_object_pose_in_link_matrix = attached_object_grasp.grasp_trans[object_in_hand_tuple[0]].matrixInv
                position = [attached_object_pose_in_link_matrix[0][3],
                            attached_object_pose_in_link_matrix[1][3],
                            attached_object_pose_in_link_matrix[2][3]]
                info = ros_interface.ItemInSpace(name=attached_object_name,
                                                 position=position,
                                                 rotation_matrix=attached_object_pose_in_link_matrix,
                                                 attached_link=link)
                item_in_space_infos.append(info)

    static = signature[2]
    ## TODO: what to do with this self.static? What is the physical meaning behind this?

    robot_config = signature[3].value.conf
    robot_x_y_theta = robot_config['pr2Base']
    robot_joint_state_dict = {}
    robot_joint_state_dict['l_gripper_l_finger_joint'] = robot_config['pr2LeftGripper'][0] * 5.0
    robot_joint_state_dict['l_gripper_l_finger_tip_joint'] = robot_config['pr2LeftGripper'][0] * 5.0
    robot_joint_state_dict['l_gripper_r_finger_joint'] = robot_config['pr2LeftGripper'][0] * 5.0
    robot_joint_state_dict['l_gripper_r_finger_tip_joint'] = robot_config['pr2LeftGripper'][0] * 5.0
    robot_joint_state_dict['r_shoulder_pan_joint'] = robot_config['pr2RightArm'][0]
    robot_joint_state_dict['r_shoulder_lift_joint'] = robot_config['pr2RightArm'][1]
    robot_joint_state_dict['r_upper_arm_roll_joint'] = robot_config['pr2RightArm'][2]
    robot_joint_state_dict['r_elbow_flex_joint'] = robot_config['pr2RightArm'][3]
    robot_joint_state_dict['r_forearm_roll_joint'] = robot_config['pr2RightArm'][4]
    robot_joint_state_dict['r_wrist_flex_joint'] = robot_config['pr2RightArm'][5]
    robot_joint_state_dict['r_wrist_roll_joint'] = robot_config['pr2RightArm'][6]
    robot_joint_state_dict['torso_lift_joint'] = robot_config['pr2Torso'][0]
    robot_joint_state_dict['r_gripper_l_finger_joint'] = robot_config['pr2RightGripper'][0] * 5.0
    robot_joint_state_dict['r_gripper_l_finger_tip_joint'] = robot_config['pr2RightGripper'][0] * 5.0
    robot_joint_state_dict['r_gripper_r_finger_joint'] = robot_config['pr2RightGripper'][0] * 5.0
    robot_joint_state_dict['r_gripper_r_finger_tip_joint'] = robot_config['pr2RightGripper'][0] * 5.0
    robot_joint_state_dict['head_pan_joint'] = robot_config['pr2Head'][0]
    robot_joint_state_dict['head_tilt_joint'] = robot_config['pr2Head'][1]
    robot_joint_state_dict['l_shoulder_pan_joint'] = robot_config['pr2LeftArm'][0]
    robot_joint_state_dict['l_shoulder_lift_joint'] = robot_config['pr2LeftArm'][1]
    robot_joint_state_dict['l_upper_arm_roll_joint'] = robot_config['pr2LeftArm'][2]
    robot_joint_state_dict['l_elbow_flex_joint'] = robot_config['pr2LeftArm'][3]
    robot_joint_state_dict['l_forearm_roll_joint'] = robot_config['pr2LeftArm'][4]
    robot_joint_state_dict['l_wrist_flex_joint'] = robot_config['pr2LeftArm'][5]
    robot_joint_state_dict['l_wrist_roll_joint'] = robot_config['pr2LeftArm'][6]

    return ros_interface.set_world_state_client(robot_x_y_theta, robot_joint_state_dict, item_in_space_infos)