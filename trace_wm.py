#!/usr/bin/env python

import socket
import random
import time
import argparse
import copy
from ascii_map import get_terminal_size, WorldMap
from geoip import geolite2


def _create_receiver(port, timeout=1):
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_RAW, proto=socket.IPPROTO_ICMP)
    s.settimeout(timeout)
    try:
        s.bind(('', port))
    except socket.error as e:
        raise IOError("Can't bind receiver socket: {}".format(e))
    return s


def _create_sender(ttl):
    s = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    return s


def _send_message(ttl, dst, port):
    start_time = time.time()
    receiver = _create_receiver(port)
    sender = _create_sender(ttl)
    sender.sendto(b'', (dst, port))
    try:
        addr = receiver.recvfrom(1024)[1]
        duration = round((time.time() - start_time) * 1000, 2)
        return '{:<4} {:<15}  {:<6}ms'.format(ttl, addr[0], duration), get_location(addr[0])
    except socket.timeout:
        return '{:<4} *  *  *'.format(ttl), None
    finally:
        receiver.close()
        sender.close()


def get_location(ip):
    result = geolite2.lookup(ip)
    location = []
    if result:
        location.append(result.country)
        location.extend(result.subdivisions)
        if result.timezone != 'None':
            location.append(result.timezone)
        location.append(result.location)
    return filter(None, location)


def trace(dst, hops=30):
    port = random.choice(range(33434, 33535))
    try:
        dst_ip = socket.gethostbyname(dst)
    except socket.error as e:
        raise IOError('Unable to resolve {}:\n{}'.format(dst, e))
    header = 'Trace to {}({}) in max {} hops'.format(dst, dst_ip, hops)
    world_map = WorldMap(*get_terminal_size())
    world_map.add_msg(0, 0, header)
    print(world_map)
    routes, ttl = [], 1
    previous_location = None
    while ttl < hops + 1:
        memento_map = copy.deepcopy(world_map)
        route, location = _send_message(ttl, dst, port)
        if location:
            route += '  ' + ', '.join(location[:-1])
            # route += ' ({:.3f}, {:.3f})'.format(*location[-1])  # add coordinates to debug
            if location != previous_location:
                world_map.add_point(*location[-1], mark='{} {}'.format(ttl, location[0]))
                previous_location = location
        routes.append(route)
        memento_map.add_text(routes)
        print(memento_map)
        if route.split()[1] == dst_ip:
            break
        ttl += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Simple trace route implementation')
    parser.add_argument('host', metavar='host', type=str, help='Destination host to trace route')
    parser.add_argument('--hops', '-n', type=int, help='Max number of hops', required=False, default=30)
    args = parser.parse_args()

    trace(args.host, args.hops)
