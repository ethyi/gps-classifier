"""
test_KML
Contains methods for graphing/testing the classifications
@author: Ethan Yi | ehy5032@rit.edu
"""
import matplotlib.pyplot as plt


def plot_speed(data):
    """
    plot the speed data
    :param data: the speed data
    """
    timestamp_list = []
    speed_list = []
    color_list = []
    for point in data:
        timestamp_list.append(point.time)
        speed_list.append(point.speed)
        color_list.append(point.color)

    plt.scatter(timestamp_list, speed_list, c=color_list)
    plt.xlabel('Time ->')
    plt.ylabel('Speed ->')
    plt.show()


def plot_altitude(data):
    """
    plot the altitude data
    :param data: the altitude data
    """
    timestamp_list = []
    alt_list = []
    color_list = []
    for point in data:
        timestamp_list.append(point.time)
        alt_list.append(point.altitude)
        color_list.append(point.color)

    plt.scatter(timestamp_list, alt_list, c=color_list)
    plt.xlabel('Time ->')
    plt.ylabel('Altitude ->')
    plt.show()