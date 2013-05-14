import socket
import sys
import signal
import thread
import eventlet


def main(setup, error):
    for settings in parse(setup):
        print settings
        thread.start_new_thread(server, settings)

    try:
        signal.pause()
    except KeyboardInterrupt:
        print "Ctrl + C: exit nicely...\n"
        sys.exit(0)


def parse(setup):
    settings = list()
    for line in file(setup):
        parts = line.split()
        settings.append((parts[0], int(parts[1]), int(parts[2])))
    return settings


def server(*settings):
    local_port = settings[2]
    host_ip = settings[0]
    host_port = settings[1]

    dock_socket = eventlet.listen(('0.0.0.0', local_port))
    while True:
        print 'New client'
        client_socket = dock_socket.accept()[0]
        server_socket = eventlet.connect((host_ip, host_port))
        eventlet.spawn_n(forward, client_socket, server_socket)
        eventlet.spawn_n(forward, server_socket, client_socket)


def forward(source, destination):
    print '--------'
    while True:
        string = source.recv(1024)
        print 'recv: %s' % len(string)
        if not string:
            break
        destination.sendall(string)
    source.shutdown(socket.SHUT_RD)
    destination.shutdown(socket.SHUT_WR)
    print '---------'


if __name__ == '__main__':
    main('proxy.ini', 'error.log')
