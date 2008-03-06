#!/usr/bin/env python
#
# $Id$
#
       
import ez_setup
ez_setup.use_setuptools()
                       
from setuptools import setup
VERSION="1.0.6.13"

setup(name="honeysnap",
    version=VERSION,
    author="Jed Hale/Arthur Clune",
    author_email="honeysnap@honeynet.org",  
    url="http://www.honeynet.org/tools/honeysnap", 
    description="A tool for analysing pcap files",
    long_description="Honeysnap helps an analyst with the task of analysing pcap files generated by a honeypot",
    license="GNU GPL",
    packages=["honeysnap"],
    scripts = [
        'scripts/xBytesNseconds.py',
        'scripts/threshholdflows.py',
    ],    
    include_package_data=True,

    install_requires = [
        "python-irclib>=0.4.6",
        "dpkt>=1.6", 
    ],
    dependency_links = [    
        "http://dpkt.googlecode.com/files/dpkt-1.6.tar.gz",
    ],
    entry_points = {
        'console_scripts': [
            'honeysnap = honeysnap.main:start',
          ]
    }
)    
