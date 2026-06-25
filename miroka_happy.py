#!/usr/bin/env python3
"""
ROS 2 — Happiness (Wave with both arms)
"""

from typing import List
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy

from sensor_msgs.msg import PointCloud2, JointState
from geometry_msgs.msg import PoseStamped, Quaternion
from enchanted_msgs.msg import ExtendedJointState, ControlMode


# ------------------------------ Helpers ------------------------------------ #

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


# ------------------------------ Node --------------------------------------- #

class HappinessWave(Node):
    def __init__(self,
                 pointcloud_topic: str = 'point_cloud',
                 neck_target_topic: str = '/targets/neck',
                 left_arm_topic: str = '/targets/left_arm',
                 right_arm_topic: str = '/targets/right_arm',
                 goal_pose_topic: str = 'goal_pose',
                 goal_frame: str = 'map'):
        super().__init__('happiness_wave_demo')

        # QoS esplicito richiesto da Mirokai
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10
        )

        # Publishers
        self.neck_pub = self.create_publisher(ExtendedJointState, neck_target_topic, qos)
        self.left_arm_pub = self.create_publisher(ExtendedJointState, left_arm_topic, qos)
        self.right_arm_pub = self.create_publisher(ExtendedJointState, right_arm_topic, qos)
        self.goal_pub = self.create_publisher(PoseStamped, goal_pose_topic, qos)

        # Subscriber (log only)
        self.create_subscription(PointCloud2, pointcloud_topic, self._on_pointcloud, qos)

        # ---------------- Configurazione collo (neutro, guarda avanti) ---------------- #
        self.neck_names = [
            "HED_NECK_FRONTAL_JOINT",      # Roll
            "HED_NECK_SAGITTAL_JOINT",     # Pitch
            "HED_NECK_TRANSVERSAL_JOINT"   # Yaw
        ]
        self.neck_pos = [0.0, 0.0, 0.0]   # testa dritta, sguardo avanti

        # ---------------- Configurazione braccia ---------------- #
        # Ordine joint per ciascun braccio:
        # [shoulder_sagittal, shoulder_frontal, shoulder_transversal,
        #  elbow_sagittal, wrist_frontal, wrist_transversal, wrist_sagittal]
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

        # Posizione base "braccio alzato" (gomito piegato, braccio in alto)
        # shoulder_frontal negativo/positivo solleva il braccio lateralmente verso l'alto
        self.left_arm_base = [-0.2, -1.4, 0.0, -1.4, 0.0, 0.0, 0.0]
        self.right_arm_base = [-0.2, 1.4, 0.0, -1.4, 0.0, 0.0, 0.0]

        # Indice del giunto su cui applichiamo l'oscillazione (polso transversal = "wave")
        self.wave_joint_index = 5  # wrist_transversal
        self.wave_amplitude = 0.5   # rad
        self.wave_frequency = 1.5   # Hz

        # ---------------- Timing ---------------- #
        self.start_time = self.get_clock().now().nanoseconds / 1e9
        self.duration = 6.0  # secondi totali del saluto
        self.timer = self.create_timer(0.05, self.publish_wave_stream)  # 20 Hz

        self.get_logger().info('Saluto felice avviato: braccia alzate + wave per 6s')

    # -------------------------- Callbacks ---------------------------------- #

    def _on_pointcloud(self, msg: PointCloud2) -> None:
        pass

    def publish_wave_stream(self) -> None:
        now = self.get_clock().now().nanoseconds / 1e9
        elapsed = now - self.start_time

        if elapsed > self.duration:
            self.get_logger().info('Saluto completato. Nodo in standby.')
            self.timer.cancel()
            return

        # Oscillazione sinusoidale per il movimento di saluto
        wave_offset = self.wave_amplitude * math.sin(2.0 * math.pi * self.wave_frequency * elapsed)

        left_pos = list(self.left_arm_base)
        right_pos = list(self.right_arm_base)
        left_pos[self.wave_joint_index] += wave_offset
        right_pos[self.wave_joint_index] += wave_offset

        # Collo neutro, fermo
        neck_msg = make_extended_joint_state(self.neck_names, self.neck_pos)
        self.neck_pub.publish(neck_msg)

        # Braccia in movimento di saluto
        left_msg = make_extended_joint_state(self.left_arm_names, left_pos)
        self.left_arm_pub.publish(left_msg)

        right_msg = make_extended_joint_state(self.right_arm_names, right_pos)
        self.right_arm_pub.publish(right_msg)

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


# ------------------------------ Main --------------------------------------- #

def main():
    rclpy.init()
    node = HappinessWave(
        pointcloud_topic='point_cloud',
        neck_target_topic='/targets/neck',
        left_arm_topic='/targets/left_arm',
        right_arm_topic='/targets/right_arm',
        goal_pose_topic='goal_pose',
        goal_frame='map',
    )
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
