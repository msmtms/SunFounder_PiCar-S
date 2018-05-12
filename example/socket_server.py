from picar import front_wheels
from picar import back_wheels
import picar
import Pyro4
import json


@Pyro4.expose
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
        message = json.load(message)
        event = message['event']
        reset = message['reset']
        if not reset:
            if event in self.key_map:
                if not self.key_map[event]:
                    if event in self.movement_dispatch:
                        print "Moving car"
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

    @Pyro4.expose
    def accelerate(self):
        print "accelerating"
        self.bw.speed = 70
        self.bw.forward()

    @Pyro4.expose
    def decelerate(self):
        self.bw.speed = 70
        self.bw.backward()

    @Pyro4.expose
    def turn_left(self):
        self.fw.turn(135)

    @Pyro4.expose
    def turn_right(self):
        self.fw.turn(45)

    @Pyro4.expose
    def stop(self):
        self.bw.speed = 0

    @Pyro4.expose
    def turn_straight(self):
        self.fw.turn(90)


obj = CarControl()
Pyro4.Daemon.serveSimple(
    {
        obj: None             # register one specific instance
    },
    ns=False,
    host="192.168.1.32",
    port=9999
)
