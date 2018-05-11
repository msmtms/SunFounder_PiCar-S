import socket
import json
from pynput import keyboard


class KeyHandler:
    HOST, PORT = "192.168.1.32", 9999

    def __init__(self):
        super(KeyHandler, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.HOST, self.PORT))
        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as self.listener:
            self.listener.join()

    def on_press(self, key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
        except AttributeError:
            message = dict()
            message['event'] = str(key)
            message['reset'] = False
            self.socket.sendall(json.dumps(message))

    def on_release(self, key):
        message = dict()
        message['event'] = str(key)
        message['reset'] = True
        self.socket.sendall(json.dumps(message))
        if key == keyboard.Key.esc:
            # Stop listener
            return False



