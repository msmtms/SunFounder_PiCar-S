import SocketServer
from threading import Thread
from picar import front_wheels
from picar import back_wheels
import picar
import json
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write("<html><body><h1>hi!</h1></body></html>")

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        self._set_headers()
        print "received:", post_data
        car_control.event_handler(json.loads(post_data))
        self.wfile.write("received")


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



def run(server_class=HTTPServer, handler_class=S, port=9999):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

    car_control = CarControl()

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()

