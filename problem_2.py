from math import atan2, cos, radians, sin, sqrt
from pathlib import Path

import networkx as nx
import pandas as pd


data_folder = './data/Chennai GTFS'


def haversine_distance(loc_1, loc_2):
    radius = 6371  # km

    lat1, lon1 = loc_1
    lat2, lon2 = loc_2

    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)

    a = sin(d_lat / 2) * sin(d_lat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) * sin(d_lon / 2)
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    d = radius * c * 1000  # m

    return d


def create_network():
    network = nx.DiGraph()

    one_day = pd.to_timedelta(24, unit='hour')

    zero_time_diff = pd.to_timedelta(0)

    max_transfer_wait_time = pd.to_timedelta(15, unit='minute')

    days_of_week = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 7}

    agencies = ['CMRL', 'MTC', 'SR']

    for agency in agencies:
        agency_stops = pd.read_csv(f'{data_folder}/{agency}/stops.txt')
        agency_stop_times = pd.read_csv(f'{data_folder}/{agency}/stop_times.txt')
        agency_trips = pd.read_csv(f'{data_folder}/{agency}/trips.txt')
        agency_calendar = pd.read_csv(f'{data_folder}/{agency}/calendar.txt')

        agency_trip_groups = agency_stop_times.groupby('trip_id')

        for trip_id, trip_group in agency_trip_groups:
            service_id = agency_trips[agency_trips.trip_id == trip_id].service_id.iloc[0]
            route_id = agency_trips[agency_trips.trip_id == trip_id].route_id.iloc[0]

            for day in days_of_week.keys():
                if agency_calendar[agency_calendar.service_id == service_id][day].iloc[0] == 0:
                    continue

                trip_stops = trip_group.stop_id.to_list()
                for stop1, stop2 in zip(trip_stops[:-1], trip_stops[1:]):
                    network.add_edge(f'{stop1}-{trip_id}-{days_of_week[day]}', f'{stop2}-{trip_id}-{days_of_week[day]}', weight=0)

                for stop in trip_stops:
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['agency'] = f'{agency}'
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['stop_id'] = stop
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['trip_id'] = trip_id
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['route_id'] = route_id
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['day'] = days_of_week[day]
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['arr_time'] = pd.to_timedelta(trip_group[trip_group.stop_id == stop].arrival_time.iloc[0])
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['dep_time'] = pd.to_timedelta(trip_group[trip_group.stop_id == stop].departure_time.iloc[0])
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['lat'] = agency_stops[agency_stops.stop_id == stop].stop_lat.iloc[0]
                    network.nodes[f'{stop}-{trip_id}-{days_of_week[day]}']['lon'] = agency_stops[agency_stops.stop_id == stop].stop_lon.iloc[0]

                    network.add_edge(stop, f'{stop}-{trip_id}-{days_of_week[day]}', weight=0)
                    network.add_edge(f'{stop}-{trip_id}-{days_of_week[day]}', stop, weight=0)

        for stop, stop_attr in network.nodes(data=True):
            if stop_attr:
                for s, attr in [(node, data) for node, data in network.nodes(data=True) if node != stop and data and data['stop_id'] == stop_attr['stop_id']]:
                    if (stop_attr['day'] - attr['day'] == 0) and (zero_time_diff < (attr['dep_time'] - stop_attr['arr_time']) <= max_transfer_wait_time):
                        network.add_edge(stop, s, weight=1, distance=0)
                    elif (stop_attr['day'] - attr['day'] == -1 or stop_attr['day'] - attr['day'] == 6) and (zero_time_diff < (one_day + attr['dep_time'] - stop_attr['arr_time']) <= max_transfer_wait_time):
                        network.add_edge(stop, s, weight=1, distance=0)

    for agency in agencies:
        for stop, stop_attr in network.nodes(data=True):
            if stop_attr and stop_attr['agency'] == agency:
                for s, attr in [(node, data) for node, data in network.nodes(data=True) if data and data['agency'] != agency]:
                    d = haversine_distance((stop_attr['lat'], stop_attr['lon']), (attr['lat'], attr['lon']))
                    if d <= 500:
                        if (stop_attr['day'] - attr['day'] == 0) and (zero_time_diff < (attr['dep_time'] - stop_attr['arr_time'] - pd.to_timedelta(d / 1.25, unit='second')) <= max_transfer_wait_time):
                            network.add_edge(stop, s, weight=1, distance=d)
                        elif (stop_attr['day'] - attr['day'] == -1 or stop_attr['day'] - attr['day'] == 6) and (zero_time_diff (one_day + attr['dep_time'] - stop_attr['arr_time'] - pd.to_timedelta(d / 1.25, unit='second')) <= max_transfer_wait_time):
                            network.add_edge(stop, s, weight=1, distance=d)

    nx.write_graphml(network, f'{data_folder}/network.graphml')

    return network


if __name__ == '__main__':
    if not Path(f'{data_folder}/network.graphml').exists():
        transit_network = create_network()
    else:
        transit_network = nx.read_graphml(f'{data_folder}/network.graphml')

    origin = input('Enter origin stop id: ')

    lengths, paths = nx.single_source_dijkstra(transit_network, origin, weight='weight')

    destination = input('Enter any destination stop id: ')

    print(paths[destination])
