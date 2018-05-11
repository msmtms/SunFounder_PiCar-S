from pynput import keyboard
from threading import Thread
from picar import front_wheels
from picar import back_wheels
import picar


class CarControl:
    FORWARD = keyboard.Key.up
    BACKWARD = keyboard.Key.down
    LEFT = keyboard.Key.left
    RIGHT = keyboard.Key.right

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

        self.mapper = KeyHandler(self.event_handler, self.event_reset_handler)
        self.mapper.start()
        self.key_map = dict()

    def event_handler(self, event):
        if event in self.key_map:
            if not self.key_map[event]:
                if event in self.movement_dispatch:
                    self.movement_dispatch[event]()
        self.key_map[event] = True

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


class KeyHandler(Thread):

    def __init__(self, callback, stop_callback):
        super(KeyHandler, self).__init__()
        self.callback = callback
        self.stop_callback = stop_callback
        self.listener = None

    def run(self):
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        try:
            print 'alphanumeric key {0} pressed'.format(key.char)
        except AttributeError:
            self.callback(str(key))


    def on_release(self, key):
        self.stop_callback(str(key))
        if key == keyboard.Key.esc:
            # Stop listener
            return False



