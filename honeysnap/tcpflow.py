################################################################################
# (c) 2005, The Honeynet Project
#   Author: Jed Haile  jed.haile@thelogangroup.biz
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
################################################################################

# $Id$

import os
import socket
import pcap
import dpkt
from flow import flow, flow_state, flow_state_manager, reverse, fileHandleError

FLOW_FINISHED=(1 << 0)
FLOW_FILE_EXISTS=(1 << 1)

class tcpFlow(object):

    def __init__(self, pcapObj):
        """Initialise the flow. Assume ethernet for now"""
        self.p = pcapObj
        self.states = flow_state_manager()
        self.outdir = ""
        self.fname = []
        self.plugins = []
        
    def __del__(self):
        pass

    def registerPlugin(self, cb):
        """
        cb is a function that takes an instance of flow_state as an arg
        """
        self.plugins.append(cb)

    def packetHandler(self, ts, buf):
        """Process a pcap packet buffer"""
        try:
            pkt = dpkt.ethernet.Ethernet(buf)
            subpkt = pkt.data
            if type(subpkt) != type(dpkt.ip.IP()):
                # skip non IP packets
                return
            proto = subpkt.p
            shost = socket.inet_ntoa(subpkt.src)
            dhost = socket.inet_ntoa(subpkt.dst)
        except dpkt.Error: 
            return

        if proto == socket.IPPROTO_TCP:
            self.process_tcp(pkt, shost, dhost)

    def process_ip(self, pkt):
        """Process a dpkt.ip.IP object"""
        pass

    def process_tcp(self, pkt, src, dst):
        """Process a tcp packet"""
        ip = pkt.data
        tcp = ip.data
        this_flow = flow()
        this_flow.src = src
        this_flow.dst = dst
        this_flow.sport = tcp.sport
        this_flow.dport = tcp.dport
        if ip.len == ip.__hdr_len__ + tcp.__hdr_len__:
            # no data, return
            return
        self.store_packet(this_flow, tcp)
        
    def store_packet(self, flow, tcp):
        """Store a packet in a flow"""
        bytes_per_flow = 100000000
        seq = tcp.seq
        data = tcp.data
        if len(data) <= 0 :
            # no data, move along
            return
        length = len(data)
        state = self.states.find_flow_state(flow)
        if state is None:
            #print "state not found, creating new"
            state = self.states.create_state(flow, seq)
            state.open()
            #else:
            #print "state found"

        if state.flags&FLOW_FINISHED:
            # print "flow finished: %s" % state.flow
            # TODO: Open a new state??
            if tcp.flags & 2:   # SYN
                print "new flow on prior state: %s" % state.flow
            state.close()
            return

        if tcp.flags & 1 or tcp.flags & 4: # FIN or RST
            # conection finished
            # close the file
            # print "got RST or FIN"
            state.flags |= FLOW_FINISHED
            state.fp.flush()
            state.close()
            return

        offset = seq - state.isn
        if offset < 0:
            # seq < isn, drop it
            # print "bad seq number"
            return 

        if bytes_per_flow and (offset > bytes_per_flow):
            # too many bytes for this flow, drop it
            #print "too many bytes for flow, dropping packet"
            state.flags |= FLOW_FINISHED   
            state.close()
            return

        if bytes_per_flow and (offset + length > bytes_per_flow):
            # long enough, mark this flow finished
            #print "flow marked finished due to length"
            state.flags |= FLOW_FINISHED
            state.close()
            length = bytes_per_flow - offset 
            return

        try:
            state.open()
        except fileHandleError:
            self.states.closeFiles()
            state.open()
        state.writeData(data)
    
    def start(self):
        """Iterate over a pcap object"""
        for ts, buf in self.p:
            self.packetHandler(ts, buf)
        
    def setFilter(self, filter):
        self.p.setfilter(filter)

    def setOutdir(self, dir):
        self.outdir = dir
        self.states.setOutdir(dir)
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)

    def setOutput(self, file):
        self.outfile = file

    def dump_extract(self, options):
        for s in self.states.flow_hash.values():
            for func in self.plugins:
                func(s, self.states)
                                        
    def writeResults(self):
        """TODO: I would like to implement some sort of summarization
        of the data files that were written during the run...
        """
        pass

if __name__ == "__main__":
    import sys
    f = sys.argv[1]
    pcapObj = pcap.pcap(f)
    tflow = tcpFlow(pcapObj)
    tflow.setFilter("not port 445")
    tflow.start()

