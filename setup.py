#!/usr/bin/env python
#
# $Id$
#
       
import ez_setup
ez_setup.use_setuptools()
                       
from setuptools import setup
VERSION="1.0.7"

setup(name="honeysnap",
    version=VERSION,
    author="Arthur Clune/Arthur Clune",
    author_email="honeysnap@honeynet.org",  
    url="https://projects.honeynet.org/honeysnap/", 
    description="A tool for analysing pcap files",
    long_description="Honeysnap helps an analyst with the task of analysing pcap files generated by a honeypot",
    license="GNU GPL",
    packages=["honeysnap"],
    include_package_data=True,

    install_requires = [
        "python-irclib>=0.4.6",
        "dpkt>=1.7", 
    ],
    dependency_links = [    
        "http://dpkt.googlecode.com/files/dpkt-1.7.tar.gz",
    ],
    entry_points = {
        'console_scripts': [
            'honeysnap = honeysnap.main:start',
	    'xBytesNseconds = honeysnap.xBytesNseconds:main',
	    'thresholdflows = honeysnap.thresholdflows:main'
          ]
    }
)    
