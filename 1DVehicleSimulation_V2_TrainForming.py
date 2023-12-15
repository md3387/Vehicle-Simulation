import random
import pandas as pd

# Initialize parameters
num_vehicles = 5
track_circumference = 2000  #[m] Circumference of the circular track
max_speed_limit = 30  #[m/s] Maximum speed limit [distance/time step]
Max_Postion_Delta = 0.1 #[m] maximum chance allowed in position on each simulation loop
Abs_Max_Speed = 1.2*(max_speed_limit) #[m/s]
max_vehicles = int(track_circumference/max_speed_limit)-1 # limit the number of vehicles allowed on the track
num_vehicles=min(max_vehicles, num_vehicles) #reduce number of vehicles in simulation if user has specified more than the max
print(f"num_vehicles = {num_vehicles}") #print the number of vehicles you've accepted into the simulation
initial_positions = [random.uniform(0, track_circumference) for _ in range(num_vehicles)] #initialize positions in random order


# Generate random initial speeds for each vehicle
initial_speeds = [random.uniform(0, max_speed_limit) for _ in range(num_vehicles)]
speeds = initial_speeds.copy() #[m/s]
acceleration_factor = 3#[m/s^2] This is also the deceleration factor
min_safe_distance = Max_Postion_Delta #[m] Minimum safe following distance


# Sort the initial positions in ascending order
positions = sorted(initial_positions)

# Adjust positions iteratively to ensure distances are at least 10X the maximum change in position 
#This loop still doesn't seem to be iterating enough to achieve an initial distance=max_speed_limit.
adjusted = True  # Initialize to True to enter the loop
while adjusted:
    positions = sorted(positions) # Sort the positions to ensure they are in ascending order after adjustments
    adjusted = False
    for i in range(num_vehicles):
        next_vehicle_index = (i + 1) % num_vehicles
        distance = (positions[next_vehicle_index] - positions[i]) % track_circumference
        if distance < 10*Max_Position_Delta:
            positions[next_vehicle_index] = (positions[i] + max_speed_limit) % track_circumference
            adjusted = True


# Create an empty DataFrame to store data
data = []

# Simulation loop
time_step=Max_Postion_Delta/Abs_Max_Speed
simulation_time = 10000  # Set the simulation time
for t in range(simulation_time):
    # Calculate the distance between vehicles
    distance_forward = [(positions[(i + 1) % num_vehicles] - positions[i]) % track_circumference for i in range(num_vehicles)]
    distance_backward = [(positions[(i - 1) % num_vehicles] - positions[i]) % track_circumference for i in range(num_vehicles)]

####################################################################################################    
#Commands for individual vehicles start here.
#This loop commands each vehicle to look for the nearest vehicle and adjust speed to get closer to it. 
#This version is supposed to encourage train forming, but upon first attempt, no vehicles passed the max_speed_limit.
#Also, it appears that the vehicles are still passing each other sometimes.  Need to enforce that better.
    # Update speeds based on distance to maintain constant distance and obey speed limit
    for i in range(num_vehicles):        
     if distance_forward < distance_backward: #if the closest vehicle is in front of you, speed up!
        if speeds[i] < max_speed_limit:
            if distance_forward[i] > (3*min_safe_distance):   
                speeds[i] += (1* acceleration_factor*time_step)
            elif distance_forward[i] > (2*min_safe_distance):
                speeds[i] += (0.5*acceleration_factor*time_step)
            elif distance_forward[i] < (2*min_safe_distance):
                speeds[i]-= (acceleration_factor*time_step)
            elif distance_forward[i] < min_safe_distance:
                speeds[i]=speeds[(i+1) % num_vehicles]
                speeds[i+1]+=(1* acceleration_factor*time_step)
                speeds[i]=speeds[i+1]
        elif speeds [i] > max_speed_limit:
            if distance_forward[i] > min_safe_distance: #if you have not formed a train, then you have to go the speed limit.
                speeds[i]=max_speed_limit
            elif distance_forward[i] < min_safe_distance: # if you have formed a train, then you can go faster.
                if speeds[i] < Abs_Max_Speed:
                 speeds[i+1]+=(1* acceleration_factor*time_step)
                 speeds[i]=speeds[i+1]
                elif speeds[i] > Abs_Max_Speed:
                    speeds[i]=Abs_Max_Speed
                    speeds[i+1]=Abs_Max_Speed
     elif distance_forward > distance_backward: #If the closest vehicle is behind you, slow down!
        if speeds[i] < max_speed_limit:
            if distance_backward[i] > (3*min_safe_distance):   
                speeds[i] -= (1*acceleration_factor*time_step)
            elif distance_backward[i] > (2*min_safe_distance):
                speeds[i] -= (0.5*acceleration_factor*time_step)
            elif distance_backward[i] < (2*min_safe_distance):
                speeds[i]+= (acceleration_factor*time_step)
            elif distance_backward[i] < min_safe_distance:
                speeds[i]=speeds[(i-1) % num_vehicles] 
                speeds[i]+=(1* acceleration_factor*time_step)
                speeds[i-1]=speeds[i]
        elif speeds [i] > max_speed_limit:
            if distance_backward[i] > min_safe_distance: #if you have not formed a train, then you have to go the speed limit.
                speeds[i]=max_speed_limit
            elif distance_backward[i] < min_safe_distance: # if you have formed a train, then you can go faster.
                if speeds[i] < Abs_Max_Speed:
                 speeds[i]+=(1* acceleration_factor*time_step)
                 speeds[i-1]=speeds[i]
                elif speeds[i] > Abs_Max_Speed:
                    speeds[i]=Abs_Max_Speed
                    speeds[i-1]=Abs_Max_Speed      
        
 #Possible additions:
####Train Forming#####
#1) need to adjust following distance commands to get total distance to zero to form a train.
#2) train-forming should be encouraged.  So, there should be some commands to adjust speeds up or down as necessary to get to zero distance.
    #This might require each vehicle to either slow down or speed up to converge upon the closest vehicle (ahead or behind it.)
#3) max_speed_limit should be increased incrementally as vehicles form a longer and longer train.   
    #2 + #3 would create a "race" to form the first 2-vehicle train. which would then have the highest speed limit and naturally catch up to the next vehicle...
    #...to form a 3-vehicle train and so-on

####Incremental Accelleration/Decelleration#####
#4)The accellerate/decellerate functions could be incrementalized to prevent overshooting distances & speeds, and to be more realistic in terms of what would be comfortable for passengers.
#5)In order to be more realistic, speeds/accellerations/distances should get units placed on them, and use numbers from my spreadsheet.
#6)The vehicles may need to be given a finite length.  So, they're represented as a line instead of a dot.

###Real World factors######
#7)Eventually, the cars should be given some kind of power unit simulation and a mass, so that we can consider inertia in their accell/decel calculations.
#8) imagine what information will come from what kind of sensors, and design code to simulate the input from real sensors. 

###Track Complexity#####
#Eventually, add complexity to the track according the the levels you defined in your notebook:
#9) Current setup: Single Track, 1 stop, one start, no off-ramps (Velocity coordination, but no route or best-route coordination)
#10) Single track with offramps, multiple starts/stops (Velocity coordination, route coordination, best route coordination)
#11) Multi-track, multiple start/stop, many routes to same destination (Velocity coordination, route coordination, best route coordination)    
 
        # Ensure speeds do not become negative
    speeds[i] = max(0, speeds[i])
#Commands for individual vehicles end here.
#######################################################################################################
   
    # Update positions
    for i in range(num_vehicles):
        positions[i] += speeds[i]*time_step
        positions[i] %= track_circumference  # Ensure positions are within the track's circumference


#The rest is just data reporting.#######################################################################
    # Store time, positions, and speeds in the data list
    data.append([t] + positions + speeds)


# Create a DataFrame from the data
column_names = ["Time"] + [f"Position_{i + 1}" for i in range(num_vehicles)] + [f"Speed_{i + 1}" for i in range(num_vehicles)]
df = pd.DataFrame(data, columns=column_names)

# Specify the full file path including "OneDrive - afacademy.af.edu"
excel_file_path = "~/OneDrive - afacademy.af.edu/Desktop/vehicle_positions_and_speeds.xlsx"
df.to_excel(excel_file_path, index=False)

print(f"Data saved to {excel_file_path}")
        

        
