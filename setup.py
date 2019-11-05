#!/usr/bin/env python3

from setuptools import setup
from distutils.core import Extension

fr8_manpages = ['man/fr/man8/pydhcp.8.gz']
fr3_manpages = ['man/fr/man3/pydhcplib.3.gz',
                'man/fr/man3/pydhcplib.DhcpBasicPacket.3.gz',
                'man/fr/man3/pydhcplib.DhcpPacket.3.gz',
                'man/fr/man3/pydhcplib.hwmac.3.gz',
                'man/fr/man3/pydhcplib.ipv4.3.gz',
                'man/fr/man3/pydhcplib.strlist.3.gz']
en3_manpages = ['man/man3/pydhcplib.strlist.3.gz',
                'man/man3/pydhcplib.3.gz',
                'man/man3/pydhcplib.ipv4.3.gz']
en8_manpages = ['man/man8/pydhcp.8.gz']

rawsocketmod = Extension( "pydhcplib._rawsocket",
                          sources = ["networking/rawsocket.c", "networking/rawsocketmod.c"]
                        )

setup(name='pydhcplib',
      version      = "0.7.1",
      license      = "GPL v3",
      description  = "Dhcp client/server library",
      author       = "Mathieu Ignacio, Diego Souza",
      author_email = "mignacio@april.org",
      url          = "http://github.com/dgvncsz0f/pydhcplib",
      packages     = ["pydhcplib"],
      scripts      = ["scripts/pydhcp"],
      ext_modules  = [rawsocketmod],
      data_files   = [("share/man/man8",en8_manpages),
                      #            ("share/man/fr/man8",fr8_manpages),
                      ("share/man/fr/man3",fr3_manpages),
                      ("share/man/man3",en3_manpages)
                     ])
