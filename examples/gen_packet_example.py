#!/usr/bin/python

from pydhcplib.dhcp_packet import DhcpPacket
from pydhcplib.type_strlist import strlist
from pydhcplib.type_ipv4 import ipv4


packet = DhcpPacket()

packet.SetOption( "op",[1])
packet.SetOption( "domain_name",strlist("anemon.org").list())
packet.SetOption( "router",ipv4("192.168.0.1").list()+[6,4,2,1])
packet.SetOption( "time_server",[100,100,100,7,6,4,2,1])
packet.SetOption( "yiaddr",[192,168,0,18])
packet.SetOption( "maximum_datagram_reassembly_size", [2,1])
packet.SetOption( "tcp_keepalive_interval", [8,4,2,1])


print(packet.str())
