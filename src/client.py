import socket
import pickle


class Client:
    def __init__(self):
        # Server IP
        self.host = 'localhost'
        # Connection port
        self.port = 5555
        # Create an IPv4 (AF_INET), TCP (SOCK_STREAM) socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        # Take the client id to be its local port.
        self.id = self.socket.getsockname()[1]

    def send(self, data):
        """Send data from the client to the server."""
        # Serialize the data so it can be sent as a byte stream to the socket.
        message = pickle.dumps(data)
        msg_len = len(message)
        try:
            # Send what the total length of the message to be sent is in bytes.
            self.socket.send(msg_len.to_bytes(4, 'big'))
            self.socket.sendall(message)
        except socket.error as e:
            return str(e)

    def receive(self):
        """Return data received from the server."""
        # Find how big message to be received is in bytes.
        remaining = int.from_bytes(self.socket.recv(4), 'big')
        chunks = []
        # While there are still bytes to receive.
        while remaining:
            # Get remaining bytes or 4096 bytes (whatever is smaller).
            chunk = self.socket.recv(min(remaining, 4096))
            remaining -= len(chunk)
            chunks.append(chunk)

        chunks = b"".join(chunks)
        # Deserialize the received byte stream to return data to its original
        # data type.
        data = pickle.loads(chunks)
        return data


if __name__ == '__main__':
    # Testing.
    client1 = Client()
    client2 = Client()

    while True:
        client1.send(map)
        client2.send((3, 2))
        print(f"Client 1 received: {client1.receive()}")
        print(f"Client 2 received: {client2.receive()}")
