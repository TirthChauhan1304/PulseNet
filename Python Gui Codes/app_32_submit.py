import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import socket
import numpy as np
import threading

class RealTimeECG:
    def __init__(self, root):
        self.root = root
        self.root.title("Real-Time ECG Monitor")
        self.root.geometry("1600x800")
        self.root.configure(bg="#f0f0f0")

        # ECG properties
        self.fs = 500  # Sampling frequency (samples per second)
        self.duration = 5  # Duration of the plot in seconds

        self.time_data = np.linspace(0, self.duration, self.fs * self.duration)
        self.ecg_data = np.zeros_like(self.time_data)

        # Socket configuration (for ESP32 Wi-Fi connection)
        self.esp32_ip = "192.168.213.251"  # Change this to your ESP32 IP
        self.esp32_port = 80           # Port where ESP32 is sending data

        self.socket_thread = None
        self.socket_connected = False

        # GUI components
        self.create_widgets()

    def create_widgets(self):
        # Create the plot
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.line, = self.ax.plot(self.time_data, self.ecg_data, lw=2, color='#1f77b4')
        self.ax.set_ylim(-2, 2)
        self.ax.set_xlim(0, self.duration)
        self.ax.set_title('Real-Time ECG Data', fontsize=16, fontweight='bold')
        self.ax.set_xlabel('Time (s)', fontsize=14)
        self.ax.set_ylabel('ECG Amplitude (mV)', fontsize=14)
        self.ax.grid(True)

        # Button to start receiving data from ESP32
        self.start_button = ttk.Button(self.root, text="Start Receiving Data", command=self.start_receiving)
        self.start_button.pack(pady=10)

    def start_receiving(self):
        """Start the thread to receive data from ESP32."""
        if not self.socket_connected:
            self.socket_connected = True
            self.socket_thread = threading.Thread(target=self.receive_data_from_esp32, daemon=True)
            self.socket_thread.start()
            self.start_button.config(state=tk.DISABLED)

    def receive_data_from_esp32(self):
        """Receive data from the ESP32 using a socket connection."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.bind(("", self.esp32_port))
                print(f"Listening for data on port {self.esp32_port}...")
                while self.socket_connected:
                    # Receive a packet of data from ESP32
                    data, addr = s.recvfrom(1024)
                    ecg_value = float(data.decode())  # Assuming ESP32 sends ECG values as strings

                    # Update the plot with the new data
                    self.update_plot(ecg_value)
        except Exception as e:
            print(f"Error in receiving data: {e}")
            self.socket_connected = False

    def update_plot(self, new_ecg_value):
        """Update the ECG plot with the latest value."""
        # Shift old data and append the new data point
        self.ecg_data = np.roll(self.ecg_data, -1)
        self.ecg_data[-1] = new_ecg_value

        # Update the plot data
        self.line.set_ydata(self.ecg_data)
        self.canvas.draw()

        # Automatically adjust the time axis
        self.time_data = np.append(self.time_data, self.time_data[-1] + 1 / self.fs)
        self.ax.set_xlim(self.time_data[0], self.time_data[-1])

    def stop_receiving(self):
        """Stop the socket thread gracefully."""
        self.socket_connected = False
        if self.socket_thread:
            self.socket_thread.join()

if __name__ == "__main__":
    root = tk.Tk()
    app = RealTimeECG(root)
    root.protocol("WM_DELETE_WINDOW", app.stop_receiving)  # Gracefully close on window close
    root.mainloop()
