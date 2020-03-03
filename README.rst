:: 

                   _ _                _ _ _
   _ __  _   _  __| | |__   ___ _ __ | (_) |__
  | '_ \| | | |/ _` | '_ \ / __| '_ \| | | '_ \
  | |_) | |_| | (_| | | | | (__| |_) | | | |_) |
  | .__/ \__, |\__,_|_| |_|\___| .__/|_|_|_.__/
  |_|    |___/                 |_|


===========
 Pydhcplib
===========

Pydhcplib is a python library to read/write and encode/decode dhcp
packet on network.

N.B. This is a fork of this project http://pydhcplib.tuxfamily.org/pmwiki/. The only change [so far] is the implementation of a missing feature as described in the end of this document [1_].

Installation :
==============

On Debian, simply run `./setup.py install`. Python modules will be
installed in /usr/lib/python3.X/site-packages/pydhcplib/.

If you want to install it on a different location, use the `--prefix`
on the `setup.py` command line like this::

  $ ./setup.py install --prefix=/rootpath/to/your/location/

Creating egg :
==============

  use virtualenv with correct python version
  $ python setup.py bdist_egg

How to use pydhcplib :
======================

Look in the examples directory to learn how to use the modules.::
  
  $ man pydhcp
  $ man pydhcplib

.. 1:

Differences to the original pydhcplib
=====================================

The short story is I've "stolen" the udp raw socket code from [the
amazing] *busybox* project changing it to work with the udp payload
[the actual dhcp packet] this library creates.

This was required to make it work in the case the fields `giaddr` and
`ciaddr` are zero and the broadcast bit flag is not set. This requires
unicasting the udp packet to the `yiaddr` address, which does not yet
exist. Using the kernel to send the packet fails as there is no ARP
information available.  This requires using raw sockets to inject the
missing `hwaddr` information.

