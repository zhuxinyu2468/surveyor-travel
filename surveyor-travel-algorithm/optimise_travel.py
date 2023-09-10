import math
import sys

import utm  # Coordinates are converted to UTM format for analysis in metres (assume they are in same zone)
import numpy as np
import folium
from folium import plugins


# Take a list of lat/lon coords and extract out the easting and northing vectors (in m)
# NOTE: For the purposes of this exercise we can ignore differing zone letters and numbers
def convert_to_utm_xy(coordinates):
    return [utm.from_latlon(*c)[:2] for c in coordinates]


def calc_total_distance(coordinates_xy, indices):
    total_distance = 0
    for i in range(1, len(indices)):
        dx = coordinates_xy[indices[i]][0] - coordinates_xy[indices[i - 1]][0]
        dy = coordinates_xy[indices[i]][1] - coordinates_xy[indices[i - 1]][1]
        total_distance += math.sqrt(dx * dx + dy * dy)
    return total_distance


def optimise_travel_order(coordinates, survey_time=None):
    coordinates_xy = convert_to_utm_xy(coordinates)
    num_sites = len(coordinates_xy)
    dis_matrix = np.zeros((num_sites, num_sites))
    avg_driving_speed = 50000

    for i in range(num_sites):
        for j in range(num_sites):
            dx = coordinates_xy[i][0] - coordinates_xy[j][0]
            dy = coordinates_xy[i][1] - coordinates_xy[j][1]
            distance = math.sqrt(dx * dx + dy * dy)
            dis_matrix[i, j] = distance

    best_dis = sys.maxsize
    for i in range(10):
        indices = list(range(num_sites))
        start_point = np.random.randint(num_sites)

        route = [start_point]
        indices.remove(start_point)
        total_dis = 0
        # survey_time : a list of time each site
        total_tim = 0

        while indices:
            sorted_indices = np.argsort(dis_matrix[start_point, :])
            nearest_point = [idx for idx in sorted_indices if idx in indices][0]
            travel_tim = dis_matrix[start_point, nearest_point] / avg_driving_speed
            total_tim += travel_tim

            if survey_time:
                total_tim += survey_time[start_point]

            total_dis += dis_matrix[start_point, nearest_point]
            route.append(nearest_point)
            indices.remove(nearest_point)
            start_point = nearest_point

        if survey_time:
            total_tim += survey_time[route[-1]]

        if total_dis < best_dis:
            best_dis = total_dis
            best_route = route

    return best_route


def plot_route(coordinates, route):
    m = folium.Map(location=coordinates[0], zoom_start=12)
    coordinates = np.array(coordinates)
    route = np.array(route)
    data = coordinates[route]
    for i in range(0, len(data)):
        folium.Marker(
            location=data[i],
            popup=folium.Popup(
                f'Order in path: {i} <br> Coordinate :{data[i]}',
                max_width=300,
                min_width=200),
        ).add_to(m)

    antpath = plugins.AntPath(locations=data)
    antpath.add_to(m)
    # Show the map
    return m


if __name__ == '__main__':
    coordinates = [
        (-36.932197, 174.987783),
        (-36.969210, 174.912630),
        (-37.008773, 174.835551),
        (-36.812159, 174.782783),
        (-36.987639, 174.850803),
        (-36.987525, 174.756794)
    ]
    print(f'The best route indices: {optimise_travel_order(coordinates)}')
    survey_time = [5, 4, 2, 4, 4, 4]
    best_route = optimise_travel_order(coordinates, survey_time)
    print(f'The best route indices: {best_route}, further add the survey time at the sites')
    coordinates_xy = convert_to_utm_xy(coordinates)
    total_distance = calc_total_distance(coordinates_xy, best_route)
    print(f'total_distance: {total_distance}')
    plt = plot_route(coordinates, best_route)
    plt_dir_path = 'best_route_plt'
    plt.save(plt_dir_path + '.html')
    print(f'Plot has been saved, check file {plt_dir_path}')
