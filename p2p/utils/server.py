import sys
import queue
import socket
import select
from p2p.utils.logger import logger

class Server(object):
    """ multi-client server """
    PORT = 9999

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.clients = []
        self.stopped = False
        self.conn = None
        self.logger = logger()
        self.messages = {} # message queue

    def _new_connection_callback(self, conn):
        """ callback for new connection. override """
        pass

    def _new_message_callback(self, conn, msg):
        """ callback for new message. override """
        pass

    def start(self):
        """ starts the server """
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setblocking(0)
        server_addr = (self.host, self.port)
        self.conn.bind(server_addr)
        self.conn.listen(5)
        inputs = [self.conn]
        outputs = []
        while inputs and not self.stopped:
            # listen for connections
            readable, writeable, exceptional = select.select(inputs, outputs, inputs)
            for s in readable:
                if s is self.conn:
                    conn, client = s.accept()
                    self.logger.info("Accepted connection from %s"%str(client))
                    inputs.append(conn)
                    self.messages[conn] = queue.Queue()
                    self._new_connection_callback(conn)
                else:
                    data = s.recv(1024)
                    if data:
                        self.logger.info("Received message '%s' from %s"%(str(data),str(s)))
                        if s not in outputs:
                            outputs.append(s)
                        self._new_message_callback(s, data)
                    else:
                        if s in outputs:
                            outputs.remove(s)
                        inputs.remove(s)
                        s.close()
                        del self.messages[s]

            for s in writeable:
                try:
                    next_msg = self.messages[s].get_nowait()
                except queue.Empty:
                    outputs.remove(s)
                else:
                    s.send(next_msg)

            for s in exceptional:
                inputs.remove(s)
                for s in outputs:
                    outputs.remove(s)
                s.close()
                del self.messages[s]

    def stop(self):
        """ stops the server """
        self.stopped = True
        try:
            self.conn.shutdown(1)
            self.conn.close()
        except OSError:
            self.logger.error('Error shutting down socket...')
