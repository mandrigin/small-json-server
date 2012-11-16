import json
import logging
import os
import sys

import SimpleHTTPServer
import SocketServer


from optparse import OptionParser

MESSAGE_KEY    = 'message'
VERSION_KEY    = 'version'
IMAGE_PATH_KEY = 'image'

IMAGE_PATH      = 'get_image'

JSON_PATH = 'get_json'


class JsonHttpServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):


    def do_GET(self):

        if self.path.startswith('/'):
            self.path = self.path[1:]

        print self.path
        
        if self.path == JSON_PATH:
            self.wfile.write(str({MESSAGE_KEY : self.message, VERSION_KEY: self.version}))
            self.wfile.flush()
        elif self.path == IMAGE_PATH:
            image_file_obj = open(self.image_filepath, 'rb')
            self.wfile.write(image_file_obj.read())
            self.wfile.flush()
        else:
            self.wfile.write("Not found")
            self.wfile.flush()
            


def main():
    parser = OptionParser()
    parser.add_option( '-f', '--file'
                     , dest='file_to_monitor'
                     , help='File to be monitored and sent to user')

    (options, args) = parser.parse_args()

    filepath = options.file_to_monitor

    if filepath is not None:

        if os.path.exists(filepath):
            file_obj = open(filepath, 'r')

            try:
                file_json_dict = json.loads(file_obj.read())
            except:
                logging.exception("Error in file's json syntax!")
            else:
                if check_dictionary(file_json_dict, [ MESSAGE_KEY, VERSION_KEY, IMAGE_PATH_KEY ]):
                    message        = file_json_dict[MESSAGE_KEY]
                    version        = file_json_dict[VERSION_KEY]
                    image_filepath = file_json_dict[IMAGE_PATH_KEY]

                    if os.path.exists(image_filepath):
                        start_server(message, version, image_filepath)

                    else:
                        logging.fatal("No image file at path %s" % image_filepath)

                else:
                    logging.fatal(
                            "Wrong format of the JSON file: should have keys: %s, %s, %s" % (MESSAGE_KEY, VERSION_KEY, IMAGE_PATH_KEY))
        else:
            logging.fatal("File %s does not exists!" % filepath) 
    else:
        logging.fatal("Argument -f not specified!.\nUsage python small-json-server.py -f <FILENAME>")


def start_server(message, version, image_filepath):
    port = 8001 

    handler = JsonHttpServerHandler
    handler.message = message
    handler.version = version
    handler.image_filepath = image_filepath

    httpd = SocketServer.TCPServer(("", port), handler)

    logging.info("Starting server @ port %s" % port)

    httpd.serve_forever()


def check_dictionary(dict_, keys):
    for key in keys:
        if dict_.get(key, None) is None:
            return False

    return True




if __name__ == '__main__':
    main()
