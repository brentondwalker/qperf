#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import CPULimitedHost
from mininet.node import Node
from mininet.util import dumpNodeConnections
from mininet.cli import CLI
from mininet.log import setLogLevel, info

# based on the mininet linuxrouter example
# https://github.com/mininet/mininet/blob/master/examples/linuxrouter.py

class LinuxRouter(CPULimitedHost):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        # Add a router connecting two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.0.1/24')

        # Add 2 switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Connect each subnet on the router to a switch
        self.addLink(s1,
                     r1,
                     intfName2='r1-eth1',
                     params2={'ip': '10.0.0.1/24'})

        self.addLink(r1,
                     s2,
                     intfName1='r1-eth2',
                     params1={'ip': '10.1.0.1/24'},
                     bw=10, delay='20ms', loss=0, max_queue_size=10000, use_tbf=True)

        # Add two "TX" hosts on one subnet, and one "RX" host on the other
        tx1 = self.addHost(name='tx1',
                          ip='10.0.0.251/24',
                          defaultRoute='via 10.0.0.1')
        tx2 = self.addHost(name='tx2',
                          ip='10.0.0.252/24',
                          defaultRoute='via 10.0.0.1')
        rx1 = self.addHost(name='rx1',
                          ip='10.1.0.252/24',
                          defaultRoute='via 10.1.0.1')

        # Connect the hosts to their respective switches
        self.addLink(tx1, s1, bw=100, delay='0ms', loss=0, use_tbf=True)
        self.addLink(tx2, s1, bw=100, delay='0ms', loss=0, use_tbf=True)
        self.addLink(rx1, s2)


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, autoStaticArp=True)

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()

