import socket
from _thread import start_new_thread

clients = []


def threaded(client):
    """
    Threaded function so more than one client can connect and interact with
    the server at once. The server receives data from one client and then sends
    that data to all the other clients.
    """
    while True:
        # Data received from the client.
        data = client.recv(4096)
        if not data:
            print('Not Data.')
            break

        # Send the data received from one client to all the other clients.
        for c in clients:
            if c != client:
                c.sendall(data)

    client.close()


def main():
    """
    Main server function where a socket is created and a loop waits for clients
    to connect to the socket.
    """
    # Host left to "" so when .bind() is called socket is binded to all interfaces.
    host = ""
    # Connection port
    port = 5555
    # Create an IPv4 (AF_INET), TCP (SOCK_STREAM) socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind() associates the socket with its local address
    # server side binds so that clients can use that address to connect to server
    s.bind((host, port))
    print("Socket binded to port:", port)
    # Put the socket into listening mode.
    s.listen(2)
    print("Socket is listening.")

    # A forever loop until the client wants to exit.
    while True:
        # Establish a connection with the client.
        c, addr = s.accept()
        clients.append(c)

        print(f"Connected to: {addr[0]}:{addr[1]}")

        # Start a new thread and return its identifier.
        start_new_thread(threaded, (c,))

    s.close()


if __name__ == '__main__':
    main()
