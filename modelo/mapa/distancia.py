import csv
from math import radians, sin, cos, sqrt, atan2
import csv
from math import radians, sin, cos, sqrt, atan2


# Read data from CSV file
def calculate_distance(lat1, lon1, lat2, lon2):
    # approximate radius of Earth in km
    R = 6371.0
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

data = []
# Read data from CSV file
with open('data.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    for row in reader:
        lat1 = float(row[0])
        lon1 = float(row[1])
        data.append((lat1, lon1))

distances = {}

# Calculate distances between each pair of points
for i in range(len(data)):
    lat1, lon1 = data[i]
    distances[(lat1, lon1)] = {}

    for j in range(i+1, len(data)):
        lat2, lon2 = data[j]
        distance = calculate_distance(lat1, lon1, lat2, lon2)
        distances[(lat1, lon1)][(lat2, lon2)] = distance

# Write distances to CSV file
with open('distance.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([''] + [f'Station {i+1}' for i in range(len(data))])

    for i in range(len(data)):
        station_num = i + 1
        row = [f'Station {station_num}']
        for j in range(len(data)):
            if i == j:
                row.append('')
            else:
                distance = distances.get(data[i], {}).get(data[j], 0)
                row.append(distance)
        writer.writerow(row)

print(distances.get(data[i], {}).get(data[j], 0))
