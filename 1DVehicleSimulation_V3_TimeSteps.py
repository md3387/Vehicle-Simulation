import random
import pandas as pd

# Initialize parameters
num_vehicles = 5
track_circumference = 2000  #[m] Circumference of the circular track
Single_car_speed_limit = 30  #[m/s] Maximum speed limit [distance/time step]
Max_Position_Delta = 0.1 #[m] maximum chance allowed in position on each simulation loop
Speed_Limit_Multiplier = 1.2  #% of original speed limit[m/s]
max_vehicles = int(track_circumference/Single_car_speed_limit)-1 # limit the number of vehicles allowed on the track
num_vehicles=min(max_vehicles, num_vehicles) #reduce number of vehicles in simulation if user has specified more than the max
print(f"num_vehicles = {num_vehicles}") #print the number of vehicles you've accepted into the simulation
initial_positions = [random.uniform(0, track_circumference) for _ in range(num_vehicles)] #initialize positions in random order


# Generate random initial speeds for each vehicle
initial_speeds = [random.uniform(0, Single_car_speed_limit) for _ in range(num_vehicles)]
speeds = initial_speeds.copy() #[m/s]
acceleration = 3#[m/s^2] This is also the deceleration factor
min_safe_distance = 10*Max_Position_Delta #[m] Minimum safe following distance


# Sort the initial positions in ascending order
positions = sorted(initial_positions)

# Adjust positions iteratively to ensure distances are at least 10X the maximum change in position 
#This loop still doesn't seem to be iterating enough to achieve an initial distance=Single_car_speed_limit.
adjusted = True  # Initialize to True to enter the loop
while adjusted:
    positions = sorted(positions) # Sort the positions to ensure they are in ascending order after adjustments
    adjusted = False
    for i in range(num_vehicles):
        next_vehicle_index = (i + 1) % num_vehicles
        distance = (positions[next_vehicle_index] - positions[i]) % track_circumference
        if distance < 10*Max_Position_Delta:
            positions[next_vehicle_index] = (positions[i] + Single_car_speed_limit) % track_circumference
            adjusted = True


# Create an empty DataFrame to store data
data = []

# Simulation loop
time_step=Max_Position_Delta/(Speed_Limit_Multiplier*Single_car_speed_limit) #Should update this whenever speed limit changes
simulation_time = 10000  # Set the simulation time
for t in range(simulation_time):
    # Calculate the distance between vehicles
    distance_forward = [abs((positions[(i + 1) % num_vehicles] - positions[(i)% num_vehicles])) % track_circumference for i in range(num_vehicles)]
    distance_backward =[abs((positions[(i)% num_vehicles] - positions[(i - 1) % num_vehicles])) % track_circumference for i in range(num_vehicles)]

####################################################################################################    
#Commands for individual vehicles start here.
#This loop commands each vehicle to look for the nearest vehicle and adjust speed to get closer to it. 
#vehicles are now trending towards the nearest vehicle then matching speed and staying in order.
#****************
#However, vehicles accellerate or decellerate rapidly when they meet up, and we now need to encourage and form trains of >2 vehicles.
#This may require a completely reconfigured loop.
#******************
    # Update speeds based on distance to maintain constant distance and obey speed limit
    for i in range(num_vehicles):
     distance_to_equilibrate=((speeds[i]-speeds[i-1])^2)/(2*acceleration)        
     if distance_forward[i] < distance_backward[i]: #if the closest vehicle is in front of you, speed up!
        if speeds[i] < Single_car_speed_limit:
            if distance_forward[i] > distance_to_equilibrate:   
               speeds[i] += (acceleration*time_step)
            elif min_safe_distance < distance_forward[i] <= (distance_to_equilibrate):
                if speeds[i]>speeds[i+1]:
                   speeds[i]-= (acceleration*time_step)
                elif speeds[i]<speeds[i+1]:
                   speeds[i] += (1* acceleration*time_step)
            elif distance_forward[i] <= min_safe_distance:
                speeds[i]=speeds[(i+1) % num_vehicles]
                speeds[(i+1)% num_vehicles]+=(1* acceleration*time_step)
                speeds[i]=speeds[(i+1) % num_vehicles]
        elif speeds[i] >= Single_car_speed_limit:
            if distance_forward[i] > min_safe_distance: #if you have not formed a train, then you have to go the speed limit.
                speeds[i]=Single_car_speed_limit#slow down to the speed limit
                #speeds[(i+1)% num_vehicles]-=(1* acceleration*time_step) #the vehicle in front of you should slow down a bit to let you catch up.
            elif distance_forward[i] <= min_safe_distance: # if you have formed a train, then you can go faster.
                if speeds[i] < Speed_Limit_Multiplier*Single_car_speed_limit:
                 speeds[(i+1) % num_vehicles]+=(1* acceleration*time_step)
                 speeds[i]=speeds[(i+1) % num_vehicles]
                elif speeds[i] > Speed_Limit_Multiplier*Single_car_speed_limit:
                    speeds[i]=Speed_Limit_Multiplier*Single_car_speed_limit
                    speeds[(i+1)% num_vehicles]=Speed_Limit_Multiplier*Single_car_speed_limit
            
     elif distance_forward[i] > distance_backward[i]: #If the closest vehicle is behind you, wait for it!
        if speeds[i] < Single_car_speed_limit:
            if distance_backward[i] > (distance_to_equilibrate):  #if closest vehicle is far behind 
                speeds[i] = speeds[i] #continue at your current speed
            elif distance_backward[i] < (distance_to_equilibrate): #if closest vehicle is closing in....
               if distance_backward[i] > min_safe_distance: #...but still farther than the min. safe distance...
                if speeds[i] < speeds[(i-1) % num_vehicles]:#...and you're going slower than them...
                  speeds[i] += (0.5*acceleration*time_step) #...speed up a little to reduce the close rate, but not so much they can't catch up. 
                elif speeds[i]>=speeds[(i-1) % num_vehicles]:#but if you're going faster than the vehicle trying to catch up....
                  speeds[i]=speeds[(i-1) % num_vehicles] #...then slow down to match their speed (this will likely hold the distance constant, and prevent them from catching up).
               elif distance_backward[i] <= min_safe_distance: #if you've formed a train...
                 speeds[i]+=(1* acceleration*time_step) #...Speed up!
                 speeds[(i-1) % num_vehicles]=speeds[i] #And tell the car behind you to speed up with you.
        elif speeds [i] >= Single_car_speed_limit:
            if distance_backward[i] > min_safe_distance: #if you have not formed a train.... 
                 speeds[i]= Single_car_speed_limit #...then you have to go the speed limit.
            elif distance_backward[i] < min_safe_distance: # if you have formed a train....
                if speeds[i] < Speed_Limit_Multiplier*Single_car_speed_limit: #and you're going slower than the increased speed limit...
                 speeds[i]+=(1* acceleration*time_step)#...speed up!
                 speeds[(i-1)% num_vehicles]=speeds[i]#and bring the car behin
                elif speeds[i] > Speed_Limit_Multiplier*Single_car_speed_limit:
                    speeds[i]=Speed_Limit_Multiplier*Single_car_speed_limit
                    speeds[(i-1)% num_vehicles]=Speed_Limit_Multiplier*Single_car_speed_limit     
                    
             
        
 #Possible additions:
####Train Forming#####
#3) speed_limit should be increased incrementally as vehicles form a longer and longer train.   
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
     speeds[(i+1) % num_vehicles]= max(0, speeds[(i+1) % num_vehicles])
     speeds[(i-1) % num_vehicles]= max(0, speeds[(i-1) % num_vehicles])
#Commands for individual vehicles end here.
#######################################################################################################
   
    # Update positions
    for i in range(num_vehicles):
        positions[i] += speeds[i]*time_step
        positions[i] %= track_circumference  # Ensure positions are within the track's circumference

    print(t)
#The rest is just data reporting.#######################################################################
    # Store time, positions, and speeds in the data list
    data.append([t] + positions + speeds)


# Create a DataFrame from the data
column_names = ["Time"] + [f"Position_{i + 1}" for i in range(num_vehicles)] + [f"Speed_{i + 1}" for i in range(num_vehicles)]
df = pd.DataFrame(data, columns=column_names)


# Specify the full file path including "OneDrive - afacademy.af.edu"
excel_file_path = "~/Desktop/vehicle_positions_and_speeds.xlsx"
df.to_excel(excel_file_path, index=False)

print(f"Data saved to {excel_file_path}")
        

        
