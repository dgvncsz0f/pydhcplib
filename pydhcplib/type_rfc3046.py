# initial stub, right now I only care about getting it to a string
import re
import string

printable = re.compile( '[^{0}]'.format( string.printable ) )


class rfc3046:
  def __init__( self, data ):
    str_type = type( data )
    self.remote = '00:00:00:00:00:00'
    self.slot = 0
    self.port = 0
    self.subport = 0
    self.sp_index = 0
    self.vlan = 0
    self.misc = None

    if str_type == tuple or str_type == dict:
      if str_type == tuple:
        self.remote = str( data[0] )  # FIXME: some checking of the tuple would be good
        self.slot = int( data[1] )
        self.port = int( data[2] )
        self.subport = int( data[3] )
        self.sp_index = int( data[4] )
        self.vlan = int( data[5] )
        self.misc = data[6]
      else:
        self.remote = str( data[ 'remote' ] )
        self.slot = int( data[ 'slot' ] )
        self.port = int( data[ 'port' ] )
        self.subport = int( data[ 'subport' ] )
        self.sp_index = int( data[ 'sp_index' ] )
        self.vlan = int( data[ 'vlan' ] )
        self.misc = data[ 'misc' ]

    elif str_type == list:
      tmploc = 0
      while tmploc < len( data ):
        subopt = data[ tmploc ]
        sublen = data[ tmploc + 1 ]
        tmploc += 2

        if subopt == 1:  # circuit ID
          # the first two are cisco formats with defined circuit id types
          # seen formats vlan-XXXX  vlanXXXX
          # this is something we manually configure in the switches to help dhcp know what vlan a DHCP request started on for times when regualr snooping isn't aviable
          # also misc-XXXX, misc XXXXX, miscXXXX
          if ( sublen >= 7 ) and ( data[ tmploc ] == 1 ):  # Circuit type = 1, http://www.cisco.com/c/en/us/td/docs/ios-xml/ios/ipaddr_dhcp/configuration/15-s/dhcp-15-s-book/dhcp-option-82.html
            id = ''.join( [ chr( i ) for i in data[ tmploc + 2: sublen + 2 ] ] )
            id = printable.sub( '', id )
            if id[ 0:4 ].lower() == 'vlan':
              self.vlan = int( re.sub( '[^0-9]', '', id ) )

            elif id[ 0:4 ].lower() == 'misc':
              self.misc = id[ 4: ]
              if self.misc[0] in ( ' ', '-' ):
                self.misc = self.misc[ 1: ]

            else:
              raise Exception( 'Unknown Circuit Id Type 1 format: "%s"' % id )

          # cisco vlan-mod-port
          # NOTE: if vlan-mod-port isn't aviable and ifindex is, disabeling ifindex should enable vlan-mod-port
          elif ( sublen == 6 ) and ( data[ tmploc ] == 0 ) and ( data[ tmploc + 1 ] == 4 ):  # Circuit ID Type = 0, len = 4, CISCO Format, http://www.cisco.com/en/US/docs/switches/lan/catalyst6500/ios/12.2SX/configuration/guide/snoodhcp.html#wp1108657
            self.vlan = ( ( data[ tmploc + 2 ] & 0x0f ) << 8 ) + data[ tmploc + 3 ]
            # if it's a fex:
            self.slot = data[ tmploc + 4 ] + 67  # if there is some way to detect that this is a FEX port, add 67, for somereason fex slots are the fex id - 67
            self.port = 1
            self.subport = data[ tmploc + 5 ]
            # if not a fex slot = tmpLoc + 4 and port = temploc + 5

          # Cisco snmp-ifindex
          # see http://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst3550/software/release/12-2_25_se/configuration/guide/3550scg/swdhcp82.html#wp1119490
          elif sublen == 4:
            if ( data[ tmploc ] == 9 ) and ( data[ tmploc + 1 ] == 1 ):  # this range of snmp-ifindex is a vlan
              self.vlan = ( ( data[ tmploc + 2 ] & 0x0f ) << 8 ) + data[ tmploc + 3 ]

            else:
              self.sp_index = ( data[ tmploc ] << 24 ) + ( data[ tmploc + 1 ] << 16 ) + ( data[ tmploc + 2 ] << 8 ) + data[ tmploc + 3 ]

          # this one is used by arista, no circuit type field
          elif ( sublen > 6 ):  # see Cisco Circuit Type = 1
            id = ''.join( [ chr( i ) for i in data[ tmploc: sublen + 2 ] ] )
            id = printable.sub( '', id )
            if id[ 0:4 ].lower() == 'vlan':
              self.vlan = int( re.sub( '[^0-9]', '', id ) )

            elif id[ 0:4 ].lower() == 'misc':
              self.misc = id[ 4: ]
              if self.misc[0] in ( ' ', '-' ):
                self.misc = self.misc[ 1: ]

            else:  # vyos/isc-dhcp-relay just puts in the interface it was recieved on ie: eth1.102
              self.misc = id  # catch everything else -
              # raise Exception( 'Unknown other sublen format: "{0}"'.format( id ) )

          # another unknown format that seems to come from cisco Circuit-ID :  00:00:16:00:00:XX
          # Have been unable to figure out what switch is putting it on, and what it means, so we are punting, firt 3 bytes -> slot  last 3 byts -> port
          elif sublen == 6:
            self.port = ( data[ tmploc + 3 ] << 16 ) + ( data[ tmploc + 4 ] << 8 ) + data[ tmploc + 5 ]
            self.slot = ( data[ tmploc + 0 ] << 16 ) + ( data[ tmploc + 1 ] << 8 ) + data[ tmploc + 2 ]

          else:
            raise Exception( 'Unknwon subopt 1 format' )

        elif subopt == 2:  # Remote-ID
          if ( sublen == 8 ) and ( data[ tmploc ] == 0 ) and ( data[ tmploc + 1 ] == 6 ):  # Remote ID Type = 0, len = 6, CISCO Format
            self.remote = ':'.join( [ "{0:02x}".format( i ) for i in data[ tmploc + 2: tmploc + 8 ] ] )

          # Cisco NX does this when it is using if_index
          # Arista uses this format
          elif sublen == 6:
            self.remote = ':'.join( [ "{0:02x}".format( i ) for i in data[ tmploc: tmploc + 6 ] ] )

          else:
            raise Exception( 'Unknown subopt 2 format' )

        else:
          raise Exception( 'Unknown subopt type "{0}"'.format( subopt ) )

        tmploc += sublen

    else:
      raise TypeError( 'rfc3046 init: Valid types are tuple, dict and list of int' )

  # return string
  def str( self ):
    return 'Vlan: {0} Slot: {1} Port: {2} Subport: {3} SwitchPort Index: {4} Remote Id: {5} Misc: {6}'.format( self.vlan, self.slot, self.port, self.subport, self.sp_index, self.remote, self.misc )

  def tuple( self ):
    return ( self.remote, self.slot, self.port, self.subport, self.sp_index, self.vlan, self.misc )

  def dict( self ):
    return { 'remote': self.remote, 'slot': self.slot, 'port': self.port, 'subport': self.subport, 'sp_index': self.sp_index, 'vlan': self.vlan, 'misc': self.misc }

  # return list (useful for DhcpPacket class)
  # can't really go back
  def list( self ):
    return []

  """ Useful function for native python operations """

  def __hash__( self ):
    return self.tuple().__hash__()

  def __repr__( self ):
    return self.str()

  def __str__( self ):
    return self.str()

  def __cmp__( self, other ):
    return self.__hash__ == other.__hash__
