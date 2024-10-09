
import socket
import threading
import tkinter as tk
import tkinter.messagebox
from datetime import datetime, date

LIGHT_BLACK = '#333333' 
LIGHT_BLUE = '#ADD8E6'
LIGHT_GREEN = '#90EE90' 
LIGHT_SGREEN = '#20B2AA'

class ServerApp(tk.Tk):

    def __init__(self, server_host=None, server_port=None):
        super().__init__()
        self.title("server Tool: GD1.0.0")
        self.protocol("WM_DELETE_WINDOW", self.close_escape)
        self.server_host = server_host
        self.server_port = server_port
        self.closed_flag = threading.Event()
        self.connected_clients = []
        self.clients = {}
        self.client_threads = {}
        self.lock = threading.Lock()         
        if not self.server_host or not self.server_port:
            self.set_server_details() 
        self.csq_value = None
        self.cstatus_value = None
        self.S1_value = None
        self.S2_value = None
        self.NPRES_value = None
        self.bat_value = None
        self.ccid_value = None
        self.smode_value = None
        self.apn_value = None
        self.ip_value = None
        self.port_value = None
        self.apn1_value = None
        self.ip1_value = None
        self.port1_value = None
        self.r_value = None
        self.y_value = None
        self.b_value = None
        self.pwr_value = None
        self.rf_value = None
        self.serial_value = None
        self.tr_f = 0
        self.tt_f = 0
        self.flag2 = 0
        self.flag3 = 0
        self.flag4 = 0
        self.flag5 = 0
        self.pw = 0
        self.raw = 0
        self.create_window_controls()
        self.entry_frame()
        self.send_frame()
        self.button_frame()
        self.button_frame1()
        self.client_frame()
        self.create_controls()
        self.fetch_datetime()

    def fetch_datetime(self):
        current_time = datetime.now().strftime("%I:%M:%S %p")
        self.time_label.config(text=current_time)
        day = date.today()
        self.date_label.config(text=day)
        self.after(1000, self.fetch_datetime)

    def set_server_details(self):
        self.withdraw()
        dialog = ServerDetailsDialog(self)
        self.wait_window(dialog)  
        
        if dialog.server_ip and dialog.server_port:
            self.server_host = dialog.server_ip
            self.server_port = dialog.server_port
            self.deiconify()  
            self.start_server()
           
        else:
            self.close_escape() 

    def start_server(self):
        if not self.server_host or not self.server_port:
            tk.messagebox.showerror("Error", "Please enter Server IP Address and Port")
            return
        try:
            self.server_port = int(self.server_port)
        except ValueError:
            tk.messagebox.showerror("Error", "Port must be a number")
            return
        server_thread = threading.Thread(target=self.run_server)
        server_thread.start()

    def run_server(self):
        try:
            if ":" in self.server_host:
                server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            else:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            server_socket.bind((self.server_host, self.server_port))
            server_socket.listen(5)

            while not self.closed_flag.is_set():
                client_socket, client_address = server_socket.accept()
                receive_thread = threading.Thread(target=self.receive_data, args=(client_socket,))
                receive_thread.start()
                with self.lock:
                    self.client_threads[client_address] = receive_thread
                    self.clients[client_address] = client_socket
                    self.connected_clients.append(client_address)
                self.update_connection_label()
                self.sign_on_button.config(state=tk.NORMAL) 
                self.sign_on1_button.config(state=tk.NORMAL) 
                self.raw_button.config(state=tk.NORMAL)

        except socket.error as e:
            tk.messagebox.showerror("Socket Error", f"Failed to start server\nEnter valid IP and port: {e}")
            self.close_escape() 

    def receive_data(self, client_socket):
        client_address = client_socket.getpeername()
        dt = datetime.now().strftime("%I:%M:%S")
        while not self.closed_flag.is_set():
            try:
                data = client_socket.recv(4096)
                if not data:              
                    received_data = f"{dt} Client {client_address} disconnected"
                    self.received_data_text.insert(tk.END, received_data)
                    self.received_data_text.see(tk.END)
                    client_socket.close()
                    with threading.Lock():
                        if client_address in self.clients:
                            del self.clients[client_address]
                        if client_address in self.connected_clients:
                            self.connected_clients.remove(client_address)
                    self.update_connection_label()
                    break
 
                if data:
                    #print(data)
                    
                    if (self.raw == 1):
                        self.received_data_text.insert(tk.END, data)
                        self.received_data_text.see(tk.END)
                    
                    try:
                        decoded_data = data.decode('utf-8')  # Decode bytes to string
                        
                    except UnicodeDecodeError:
                            try:
                                decoded_data = ' '.join(f'{byte:02X}' for byte in data)  
                            except Exception as e:
                                decoded_data = data  

                    hex_data = bytearray(data)
                    
            except Exception as e:
                del self.clients[client_address]
                self.connected_clients.remove(client_address)
                self.update_connection_label()
                #print(f"Error in receive_data xx: {e}")
                print_data = "\nError in receive_data xx: {e}\n"
                self.received_data_text.insert(tk.END, print_data)
                self.received_data_text.see(tk.END)
                self.tr_f = 0
                self.tt_f = 0
                self.flag2 = 0
                break

    def update_connection_label(self):
        num_clients = len(self.clients)
        dt = datetime.now().strftime("%I:%M:%S")
        if not self.connected_clients or num_clients == 0:
            received_data = f"\n[{dt}]--[No client connected]\n"
            self.received_data_text.insert(tk.END, received_data)  
            self.received_data_text.see(tk.END)
        else:
            client_list = "\n".join(str(client) for client in self.connected_clients)
            received_data = f"\n[{dt}]--[Connected Client:{client_list}]\n"
            self.received_data_text.insert(tk.END, received_data)  
            self.received_data_text.see(tk.END)

    def auto_debug(self):
        command1 = ""  
        with threading.Lock():
            for client_address, client_socket in list(self.clients.items()):
                try:
                    dt = datetime.now().strftime("%I:%M:%S")
                    client_socket.sendall((command1 + '\r\n').encode('utf-8'))
                    
                except Exception as e:
                    print(f"Error sending command to client {client_address}: {e}")
    
   
    def send_command(self):
        with threading.Lock():    
            for client_address, client_socket in list(self.clients.items()):
                command_to_send = self.send_entry.get()
                if command_to_send:
                    self.pw = 1
                    self.raw = 1
                    if ' ' in command_to_send:
                        try:
                            dt = datetime.now().strftime("%I:%M:%S")
                            bytes_command = bytes.fromhex(command_to_send.replace(' ', ''))
                            client_socket.sendall(bytes_command)
                            received_data = f"\n[TX{dt}]--[{command_to_send}]\n"
                            self.received_data_text.insert(tk.END, received_data)  
                            self.received_data_text.see(tk.END)
                        except ValueError:
                            print("Invalid hexadecimal input")
                    else:
                        try:
                            dt = datetime.now().strftime("%I:%M:%S")
                            client_socket.sendall((command_to_send + '\r\n').encode('utf-8'))
                            received_data = f"\n[TX{dt}]--[{command_to_send}]\n"
                            self.received_data_text.insert(tk.END, received_data) 
                            self.received_data_text.see(tk.END)
                        except Exception as e:
                            print(f"Error sending command to client {client_address}: {e}")
                    
    def close_escape(self):
        self.closed_flag.set() 
        for client_socket in self.clients.values():
            client_socket.close()

        self.after(10, self.destroy)
 

    


    def create_window_controls(self):
        window_controls_frame = tk.Frame(self,bg=LIGHT_BLACK)
        window_controls_frame.pack(side="top", fill="x")
        self.time_label = tk.Label(window_controls_frame, text="",bg=LIGHT_BLACK,fg =LIGHT_BLUE, font=("Arial", 12))
        self.time_label.pack(side="left", padx=10)
        self.date_label = tk.Label(window_controls_frame, text="",bg=LIGHT_BLACK,fg =LIGHT_BLUE, font=("Arial", 12))
        self.date_label.pack(side="right", padx=10)
        self.label2 = tk.Label(self, text=f"Server is listening on \n IP =  {self.server_host}, port = {self.server_port}", font=("Arial", 15), fg=LIGHT_SGREEN,bg='black')
        self.label2.pack(padx=5, pady=10)
    
    def pw_check(self):
        pw = self.pw_entry.get()
        if (pw == "manas@007"):
            self.send_button.config(state=tk.NORMAL)
            self.reset1_button.config(state=tk.NORMAL)
            self.RESET_button.config(state=tk.NORMAL)
            self.send_label.config(state=tk.NORMAL)
            self.SLAVE_button.config(state=tk.NORMAL)
            self.MASTER_button.config(state=tk.NORMAL)
            '''received_data = f"\nEnjoy the PRO version 🙂\n"
            self.received_data_text.insert(tk.END, received_data)  
            self.received_data_text.see(tk.END)'''
            tk.messagebox.showerror("Success", "Enjoy the PRO version 🙂")
            self.pw = 1
            self.sign_on3_button.config(text="DINFO")
            self.sign_on_button.config(text="TR")
            self.sign_on1_button.config(text="TT")
            self.sign_on2_button.config(text="CPIN?")            
        else:
            '''received_data = f"\nPlease try with different code 😒\n"
            self.received_data_text.insert(tk.END, received_data)  
            self.received_data_text.see(tk.END)'''
            tk.messagebox.showerror("Failure", "Please try with different code 😒")
            self.send_button.config(state=tk.DISABLED)
            self.reset1_button.config(state=tk.DISABLED)
            self.RESET_button.config(state=tk.DISABLED)
            self.send_label.config(state=tk.DISABLED)
            self.MASTER_button.config(state=tk.DISABLED)
            self.SLAVE_button.config(state=tk.DISABLED)
            self.pw = 0
            self.sign_on3_button.config(text="START")
            self.sign_on_button.config(text="AUTO DEBUG ➡️")
            self.sign_on1_button.config(text="MODULE DEBUG ➡️")
            self.sign_on2_button.config(text="CSTART")
        self.pw_entry.delete(0, tk.END)

    def toggle_raw(self):
        if self.raw == 1: 
           self.raw = 0 
           tk.messagebox.showerror("message", "RAW Data Disabled")
           '''received_data = f"\nRAW DATA desabled\n"
           self.received_data_text.insert(tk.END, received_data)  
           self.received_data_text.see(tk.END)'''
        else: 
            self.raw = 1
            tk.messagebox.showerror("message", "RAW Data Enabled")
            '''received_data = f"\nRAW DATA Enabled\n"
            self.received_data_text.insert(tk.END, received_data)  
            self.received_data_text.see(tk.END)'''
    
    def entry_frame(self):
        entry_frame = tk.Frame(self,  bg='black')   
        self.send_label = tk.Label(entry_frame, text="Enter command :", font=("Arial", 14), bg='black',fg=LIGHT_BLUE)
        self.send_label.pack(side="left", padx=5)
        self.send_label.config(state=tk.DISABLED)
        self.send_entry = tk.Entry(entry_frame, width=90,bg='black', fg='white')
        self.send_entry.pack(side="left", padx=10)
        entry_frame.pack(padx=10)
    
    def send_frame(self):
        send_frame = tk.Frame(self,  bg='black')   
        self.send_button = tk.Button(send_frame, text="Send", font=("Arial", 12),bg=LIGHT_BLACK,fg=LIGHT_BLUE, command=self.send_command)
        self.send_button.pack(side="left", padx=5, pady=5)
        self.send_button.config(state=tk.DISABLED)
        send_frame.pack()

    def button_frame(self):
        
        button_frame = tk.Frame(self,  bg='black')
        self.sign_on_button = tk.Button(button_frame, text = "AUTO DEBUG ➡️", font=("Arial", 10), bg=LIGHT_BLACK,fg=LIGHT_BLUE, command=self.auto_debug)
        self.sign_on_button.pack(side="left", padx=5, pady=5)
        self.sign_on_button.config(state=tk.DISABLED)
        

        self.raw_button = tk.Button(button_frame, text="RAW DATA", font=("Arial", 10), bg=LIGHT_BLACK,fg=LIGHT_BLUE, command=self.toggle_raw)
        self.raw_button.pack( side="left", padx=5, pady=5)
        self.raw_button.config(state=tk.DISABLED)

        button_frame.pack()

    def button_frame1(self):
        button_frame1 = tk.Frame(self,  bg='black')
    
        button_frame1.pack()

    def client_frame(self):  
        client_frame = tk.Frame(self,  bg='black') 
        self.received_data_text = tk.Text(client_frame, font=("Arial", 10),bg=LIGHT_BLACK,fg=LIGHT_GREEN, height=25, width=105, wrap='word')
        '''scrollbar = tk.Scrollbar(client_frame, bg=LIGHT_BLACK, troughcolor='black')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.received_data_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.received_data_text.yview,bg=LIGHT_BLACK)'''
        self.received_data_text.pack()
        self.send_entry.bind('<Return>', lambda event=None: self.send_command())
        client_frame.pack()
        
    def create_controls(self):
        controls_frame = tk.Frame(self,  bg='black')
        controls_frame.pack(side="bottom", fill="x")
        self.my_label = tk.Label(controls_frame, text="made by manas;)", font=("ITALIC", 9),bg='black', fg='white')
        self.my_label.pack(side="right", padx=10)
        self.pw_label = tk.Label(controls_frame, text="Enter Code for pro version:", font=("Arial", 10), bg='black', fg='white')
        self.pw_label.pack(side="left", padx=5, pady=10)
        self.pw_entry = tk.Entry(controls_frame, width=50,bg='black', fg='white')
        self.pw_entry.pack(side="left", padx=5, pady=10)       
        self.pw_button = tk.Button(controls_frame, text="Submit", font=("Arial", 10),  bg='black', fg='white', command=self.pw_check)
        self.pw_button.pack(side="left", padx=5, pady=10)
        self.pw_entry.bind('<Return>', lambda event=None: self.pw_check())

class ServerDetailsDialog(tk.Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        self.title("Create Server")
        self.server_ip = None
        self.server_port = None
        self.default_options = {
            "Select default option": {"ip": "", "port": ""},
            "2403:xxxx:xxxx:xx::xx (Port: 4059)": {"ip": "2403:xxxx:xxxx:xx::xx", "port": "4059"},  #enter  your local ip 
            "2403:xxxx:xxxx:xx::xx(Port: 8989)": {"ip": "2403:xxxx:xxxx:xx::xx", "port": "8989"},       
        }

        self.default_selection = tk.StringVar(self)
        self.default_selection.set("Select Default IP and PORT")
    
        self.default_entry = tk.OptionMenu(self, self.default_selection, *self.default_options.keys(), command=self.update_ip_port)
        self.default_entry.grid(row=0, column=1, columnspan=2, padx=10, pady=10)
        
        #self.configure(bg=LIGHT_BLACK) 
        tk.Label(self, text="Server IP:", font=("ITALIC", 12)).grid(row=1, column=0, padx=10, pady=10)
        self.ip_entry = tk.Entry(self, width=45)
        self.ip_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self, text="Server Port:", font=("ITALIC", 12)).grid(row=2, column=0, padx=10, pady=10)
        self.port_entry = tk.Entry(self,width=45)
        self.port_entry.grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self, text="Submit",  font=("ITALIC", 12),  command=self.on_ok).grid(row=3, column=0, columnspan=2, padx=5, pady=10)
        #tk.Button(self, text="Close",  font=("ITALIC", 12),  command=self.destroy).grid(row=3, column=2, columnspan=2, padx=5, pady=10)

    def update_ip_port(self, selected_option):
        if selected_option and selected_option != "Select default option":
            selected_data = self.default_options[selected_option]
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.insert(0, selected_data["ip"])
            self.port_entry.delete(0, tk.END)
            self.port_entry.insert(0, selected_data["port"])
        else:
            self.ip_entry.delete(0, tk.END)
            self.port_entry.delete(0, tk.END)
    
    def on_ok(self):
        self.server_ip = self.ip_entry.get()
        self.server_port = self.port_entry.get()

        if not self.server_ip or not self.server_port:
            tk.messagebox.showerror("Error", "Please enter Server IP Address and Port")
        else:
            self.parent.server_host = self.server_ip
            self.parent.server_port = self.server_port
            self.destroy()  


def launch_server_app():
    app = ServerApp()
    app.configure(bg="BLACK")
    app.bind("<`>", lambda e: app.close_escape())
    app.mainloop()


if __name__ == "__main__":
    launch_server_app()