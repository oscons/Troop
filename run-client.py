#!/usr/bin/env python
"""
    Troop-Client
    ------------
    Real-time collaborative Live Coding.

    - Troop is a real-time collaborative tool that enables group live
      coding within the same document. To run the client application it
      must be able to connect to a running Troop Server instance on
      your network. Running `python run-client.py` will start the process
      of connecting to the server by asking for a host and port (defaults
      are localhost and port 57890). 

    - Using other Live Coding Languages:
    
        Troop is designed to be used with FoxDot (http://foxdot.org) but
        is also configured to work with Tidal Cycles (http://tidalcycles.org).
        You can run this file with the `--mode` flag followed by "tidalcycles"
        to use the Tidal Cycles language. You can also use any other application
        that can accept code commands as strings via the stdin by specifying
        the path of the interpreter application, such as ghci in the case of
        Tidal Cycles, in place of the "tidalcycles" string when using the
        `--mode` flag.
"""

import argparse

default_config_file_name = 'client.cfg'

parser = argparse.ArgumentParser(
    prog="Troop Client", 
    description="Collaborative interface for Live Coding")

parser.add_argument('-i', '--cli', action='store_true', help="Use the command line to enter connection info")
parser.add_argument('-p', '--public', action='store_true', help="Connect to public Troop server")
parser.add_argument('-H', '--host', action='store', help="IP Address of the machine running the Troop server")#, default="localhost")
parser.add_argument('-P', '--port', action='store', help="Port for Troop server (default 57890)")#, default=57890)
parser.add_argument('-m', '--mode', action='store', default='foxdot',
                    help='Name of live coding language (TidalCycles, SonicPi, SuperCollider, FoxDot, None, or a valid executable')
parser.add_argument('-a', '--args', action='store', help="Add extra arguments to supply to the interpreter", nargs=argparse.REMAINDER, type=str)
parser.add_argument('-c', '--config', action='store', help="Load connection info from '"+default_config_file_name+"' or provided file", nargs='?', default=None, const=default_config_file_name)
parser.add_argument('-l', '--log', action='store_true')

args = parser.parse_args()

# Set up client

from src.client import Client
from src.config import readin
from getpass import getpass

# Client config options

options = { 'lang': args.mode, 'logging': args.log }

if not args.config is None:
    import os.path
    
    if os.path.isfile(args.config):

        """
        You can set a configuration file if you are connecting to the same
        server on repeated occasions. A password should not be stored. The
        file (client.cfg) should look like:

        host=<host_ip>
        port=<port_no>

        """

        options.update(Client.read_configuration_file(args.config))
    else:
        print("Unable to load configuration from 'client.cfg'")

if args.public:

    from src.config import PUBLIC_SERVER_ADDRESS
    options['host'], options['port'] = PUBLIC_SERVER_ADDRESS  

if args.host:

    options['host'] = args.host

if args.port:

    options['port'] = args.port

if args.cli:

    if 'host' not in options:

        options['host']     = readin("Troop Server Address", default="localhost")

    if 'port' not in options:
    
        options['port']     = readin("Port Number", default="57890")

    if 'name' not in options:

        options['name']     = readin("Enter a name").replace(" ", "_")

    if 'password' not in options:

        options['password'] = getpass()

# Store any extra arguments to supply to the interpreter

if args.args:

    options['args'] = args.args

def get_string_type():
    import sys

    PY3 = sys.version_info[0] == 3

    if PY3:
        string_type = str
    else:
        string_type = basestring
    return string_type

required_options = ['host','port','name','password']
options['get_info'] = False
for y in [x in options.keys() for x in required_options]:
    if not y:
        options['get_info'] = True
        break

for (pn, pt) in [
    ('port', int)
    , ('get_info', lambda x: x.strip().lower() == 'true')
]:
    if pn in options.keys():
        if isinstance(options[pn], get_string_type()):
            options[pn] = pt(options[pn])


myClient = Client(**options)