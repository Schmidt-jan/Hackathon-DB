from flask import Flask, jsonify
import time
import math

app = Flask(__name__)

# Define the waypoints for a 5x5 square
waypoints = [[0, 0], [5, 0], [5, 5], [0, 5], [0, 0]]

# Velocity to complete one loop in 10 seconds
velocity = 2.0  # meters per second

# Calculate the cumulative distances between waypoints
cumulative_distances = []
total_distance = 0

def calculate_distances(points):
    """Calculate the cumulative distances between waypoints."""
    distances = []
    total = 0
    for i in range(1, len(points)):
        dist = math.dist(points[i-1], points[i])
        total += dist
        distances.append(total)
    return distances

# Precompute distances and total distance
cumulative_distances = calculate_distances(waypoints)
total_distance = cumulative_distances[-1]

def get_position_at_time(t):
    """Calculate the current position based on time and velocity."""
    global waypoints, cumulative_distances
    
    # Normalize time for looping (modulo total time for a full loop)
    loop_time = total_distance / velocity
    t = t % loop_time

    # Total distance covered in time t
    distance_covered = t * velocity

    # Find which segment the object is in based on distance
    for i, cumulative_distance in enumerate(cumulative_distances):
        if distance_covered <= cumulative_distance:
            # Interpolate between waypoints[i] and waypoints[i + 1]
            prev_distance = cumulative_distances[i - 1] if i > 0 else 0
            ratio = (distance_covered - prev_distance) / (cumulative_distance - prev_distance)
            start_point = waypoints[i]
            end_point = waypoints[i + 1]
            current_position = [
                start_point[j] + ratio * (end_point[j] - start_point[j])
                for j in range(len(start_point))
            ]
            return current_position
    
    # If the distance exceeds the last waypoint, return the last point
    return waypoints[-1]

@app.route('/position', methods=['GET'])
def get_position():
    """Get the current position of the object."""
    # Calculate elapsed time
    elapsed_time = time.time()  # No need for a start time since we continuously loop
    
    # Get the current position based on elapsed time
    current_position = get_position_at_time(elapsed_time)
    
    return jsonify({"position": current_position})

if __name__ == '__main__':
    app.run(debug=True)
