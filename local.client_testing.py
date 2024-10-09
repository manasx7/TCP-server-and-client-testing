import socket
import time
import threading

def gprsconnect():
    server = "2403:xxxx:xxxx:xx::xx" # enter server ip you want to connect to
    port = 4059
    client_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    client_socket.connect((server, port))
    print(f"Connected to server at [{server}]:{port}")
    return client_socket

def gprs_retry():
    while True:
        try:
            client_socket = gprsconnect()
            return client_socket
        except socket.error as e:
            retry_delay = 5
            print(f"Connection error: {e}")
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

def send_data(client_socket,  closed_flag):
    while not closed_flag.is_set():
        try:           
            msg = input("Enter msg to send : ")
            try:
                client_socket.sendall(msg.encode())
            except Exception as e:
                print(f"Error sending to client: {e}")
        except socket.error as e:
            print(f"Error: {e}")
            client_socket = gprs_retry()  
            if client_socket:
                print("Reconnected to the server.")
            else:
                print("Failed to reconnect. Exiting.")
                break


def receive_data(client_socket, closed_flag):
    while not closed_flag.is_set():
        try:
            data = client_socket.recv(4096).decode()
            print("Received data:", data)
            if not data:
                print("Server closed the connection. Reconnecting...")
                client_socket = gprs_retry() 
                if client_socket:
                    print("Reconnected to the server.")
                else:
                    print("Failed to reconnect. Exiting.")
                    break
            elif data == "close":
                print("Received 'close' command. Closing the connection and exiting.")
                closed_flag.set()
                close_connection(client_socket)
            else:
                print("Received data:", data)

        except ConnectionAbortedError as e:
            print(f"ConnectionAbortedError: {e}")
            client_socket = gprs_retry() 
            if client_socket:
                print("Reconnected to the server.")
            else:
                print("Failed to reconnect. Exiting.")
                break

        except ConnectionResetError as e:
            print(f"ConnectionResetError: {e}")
            client_socket = gprs_retry() 
            if client_socket:
                print("Reconnected to the server.")
            else:
                print("Failed to reconnect. Exiting.")
                break

def close_connection(client_socket):
    client_socket.close()
    print("Connection closed")

def main():
    serial = 1000
    closed_flag = threading.Event()
    try:
        client_socket = gprs_retry()
        if client_socket:
            
            send_thread = threading.Thread(target=send_data, args=(client_socket,  closed_flag))
            receive_thread = threading.Thread(target=receive_data, args=(client_socket, closed_flag))

            send_thread.start()
            receive_thread.start()

    except socket.error as e:
        gprs_retry()

if __name__ == "__main__":
    main()

