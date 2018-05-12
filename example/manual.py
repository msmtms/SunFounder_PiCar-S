import json
from pynput import keyboard
import Pyro4


class KeyHandler:
    HOST, PORT = "192.168.1.32", "9999"
    FORWARD = 'Key.up'
    BACKWARD = 'Key.down'
    LEFT = 'Key.left'
    RIGHT = 'Key.right'

    def __init__(self):
        super(KeyHandler, self).__init__()
        uri = "PYRO:obj_3f80d0dae05a41db9037b0a4b3468c6c@192.168.1.32:9999"
        self.conn = Pyro4.Proxy(uri)
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
        self.key_map[self.FORWARD] = False
        self.key_map[self.BACKWARD] = False
        self.key_map[self.LEFT] = False
        self.key_map[self.RIGHT] = False
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
        except AttributeError:
            event = str(key)
            if event in self.key_map:
                if not self.key_map[event]:
                    self.key_map[event] = True
                    self.movement_dispatch[event]()

    def on_release(self, key):
        event = str(key)
        if event in self.key_map:
            if self.key_map[event]:
                self.key_map[event] = False
                self.movement_reset[event]()
        if key == keyboard.Key.esc:
            # Stop listener
            return False

    def accelerate(self):
        print("sending accelerate")
        self.conn.accelerate()

    def decelerate(self):
        self.conn.decelerate()

    def turn_left(self):
        self.conn.turn_left()

    def turn_right(self):
        self.conn.turn_right()

    def stop(self):
        self.conn.stop()

    def turn_straight(self):
        self.conn.turn_straight()


handler = KeyHandler()
