"""
    Example file to test robot abilities with a mini-scenario.
    /!\ Don't work in simulation
"""

import argparse
import asyncio
import logging
import os
from dotenv import load_dotenv
from pprint import pformat
from pymirokai.enums import Arm, Direction, SoundName
from pymirokai.models.data_models import EnchantedObject, Coordinates
from pymirokai.robot import connect, Robot
from pymirokai.utils.get_local_ip import get_local_ip
from pymirokai.utils.run_until_interruption import run_until_interruption

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pymirokai_examples")

# Global variables to remember state and display only when value changes
grasping_state = None
navigation_state = None
battery_state = None


async def run(ip: str, api_key: str) -> None:
    """Run the robot, demonstrating various features."""
    async with connect(ip=ip, api_key=api_key) as robot:
        await robot_behavior(robot)
        await asyncio.Future()  # Wait indefinitely


async def robot_behavior(robot: Robot) -> None:
    """Demonstrate various features."""
    logger.info("======= SUBSCRIBE TO TOPICS =======")
    # Subscribe to topics
    robot.subscribe("grasping_state")
    robot.subscribe("navigation_state")
    robot.subscribe("battery_voltage")

    # Register callbacks for topics
    robot.register_callback("grasping_state", handle_grasping_state)
    robot.register_callback("navigation_state", handle_navigation_state)
    robot.register_callback("battery_voltage", handle_battery_voltage)

    await asyncio.sleep(0.5)

    logger.info("======= START SCENARIO =======")

    logger.info("----------- Wave and say hello -----------")
    waving = await robot.wave(arm=Arm.RIGHT).started()
    await robot.say("Hi, I'm a mirokai.").completed()

    await waving.completed()
    await asyncio.sleep(1)

    logger.info("----------- Rotate 90° to the left -----------")
    await robot.turn(degrees=90, direction=Direction.LEFT).completed()

    logger.info("----------- Grasp handle with left arm -----------")
    grasping_handleB = robot.grasp_known_object(rune=EnchantedObject(id="handleB"), arm=Arm.LEFT)
    try:
        await grasping_handleB.started()
    except Exception as e:
        logger.error(f"Error while starting to grasp handleB: {e}")
    try:
        await grasping_handleB.completed()
    except Exception as e:
        logger.error(f"Error while grasping handleB: {e}")

    logger.info("----------- Rotate 90° on the right -----------")
    await robot.turn(degrees=90, direction=Direction.RIGHT).completed()

    logger.info("----------- Move forward (2m) -----------")
    await robot.go_to_relative(Coordinates(x=2)).completed()
    await asyncio.sleep(1)

    logger.info("----------- Give the handle to the user -----------")
    await robot.animate_arm(anim_name="GIVE_HAND_NO_OPEN_HAND_BACK", arm=Arm.LEFT).started()

    logger.info("----------- Laugh and use TTS -----------")
    await robot.say("It's for you").completed()
    await robot.play_sound(SoundName.HAPPY_COOING).completed()


def handle_grasping_state(message: dict) -> None:
    """Handle updates to the grasping state."""
    global grasping_state
    if message != grasping_state:
        logger.info(f"Grasping State: {pformat(message['data'])}")
        grasping_state = message


def handle_navigation_state(message: dict) -> None:
    """Handle updates to the navigation state."""
    global navigation_state
    if message != navigation_state:
        logger.info(f"Navigation State: {pformat(message['data'])}")
        navigation_state = message


def handle_battery_voltage(message: dict) -> None:
    """Handle updates to the battery voltage."""
    global battery_state
    if message != battery_state:
        logger.info(f"Battery voltage: {pformat(message['data'])}")
        battery_state = message


async def main() -> None:
    """Main entry point for the script."""
    load_dotenv()
    ip = os.getenv("ROBOT_IP")
    if ip:
        logger.info(f"trying to start on host:{ip}")
    else:
        ip = get_local_ip()
        logger.info(f"trying to start on simulation, host:{ip}")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-i",
        "--ip",
        help="Set the IP of the robot you want to connect.",
        type=str,
        default=ip,
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Set the API key of the robot you want to connect.",
        type=str,
        default=os.getenv("PYMIROKAI_API_KEY", ""),
    )
    args = parser.parse_args()
    await run(ip=args.ip, api_key=args.api_key)


if __name__ == "__main__":
    run_until_interruption(main)
