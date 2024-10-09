# TCP-server-and-client-testing
Python TCP Server and Client for Testing
This Python implementation provides a simple TCP server and client for testing network communications. The server listens for incoming connections and can handle multiple clients concurrently.
The client can connect to the server, send messages, and receive responses, making it ideal for testing network interactions and debugging.

Features:
TCP Server:
Listens on a specified port for incoming client connections.
Handles multiple clients using threading, allowing simultaneous communication.
Echoes received messages back to the client, enabling easy verification of data transmission.
Configurable server settings, such as host and port.

TCP Client:
Connects to the specified server and port.
Sends user-defined messages to the server.
Receives and displays the server's responses, facilitating real-time testing.
Includes error handling for connection issues and timeouts.

Usage:
Run the Server: Start the TCP server script on your machine, specifying the desired host and port.

Run the Client: Execute the TCP client script, providing the server's host and port. You can enter messages to send to the server.

Testing: Use the client to send various messages and observe the server's responses. This setup is useful for testing the robustness of network communications in your applications.

Requirements:
Python 3.x

This TCP server and client can serve as a foundation for more complex network applications or be used for educational purposes to understand TCP communication in Python.
