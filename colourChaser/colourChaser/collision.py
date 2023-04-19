#!/usr/bin/env python

#twist mux is used to help with ros topics for requires downloading to root on every launch 
# download guide below 
# sudo apt update
# sudo apt install ros-humble-twist-mux

# This code was adapted from scripts found on this github page 
#https://github.com/LCAS/teaching/tree/lcas_humble/cmp3103m_ros2_code_fragments


import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class collisionAvoidance(Node):
    def __init__(self):

        super().__init__('collisionAvoidance')
        # Create a publisher for the twist message
        self.twist_pub = self.create_publisher(Twist, 'collision_vel', 10)
        # Create a subscriber for the laser scan message
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.collisionCallback, 10)

    def collisionCallback(self, msg):

        # initialize the collisionDetected variable to False
        collisionDetected = False

        # create a new instance of the Twist() class to set the robot's velocity
        robotMove = Twist()

        # check if the range value at the front of the robot is greater than 0.8
        forwardView = msg.ranges[0] > 0.7
        
        # check range values from the front of the robot to 60 degrees to the left and right
        for empty in range(60):
            # If all the range values are greater than 0.7, set forwardView to True
            forwardView = forwardView and msg.ranges[empty] > 0.7
            forwardView = forwardView and msg.ranges[-empty] > 0.7

        # check range values at different angular rotations
        for angularRotation in range(0, len(msg.ranges), 30):

            # if an obstacle is detected in front and the front view is clear, move forward
            if (msg.ranges[angularRotation] < 0.7 and forwardView):
                # print out message to show that the front of the robot is clear
                print(f"in front of the robot is clear")
                # set the robot's velocity to move forward
                robotMove.linear.x = 0.25
                robotMove.angular.z = 0.0

                collisionDetected = False

            # if an obstacle is detected and the front view is not clear, stop and turn the robot
            elif (msg.ranges[angularRotation] < 0.7 or forwardView == False):
                # print out message to show that the front of the robot is not clear
                print(f"Collision detected at {angularRotation}")
                # set the robot's velocity to stop
                robotMove.linear.x = 0.0
                # set collisionDetected to True to indicate an obstacle is detected
                collisionDetected = True

                # decides which side of the robot is clear and turns the robot to the right or left
                # use more precise condition for angular rotation
                if 180 <= angularRotation <= 400: 
                    # turn the robot to the right
                    robotMove.angular.z = 0.3
                elif 0 <= angularRotation <= 180: 
                    # turn the robot to the left
                    robotMove.angular.z = -0.3
                else:
                    # use a default turn direction if angular rotation value is outside expected range
                    robotMove.angular.z = -0.3



        # output message 
        if collisionDetected == True:
            self.twist_pub.publish(robotMove)

def main(args=None):
    print('Starting collision.py.')

    rclpy.init(args=args)

    collision = collisionAvoidance()

    rclpy.spin(collision)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    collision.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()