import random
import time
import socket
import unittest
import threading
from p2p.server.rs import RegistrationServer
from p2p.proto.proto import Message, MethodTypes, Headers, ServerResponse, ResponseStatus
from p2p.utils.app_constants import RS, RS_HOST, RS_PORT
from p2p.utils.app_utils import send, recv

random.seed(0)


class RegistrationServerTest(unittest.TestCase):
    """ Registration Server Tests"""

    def test_register(self):
        """ registers a new client """
        pass

    def test_unregister(self):
        """ un-registers a new client """
        pass

    def _socket_connect_test(self):
        """ connects to a server socket """
        client = socket.socket()
        client.connect(RS)
        time.sleep(4)

        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "nick-name{}{}".format(Message.SR_FIELDS, random.randint(7000, 8000))

        send(client, msg)
        response = ServerResponse().from_bytes(recv(client))
        self.assertTrue(Headers.Cookie.name in response.headers)

        msg.headers[Headers.Cookie.name] = response.headers[Headers.Cookie.name]
        msg.method = MethodTypes.KeepAlive.name
        send(client, msg)
        ServerResponse().from_bytes(recv(client))

        msg.method = MethodTypes.Leave.name
        send(client, msg)
        data = ServerResponse().from_bytes(recv(client))

        self.buffer.append(str(data))
        client.close()

    def _socket_error_test(self):
        """ connects to socket and fails the requests """
        client = socket.socket()
        client.connect(RS)
        time.sleep(2)

        msg = Message()
        msg.method = "Unknown"
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "Invalid message"

        send(client, msg)
        data = ServerResponse().from_bytes(recv(client))

        self.fail_buffer.append(str(data))
        client.close()

    def _socket_cookie_test(self):
        """ connects to socket and fails the requests """
        client = socket.socket()
        client.connect(RS)
        time.sleep(3)

        msg = Message()
        msg.method = MethodTypes.Register.name
        msg.headers = {}
        msg.version = Message.VERSION
        msg.payload = "nick-name{}{}".format(Message.SR_FIELDS, random.randint(7000, 8000))

        send(client, msg)
        ServerResponse().from_bytes(recv(client))

        msg.method = MethodTypes.KeepAlive.name
        send(client, msg)
        response = ServerResponse().from_bytes(recv(client))

        self.assertEqual(int(response.status), ResponseStatus.Forbidden.value)
        client.close()

    def test_start(self):
        """ starts the server and tries connecting """
        threads = []
        self.buffer = []
        self.fail_buffer = []
        rs = RegistrationServer(RS_HOST, RS_PORT)
        server_thread = threading.Thread(target=rs.start, kwargs=dict(timeout=10, ))
        server_thread.start()
        time.sleep(5)
        for i in range(3):
            threads.append(threading.Thread(target=self._socket_connect_test))
            threads.append(threading.Thread(target=self._socket_error_test))
        threads.append(threading.Thread(target=self._socket_cookie_test))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        server_thread.join()

        expected = "Response<fs>P2Pv1<cs>Success<cs>200"
        self.assertEqual([expected, expected, expected], self.buffer)

        expected = "Response<fs>P2Pv1<cs>Method not allowed<cs>405"
        self.assertEqual([expected, expected, expected], self.fail_buffer)

    def test_stop(self):
        """ stops the server """
        pass


if __name__ == "__main__":
    unittest.main()
