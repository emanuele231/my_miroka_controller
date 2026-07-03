#!/usr/bin/env python3
"""
ROS 2 — ANGRY (hands on hips, ears mid)
"""

from typing import List
import math
import time
import signal
import sys
import os

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from sensor_msgs.msg import PointCloud2, JointState
from geometry_msgs.msg import PoseStamped, Quaternion
from enchanted_msgs.msg import ExtendedJointState, ControlMode


def yaw_to_quaternion(yaw_rad: float) -> Quaternion:
    q = Quaternion()
    half = yaw_rad * 0.5
    q.w = math.cos(half)
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(half)
    return q


def make_extended_joint_state(names: List[str], positions: List[float]) -> ExtendedJointState:
    assert len(names) == len(positions)
    msg = ExtendedJointState()
    msg.joint_state = JointState()
    msg.joint_state.name = names
    msg.joint_state.position = positions
    msg.joint_state.velocity = [0.0] * len(names)
    msg.joint_state.effort = [0.0] * len(names)
    msg.control_mode = ControlMode(state=ControlMode.POSITION)
    return msg

def signal_handler_sigint(signum, frame):
    print("\nCtrl+C rilevato. Chiusura pulita...")
    if 'node' in globals():
        node.publish_default_pose()
    sys.exit(0)


def signal_handler_sigtstp(signum, frame):
    print("\nCtrl+Z rilevato. Torno in posizione di default prima di sospendere...")
    if 'node' in globals():
        node.publish_default_pose()
    os.kill(os.getpid(), signal.SIGSTOP)


class AngryDemo(Node):
    def __init__(self,
                 pointcloud_topic: str = 'point_cloud',
                 ears_target_topic: str = '/targets/ears',
                 neck_target_topic: str = '/targets/neck',
                 left_arm_topic: str = '/targets/left_arm',
                 right_arm_topic: str = '/targets/right_arm',
                 right_fingers_topic: str = '/targets/arms/right/fingers',
                 left_fingers_topic: str = '/targets/arms/left/fingers',
                 goal_pose_topic: str = 'goal_pose',
                 goal_frame: str = 'map'):
        super().__init__('Angry_demo')

        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        self.neck_pub = self.create_publisher(ExtendedJointState, neck_target_topic, qos)
        self.ears_pub = self.create_publisher(ExtendedJointState, ears_target_topic, qos)
        self.left_arm_pub = self.create_publisher(ExtendedJointState, left_arm_topic, qos)
        self.right_arm_pub = self.create_publisher(ExtendedJointState, right_arm_topic, qos)
        self.right_fingers_pub = self.create_publisher(ExtendedJointState, right_fingers_topic, qos)
        self.left_fingers_pub = self.create_publisher(ExtendedJointState, left_fingers_topic, qos)
        self.goal_pub = self.create_publisher(PoseStamped, goal_pose_topic, qos)

        self.create_subscription(PointCloud2, pointcloud_topic, self._on_pointcloud, qos)

        self.neck_names = [
            "HED_NECK_FRONTAL_JOINT",
            "HED_NECK_SAGITTAL_JOINT",
            "HED_NECK_TRANSVERSAL_JOINT"
        ]
        self.neck_pos = [0.0, -0.15, 0.0]

        self.ears_names = [
            "HED_EAR_LEFT_JOINT", "HED_EAR_RIGHT_JOINT"
        ]
        self.ears_pos = [0.5, 0.5]

        self.left_arm_names = [
            "ARM_LEFT_SHOULDER_SAGITTAL_JOINT", "ARM_LEFT_SHOULDER_FRONTAL_JOINT",
            "ARM_LEFT_SHOULDER_TRANSVERSAL_JOINT", "ARM_LEFT_ELBOW_SAGITTAL_JOINT",
            "ARM_LEFT_WRIST_FRONTAL_JOINT", "ARM_LEFT_WRIST_TRANSVERSAL_JOINT",
            "ARM_LEFT_WRIST_SAGITTAL_JOINT"
        ]
        self.right_arm_names = [
            "ARM_RIGHT_SHOULDER_SAGITTAL_JOINT", "ARM_RIGHT_SHOULDER_FRONTAL_JOINT",
            "ARM_RIGHT_SHOULDER_TRANSVERSAL_JOINT", "ARM_RIGHT_ELBOW_SAGITTAL_JOINT",
            "ARM_RIGHT_WRIST_FRONTAL_JOINT", "ARM_RIGHT_WRIST_TRANSVERSAL_JOINT",
            "ARM_RIGHT_WRIST_SAGITTAL_JOINT"
        ]
        
        self.left_fingers_names = ["LEFT_FINGERS"]
        self.right_fingers_names = ["RIGHT_FINGERS"]
        self.fingers_base = [0.0]
        
        self.left_arm_base = [0.4, 0.8, -1.0, -1.2, 0.0, 0.0, 1.0]
        self.right_arm_base = [0.4, 0.8, -1.0, -1.2, 0.0, 0.0, 1.0]
        
        self.reset_arm_base = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        self.default_neck = [0.0, 0.0, 0.0]
        self.default_ears = [0.0, 0.0]
        
        self.wave_joint_index = 5
        self.wave_amplitude = 0.5
        self.wave_frequency = 1.5

        
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.duration = 6.0
        self.timer = self.create_timer(0.05, self.publish_angry_stream)

        self.get_logger().info('Rabbia avviata: mani sui fianchi ferme, orecchie all indietro, per 6s')

    def _on_pointcloud(self, msg: PointCloud2) -> None:
        pass

    def publish_angry_stream(self) -> None:
        now = self.get_clock().now().nanoseconds / 1e9
        elapsed = now - self.start_time
        
        # face_msg = String()
	# face_msg.data = "ANGRY_SHOUT"
	# sound_msg.data = "ANGER_GROWL"
	# self.face_pub.publish(face_msg)

        if elapsed > self.duration:
            self.get_logger().info('Rabbia completato. Nodo in standby.')
            self.publish_default_pose()
            self.timer.cancel()
            return

        neck_msg = make_extended_joint_state(self.neck_names, self.neck_pos)
        self.neck_pub.publish(neck_msg)

        ears_msg = make_extended_joint_state(self.ears_names, self.ears_pos)
        self.ears_pub.publish(ears_msg)

        left_msg = make_extended_joint_state(self.left_arm_names, self.left_arm_base)
        self.left_arm_pub.publish(left_msg)

        right_msg = make_extended_joint_state(self.right_arm_names, self.right_arm_base)
        self.right_arm_pub.publish(right_msg)
        
        left_fingers_msg = make_extended_joint_state(self.left_fingers_names, self.fingers_base)
        self.left_fingers_pub.publish(left_fingers_msg)

        right_fingers_msg = make_extended_joint_state(self.right_fingers_names, self.fingers_base)
        self.right_fingers_pub.publish(right_fingers_msg)
        
    def publish_default_pose(self) -> None:
        self.get_logger().info('Pubblicazione posizione di default...')
        
        for i in range(20):
            neck_msg = make_extended_joint_state(self.neck_names, self.default_neck)
            self.neck_pub.publish(neck_msg)

            ears_msg = make_extended_joint_state(self.ears_names, self.default_ears)
            self.ears_pub.publish(ears_msg)

            left_msg = make_extended_joint_state(self.left_arm_names, self.reset_arm_base)
            self.left_arm_pub.publish(left_msg)

            right_msg = make_extended_joint_state(self.right_arm_names, self.reset_arm_base)
            self.right_arm_pub.publish(right_msg)

            left_fingers_msg = make_extended_joint_state(self.left_fingers_names, [0.0])
            self.left_fingers_pub.publish(left_fingers_msg)

            right_fingers_msg = make_extended_joint_state(self.right_fingers_names, [0.0])
            self.right_fingers_pub.publish(right_fingers_msg)
            
            time.sleep(0.1)
        
        self.get_logger().info('Posizione di default pubblicata (braccia lungo il corpo).')


    def _publish_goal_absolute(self, *, frame_id: str, x: float, y: float, yaw: float) -> None:
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = frame_id
        msg.pose.position.x = x
        msg.pose.position.y = y
        msg.pose.position.z = 0.0
        msg.pose.orientation = yaw_to_quaternion(yaw)
        self.goal_pub.publish(msg)
        self.get_logger().info(f"Goal published: x={x:.2f}, y={y:.2f}, yaw={yaw:.2f}")


def main():

    global node
    
    signal.signal(signal.SIGINT, signal_handler_sigint)
    signal.signal(signal.SIGTSTP, signal_handler_sigtstp)
    
    rclpy.init()
    node = AngryDemo(
        pointcloud_topic='point_cloud',
        ears_target_topic='/targets/ears',
        neck_target_topic='/targets/neck',
        left_arm_topic='/targets/left_arm',
        right_arm_topic='/targets/right_arm',
        right_fingers_topic='/targets/arms/right/fingers',
        left_fingers_topic='/targets/arms/left/fingers',
        goal_pose_topic='goal_pose',
        goal_frame='map',
    )
    try:
        rclpy.spin(node)
    except Exception as e:
        node.get_logger().error(f'Errore: {e}')
    finally:
        node.destroy_node()
        try:
            if rclpy.ok():
                rclpy.shutdown()
        except Exception:
            pass


if __name__ == '__main__':
    main()
