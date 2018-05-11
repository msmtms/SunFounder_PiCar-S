import SocketServer
from threading import Thread
from picar import front_wheels
from picar import back_wheels
import picar
import json


class CarControl:
    FORWARD = 'Key.up'
    BACKWARD = 'Key.down'
    LEFT = 'Key.left'
    RIGHT = 'Key.right'

    def __init__(self):
        picar.setup()
        self.fw = front_wheels.Front_Wheels(db='config')
        self.bw = back_wheels.Back_Wheels(db='config')
        self.bw.speed = 70
        self.fw.turning_max = 45

        self.forward_speed = 70
        self.backward_speed = 70

        self.back_distance = 10
        self.turn_distance = 20
        self.straight = 90

        self.movement_dispatch = dict()
        self.movement_dispatch[self.FORWARD] = self.accelerate
        self.movement_dispatch[self.BACKWARD] = self.decelerate
        self.movement_dispatch[self.LEFT] = self.turn_left
        self.movement_dispatch[self.RIGHT] = self.turn_right

        self.movement_reset = dict()
        self.movement_reset[self.FORWARD] = self.stop
        self.movement_reset[self.BACKWARD] = self.stop
        self.movement_reset[self.LEFT] = self.turn_straight
        self.movement_reset[self.RIGHT] = self.turn_straight

        self.key_map = dict()

    def event_handler(self, message):
        event = message['event']
        reset = message['reset']
        if not reset:
            if event in self.key_map:
                if not self.key_map[event]:
                    if event in self.movement_dispatch:
                        self.movement_dispatch[event]()
            self.key_map[event] = True
        else:
            if event in self.key_map:
                if not self.key_map[event]:
                    if event in self.movement_reset:
                        self.movement_reset[event]()
            self.key_map[event] = False

    def event_reset_handler(self, event):
        if event in self.key_map:
            if not self.key_map[event]:
                if event in self.movement_reset:
                    self.movement_reset[event]()
        self.key_map[event] = False

    def accelerate(self):
        self.bw.speed = 70
        self.bw.forward()

    def decelerate(self):
        self.bw.speed = 70
        self.bw.backward()

    def turn_left(self):
        self.fw.turn(135)

    def turn_right(self):
        self.fw.turn(45)

    def stop(self):
        self.bw.speed = 0

    def turn_straight(self):
        self.fw.turn(90)


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def __init__(self):
        self.car_controller = CarControl()

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        message = json.loads(self.data)
        self.car_controller.event_handler(message)


if __name__ == "__main__":
    HOST, PORT = "192.168.1.32", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
