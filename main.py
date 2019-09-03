#
# Copyright 2019 Genentech Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Genentech Warp Watcher

Minimal Tornado App to watch a directory and update with new files.

Author: Benjamin Barad <benjamin.barad@gmail.com>/<baradb@gene.com>
"""


import datetime
import json
import os
import sys

from tornado.httpserver import HTTPServer
import tornado.ioloop
import tornado.template
from tornado.web import Application, RequestHandler, StaticFileHandler
from tornado.websocket import WebSocketHandler
from tornado.options import options, define, parse_command_line

define('port', default=8182, help='Port to listen on')
define('thumbnail_count', default=200, help="Number of thumbnails to show")
define('reload_rate', default=120000, help="How often to reload thumbnails, in ms")
define('parent_path', type=str, help="Parent directory for warp jobs")

# Set up globals for use throughout the program
body_html = ""
static_path = {"path": "/tmp/thumbnails"}
warp_path = ["/tmp"]
settings = {"websocket_ping_interval": 30}
clients = set()
loader = tornado.template.Loader(".")
string_loader = loader.load("template.html")
options.parse_command_line()

async def change_warp_path(new_path):
    if not os.path.exists(os.path.join(options.parent_path, new_path, "thumbnails")):
        print("No Thumbnail Directory Found")
        return False
    else:
        warp_path[0] = os.path.join(options.parent_path, new_path)
        static_path["path"] = os.path.join(options.parent_path, new_path, "thumbnails")
        print(f"New Warp Directory: {warp_path[0]}")
    return True

async def update_html_string(path, linecount=200):
    thumbnail_dir = os.path.join(path, "thumbnails")
    if not os.path.exists(thumbnail_dir):
        await message_all_clients({"type": "alert", "data": "Could not find thumbnails in the chosen directory"})
        return
    files = [file for file in os.listdir(thumbnail_dir) if (file.lower().endswith('.png'))]
    files.sort(key=lambda x: os.path.getctime(os.path.join(thumbnail_dir, x)), reverse=False)
    total_count = len(files)
    if linecount > total_count:
        linecount = total_count
    return_list = [{"number": len(files)-i,"timestamp": datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(thumbnail_dir, j))).strftime('%Y-%m-%d %H:%M:%S'), "name": j[:-4], "url": os.path.join("/gallery/", j)} for i,j in enumerate(files[:linecount])]
    warp_name = os.path.split(path)[1]

    body_html = string_loader.generate(thumbnail_list = return_list, warp_name = warp_name, line_count = linecount, total_count = total_count).decode("utf-8")
    print("Updating Client HTML")
    await message_all_clients({"type": "gallery", "data": body_html})

async def get_body_html():
    return body_html

async def message_all_clients(message, clients = clients):
    """
    Send a message to all open clients, and close any that respond with closed state.

    Args:
        message (str or dict): a websocket-friendly message.
        clients (set): a set of websockethandler instances that should represent every open session.
    """
    for client in list(clients):
        try:
            client.write_message(message)
        except WebSocketClosedError:
            logging.warn(f"Could not write a message to client {client} due to a WebSocketClosedError. Removing that client from the client list.")
            clients.remove(client)


class IndexHandler(RequestHandler):
    """Core class to respond to new clients."""
    def get(self):
        """Minimal handler for setting up the very first connection via an HTTP request before setting up the websocket connection for all future interactions."""
        self.render("index.html")

class SocketHandler(WebSocketHandler):
    """Primary Web Server control class - every new client will make initialize of these classes.
    Extends :py:class:`tornado.websocket.WebSocketHandler`
    """
    def open(self):
        """Adds new client to a global clients set when socket is opened."""
        clients.add(self)
        print("Socket Opened from {}".format(self.request.remote_ip))

    async def on_message(self, message):
        message_json = json.loads(message)
        command = message_json['command']
        data = message_json['data']
        if command == "change_directory":
            if await change_warp_path(data):
                print(warp_path[0])
                await update_html_string(warp_path[0], linecount=options.thumbnail_count)
            else:
                self.write_message({"type": "alert", "data": "Couldn't find a thumbnails folder in that directory - has Warp run there?"})
        elif command == "initialize":
            print("initializing with body html:")
            await update_html_string(warp_path[0], linecount=options.thumbnail_count)
        else:
            self.write_message({"type": "alert", "data": "Didn't understand that message"})
    def on_close(self):
        """Remove sockets from the clients list to minimize errors."""
        clients.remove(self)
        print("Socket Closed from {}".format(self.request.remote_ip))



def main():
    """Construct and serve the tornado app"""
    app = Application([(r"/", IndexHandler), (r"/gallery/(.*)", StaticFileHandler, static_path), (r"/static/(.*)", StaticFileHandler, {"path": os.path.join(sys.path[0], "static")}), (r"/websocket", SocketHandler)], **settings)
    app.listen(options.port)
    listening_callback = tornado.ioloop.PeriodicCallback(lambda:     update_html_string(warp_path[0], linecount=options.thumbnail_count), options.reload_rate)
    listening_callback.start()

    print(f'Listening on http://localhost:{options.port}')

    tornado.ioloop.IOLoop.current().start()



if __name__ == "__main__":
    main()
