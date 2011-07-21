#!/usr/bin/python
#
# pydhcplib
# Copyright (C) 2008 Mathieu Ignacio -- mignacio@april.org
#
# This file is part of pydhcplib.
# Pydhcplib is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from pydhcplib.dhcp_packet import *
from pydhcplib.dhcp_network import *

netopt = {'client_listen_port':68,
           'server_listen_port':67,
           'listen_address':"0.0.0.0"}

class Client(DhcpClient):
    def __init__(self, options):
        DhcpClient.__init__(self,options["listen_address"],
                            options["client_listen_port"],
                            options["server_listen_port"])
        
    def HandleDhcpOffer(self, packet):
        print packet.str()
    def HandleDhcpAck(self, packet):
        print packet.str()
    def HandleDhcpNack(self, packet):
        print packet.str()        

client = Client(netopt)
# Use BindToAddress if you want to emit/listen to an internet address (like 192.168.1.1)
# or BindToDevice if you want to emit/listen to a network device (like eth0)
client.BindToAddress()

while True :
    client.GetNextDhcpPacket()
    print client.str()
