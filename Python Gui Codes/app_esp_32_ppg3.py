import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import socket
import threading
import csv
import time
from tkinter import filedialog
from queue import Queue

# Global variables
queue = Queue()
running = False
recording = False
recorded_data = []
bpm_value = 0  # Initialize BPM

# Function to receive data from ESP32
def receive_data(ip_address):
    global running, recording
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((ip_address, 80))
        print("Connected to ESP32")

        while running:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if data:
                ppg_values = data.split("\n")  # Split the received string into multiple values
                for value in ppg_values:
                    try:
                        # Attempt to extract valid PPG and BPM values from received data
                        ir_value = float(value.strip())  # Use IR value if it's just one value coming in

                        # Debug print for valid data
                        print(f"Received IR Value: {ir_value}")

                        # Use queue to safely pass data to the main GUI thread
                        queue.put(ir_value)

                        # Record the data if recording is enabled
                        if recording:
                            record_data(ir_value)

                    except ValueError:
                        print(f"Invalid data received: {value}")  # Handle invalid or malformed data
                        continue  # Skip invalid data
            time.sleep(0.1)  # Adjust sleep time for smoother reception

    except Exception as e:
        print(f"Error in connection: {e}")
    finally:
        client_socket.close()

# Function to calculate BPM based on IR signal
def calculate_bpm(ir_values):
    global bpm_value
    if len(ir_values) < 2:
        return 0  # Not enough data to calculate BPM

    # Find peaks in the IR signal using a more dynamic approach
    peaks = []  # Stores indices of peaks
    # Set a more flexible threshold based on signal range
    signal_mean = np.mean(ir_values)
    signal_range = np.max(ir_values) - np.min(ir_values)
    threshold = signal_mean + (signal_range * 0.1)  # Adjust the threshold to be 10% above the mean signal

    for i in range(1, len(ir_values) - 1):
        # Simple peak detection based on threshold
        if ir_values[i - 1] < ir_values[i] and ir_values[i] > ir_values[i + 1] and ir_values[i] > threshold:
            peaks.append(i)

    if len(peaks) < 2:
        return 0  # Not enough peaks to calculate BPM

    # Calculate the time difference between consecutive peaks
    time_diffs = []
    for i in range(1, len(peaks)):
        time_diffs.append(peaks[i] - peaks[i - 1])

    if len(time_diffs) == 0:
        return 0  # No peaks detected

    # Calculate average time between peaks (in samples)
    avg_time_between_peaks = np.mean(time_diffs)
    
    # Correct sampling rate based on your data, which is 100ms per sample (i.e., 10Hz)
    sampling_rate = 8  # Adjust based on your actual sensor's sampling rate
    if avg_time_between_peaks == 0:
        return 0  # Avoid division by zero

    # Calculate BPM formula: BPM = (Sampling Rate * 60) / Avg Time Between Peaks
    bpm_value = (sampling_rate * 60) / avg_time_between_peaks  # BPM formula
    if bpm_value > 200:  # Cap maximum BPM value at a reasonable level
        bpm_value = 200
    return bpm_value

# Function to update the plot with the new value
def update_plot():
    global y_data_ir, line_ir, ir_values
    if not queue.empty():
        ir_value = queue.get_nowait()  # Get the latest IR value from the queue
        # Shift data left and add new IR value
        y_data_ir = np.roll(y_data_ir, -1)
        y_data_ir[-1] = ir_value  # Add the new IR value

        # Adjust y-axis limits dynamically based on incoming values
        ax_ir.set_ylim(min(y_data_ir) - 50, max(y_data_ir) + 50)

        # Update the plot line
        line_ir.set_ydata(y_data_ir)
        canvas.draw()  # Redraw the updated plot

        # Add IR value to the list for BPM calculation
        ir_values.append(ir_value)
        if len(ir_values) > 200:  # Keep only the last 200 samples for BPM calculation
            ir_values.pop(0)

        # Calculate and display BPM
        bpm = calculate_bpm(ir_values)
        bpm_label.config(text=f"BPM: {bpm:.2f}")  # Update the BPM label

    root.after(50, update_plot)  # Schedule the next update for smoother display

# Function to start streaming data
def start_stream():
    global running
    running = True
    ip_address = ip_entry.get().strip()
    if not ip_address:
        print("IP address cannot be empty.")
        return
    
    thread = threading.Thread(target=receive_data, args=(ip_address,))
    thread.start()

# Function to stop streaming data
def stop_stream():
    global running
    running = False

# Function to start recording data
def start_recording():
    global recording, recorded_data
    recording = True
    recorded_data = []  # Clear previous recorded data
    print("Recording started")

# Function to stop recording data
def stop_recording():
    global recording
    recording = False
    print("Recording stopped.")
    save_data_to_csv()

# Function to record data with timestamps
def record_data(ir_value):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")  # Get current timestamp
    recorded_data.append((timestamp, ir_value))  # Store as tuple (timestamp, IR value)

# Function to save recorded data to a CSV file
def save_data_to_csv():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", 
                                               filetypes=[("CSV files", ".csv"), ("All files", ".*")])
    if file_path:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "IR Value"])  # Header
            for timestamp, ir_data in recorded_data:
                writer.writerow([timestamp, ir_data])
        print(f"Data saved to {file_path}")

# GUI setup
root = tk.Tk()  # Define the root window
root.title("IR Signal Viewer")
root.geometry("800x600")

# Configure the grid layout
for i in range(3):
    root.rowconfigure(i, weight=1)  # Allow rows to expand
for j in range(2):
    root.columnconfigure(j, weight=1)  # Allow columns to expand

# Input for ESP32 IP address
tk.Label(root, text="Enter ESP32 IP Address:").grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
ip_entry = tk.Entry(root, width=30)
ip_entry.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

# Plotting setup
fig, ax_ir = plt.subplots(figsize=(8, 6))  # Single plot for IR values
y_data_ir = np.zeros(100)  # Initialize IR data with 100 zeros
line_ir, = ax_ir.plot(y_data_ir, color='b', lw=2)

# Set initial y-axis limits dynamically
ax_ir.set_ylim(0, 1024)  # Adjust as per your signal range
ax_ir.set_title("Real-time IR Signal", fontsize=16)
ax_ir.set_ylabel("IR Value", fontsize=12)
ax_ir.grid(True)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

# BPM Label
bpm_label = tk.Label(root, text="BPM: 0.00", font=("Arial", 14))
bpm_label.grid(row=2, column=0, columnspan=2, pady=10)

# Start/Stop buttons
button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

start_button = tk.Button(button_frame, text="Start", command=start_stream, width=8)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_stream, width=8)
stop_button.pack(side=tk.LEFT, padx=5)

record_button = tk.Button(button_frame, text="Start Recording", command=start_recording, width=12)
record_button.pack(side=tk.LEFT, padx=5)

stop_record_button = tk.Button(button_frame, text="Stop Recording", command=stop_recording, width=12)
stop_record_button.pack(side=tk.LEFT, padx=5)

# Mainloop
ir_values = []  # Store recent IR values for BPM calculation
root.after(50, update_plot)  # Schedule the first update call to the plot
root.mainloop()
