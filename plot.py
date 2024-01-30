import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# Input parameters
num_vehicles = 6
Vehicle_length = 2.4  # [m]
track_circumference = 1000  # [m] Circumference of the circular track
time_skip_per_draw = 10
simulation_file = 'vehicle_positions_and_speeds_4.xlsx'

# Read data from Excel
df = pd.read_excel(simulation_file)

# Colors for each vehicle
colors = ['red', 'green', 'blue', 'cyan', 'magenta', 'yellow']

# Set up the figure
fig, ax = plt.subplots()
ax.set_aspect('equal', 'box')
theta = np.linspace(0, 2 * np.pi, 100)
x_circle = track_circumference / (2 * np.pi) * np.cos(theta)
y_circle = track_circumference / (2 * np.pi) * np.sin(theta)
ax.plot(x_circle, y_circle, 'k')  # Draw the track

last_time = time.time()
# Animation update function
def update(frame):
    global last_time
    ax.clear()
    ax.plot(x_circle, y_circle, 'k')  # Redraw the track
    legend_texts = []  # List to store legend texts

    for i in range(num_vehicles):
        position = df.iloc[frame*time_skip_per_draw][f'Position_{i+1}'] % track_circumference
        speed = df.iloc[frame*time_skip_per_draw][f'Speed_{i+1}']
        x = track_circumference / (2 * np.pi) * np.cos(2 * np.pi * position / track_circumference)
        y = track_circumference / (2 * np.pi) * np.sin(2 * np.pi * position / track_circumference)
        plot, = ax.plot(x, y, color=colors[i], marker='o', markersize=10, label=f'Vehicle {i+1}: {speed:.2f} m/s')
        legend_texts.append(plot)

    ax.legend(handles=legend_texts, loc='upper right')  # Update the legend

    current_time = df.iloc[frame*time_skip_per_draw]['Time']
    print(f"Current Time: {current_time} millis from last draw {time.time() - last_time}")  # Print the current time
    last_time = time.time()

    ax.set_aspect('equal', 'box')
    ax.set_xlim(-track_circumference / (2 * np.pi), track_circumference / (2 * np.pi))
    ax.set_ylim(-track_circumference / (2 * np.pi), track_circumference / (2 * np.pi))
    ax.set_title("Vehicle Positions on Circular Track")

# Create the animation
ani = animation.FuncAnimation(fig, update, frames=round(len(df)/time_skip_per_draw), interval=100)
plt.show()