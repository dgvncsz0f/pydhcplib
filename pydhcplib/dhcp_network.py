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

import socket
import select
import struct

# from asm-generic/socket.h
SO_BINDTODEVICE = 25

from pydhcplib import dhcp_packet, type_ipv4, interface, _rawsocket


class DhcpNetwork():
    def __init__(self, ifname, listen_address="0.0.0.0", listen_port=67, emit_port=68):
        super().__init__()
        self.ifname = ifname
        self.listen_port = int(listen_port)
        self.emit_port = int(emit_port)
        self.listen_address = listen_address
        self.so_reuseaddr = False
        self.so_broadcast = True
        self.dhcp_socket = None

    # Networking stuff
    def CreateSocket(self, so_broadcast, so_reuseaddr):
        dhcp_socket = None
        try:
            dhcp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error as msg:
            raise Exception( 'pydhcplib.DhcpNetwork socket creation error : ' + str(msg) )

        try:
            if so_broadcast:
                dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except socket.error as msg:
            raise Exception('pydhcplib.DhcpNetwork socket error in setsockopt SO_BROADCAST : ' + str(msg))

        try:
            if so_reuseaddr:
                dhcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as msg:
            raise Exception('pydhcplib.DhcpNetwork socket error in setsockopt SO_REUSEADDR : ' + str(msg))

        return dhcp_socket

    def EnableReuseaddr(self):
        self.so_reuseaddr = True

    def DisableReuseaddr(self):
        self.so_reuseaddr = False

    def EnableBroadcast(self):
        self.so_broadcast = True

    def DisableBroadcast(self):
        self.so_broadcast = False

    def BindToDevice(self):
        try:
            self.dhcp_socket.setsockopt(socket.SOL_SOCKET, SO_BINDTODEVICE, self.ifname)
        except socket.error as msg:
            raise Exception( 'pydhcplib.DhcpNetwork.BindToDevice error in setsockopt SO_BINDTODEVICE : ' + str(msg))

        try:
            self.dhcp_socket.bind(('', self.listen_port))
        except socket.error as msg:
            raise Exception( 'pydhcplib.DhcpNetwork.BindToDevice error : ' + str(msg))

    def BindToAddress(self):
        try:
            self.dhcp_socket.bind((self.listen_address, self.listen_port))
        except socket.error as msg:
            raise Exception( 'pydhcplib.DhcpNetwork.BindToAddress error : ' + str(msg))

    def GetNextDhcpPacket(self, timeout=60):
        data = ""

        while data == "":

            data_input, data_output, data_except = select.select([self.dhcp_socket], [], [], timeout)

            if( data_input != [] ):
                (data, source_address) = self.dhcp_socket.recvfrom(2048)
            else:
                return None

            if data != "":
                packet = dhcp_packet.DhcpPacket()
                packet.source_address = source_address
                packet.DecodePacket(data)

                self.HandleDhcpAll(packet)

                if packet.IsDhcpDiscoverPacket():
                    self.HandleDhcpDiscover(packet)
                elif packet.IsDhcpRequestPacket():
                    self.HandleDhcpRequest(packet)
                elif packet.IsDhcpDeclinePacket():
                    self.HandleDhcpDecline(packet)
                elif packet.IsDhcpReleasePacket():
                    self.HandleDhcpRelease(packet)
                elif packet.IsDhcpInformPacket():
                    self.HandleDhcpInform(packet)
                elif packet.IsDhcpOfferPacket():
                    self.HandleDhcpOffer(packet)
                elif packet.IsDhcpAckPacket():
                    self.HandleDhcpAck(packet)
                elif packet.IsDhcpNackPacket():
                    self.HandleDhcpNack(packet)
                else:
                    self.HandleDhcpUnknown(packet)

                return packet

    def SendDhcpPacket(self, request, response):
        giaddr = ".".join(map(str, request.GetOption("giaddr")))
        ciaddr = ".".join(map(str, request.GetOption("ciaddr")))
        broadcast = ( request.GetOption("flags")[0] & 0x80 ) != 0

        # RFC2131 from section 4.1:
        # If the ’giaddr’ field in a DHCP message from a client is non-zero,
        # the server sends any return messages to the ’DHCP server’ port on the
        # BOOTP relay agent whose address appears in ’giaddr’. If the ’giaddr’
        # field is zero and the ’ciaddr’ field is nonzero, then the server
        # unicasts DHCPOFFER and DHCPACK messages to the address in ’ciaddr’.
        # If ’giaddr’ is zero and ’ciaddr’ is zero, and the broadcast bit is
        # set, then the server broadcasts DHCPOFFER and DHCPACK messages to
        # 0xffffffff. If the broadcast bit is not set and ’giaddr’ is zero and
        # ’ciaddr’ is zero, then the server unicasts DHCPOFFER and DHCPACK
        # messages to the client’s hardware address and ’yiaddr’ address.  In
        # all cases, when ’giaddr’ is zero, the server broadcasts any DHCPNAK
        # messages to 0xffffffff.
        #
        # however some dhcp relay programs ( notably dhcp-helper:simon@thekelleys.org.uk
        # and isc-dhcp-relay) set the giaddr to the ip of the interface on
        # which it recieved the broadcast, in some cases that ip is non routable
        # from where the dhcp server is (ie: behind a NAT).  I think cisco's dhcp
        # relay can be setup to send from the interface facing the server (in ciso
        # terms the dhcp-helper)
        #
        # one solution, at lease for opnsense is to make a static route on the dhcp
        # server to the dhcp relay's front facing ip.

        if ( giaddr != "0.0.0.0" ):
            self.SendDhcpPacketTo( response, giaddr, self.listen_port )

        elif ( response.IsDhcpNackPacket() ):
            self.SendDhcpPacketTo( response, "255.255.255.255", self.emit_port)

        elif ( ciaddr != "0.0.0.0" ):
            self.SendDhcpPacketTo( response, ciaddr, self.emit_port )

        elif broadcast:
            #self.SendDhcpPacketTo( response, "255.255.255.255", self.emit_port )

            chaddr = struct.pack( 6 * "B", *request.GetOption("chaddr")[0:6] )

            ifconfig = interface.interface()
            ifindex = ifconfig.getIndex(self.ifname)
            ifaddr = ifconfig.getAddr(self.ifname)
            if (ifaddr is None):
                ifaddr = "0.0.0.0"

            _rawsocket.udp_send_packet( response.EncodePacket(),
                                        type_ipv4.ipv4(ifaddr).int(),
                                        self.listen_port,
                                        type_ipv4.ipv4("255.255.255.255").int(),
                                        self.emit_port,
                                        chaddr,
                                        ifindex
                                        )

        else:  # unicast to yiaddr
            yiaddr = ".".join(map(str, response.GetOption("yiaddr")))
            chaddr = struct.pack( 6 * "B", *request.GetOption("chaddr")[0:6] )

            ifconfig = interface.interface()
            ifindex = ifconfig.getIndex(self.ifname)
            ifaddr = ifconfig.getAddr(self.ifname)
            if (ifaddr is None):
                ifaddr = "0.0.0.0"

            _rawsocket.udp_send_packet( response.EncodePacket(),
                                        type_ipv4.ipv4(ifaddr).int(),
                                        self.listen_port,
                                        type_ipv4.ipv4(yiaddr).int(),
                                        self.emit_port,
                                        chaddr,
                                        ifindex
                                        )

    def SendDhcpPacketTo(self, packet, _ip, _port):
        return self.dhcp_socket.sendto( packet.EncodePacket(), ( _ip, _port ) )

    # Server side Handle methods
    def HandleDhcpDiscover(self, packet):
        pass

    def HandleDhcpRequest(self, packet):
        pass

    def HandleDhcpDecline(self, packet):
        pass

    def HandleDhcpRelease(self, packet):
        pass

    def HandleDhcpInform(self, packet):
        pass

    # client-side Handle methods
    def HandleDhcpOffer(self, packet):
        pass

    def HandleDhcpAck(self, packet):
        pass

    def HandleDhcpNack(self, packet):
        pass

    # Handle unknown options or all options
    def HandleDhcpUnknown(self, packet):
        pass

    def HandleDhcpAll(self, packet):
        pass


class DhcpServer(DhcpNetwork):
    def __init__(self, ifname, listen_address="0.0.0.0", client_listen_port=68, server_listen_port=67):
        super().__init__(ifname, listen_address, server_listen_port, client_listen_port)

        self.EnableBroadcast()
        self.DisableReuseaddr()

        self.dhcp_socket = self.CreateSocket(self.so_broadcast, self.so_reuseaddr)
        self.BindToAddress()


class DhcpClient(DhcpNetwork):
    def __init__(self, ifname=None, listen_address="0.0.0.0", client_listen_port=68, server_listen_port=67):
        super().__init__(ifname, listen_address, client_listen_port, server_listen_port)

        self.EnableBroadcast()
        self.EnableReuseaddr()

        self.dhcp_socket = self.CreateSocket(self.so_broadcast, self.so_reuseaddr)
