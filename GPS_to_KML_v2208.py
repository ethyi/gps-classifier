"""
GPS Classifer, converts GPS data to a classified KML file
@author: Ethan Yi | ehy5032@rit.edu
"""
import math

import pynmea2
import argparse

import datetime as dt
import numpy as np
from output_KML import *
from test_KML import *
from scipy.signal import argrelextrema


# class that holds a gps coordinate
class Point:
    # a point either has speed and direction or altitude
    speed = None  # speed of point
    direction = None  # direction of point relative to north
    altitude = None  # altitude of point

    def __init__(self, lon, lat, time):
        self.longitude = lon  # longitude of point
        self.latitude = lat  # latitude of point
        self.time = time  # elapsed time in seconds
        self.color = 'black'  # associated default color pin


def read_gps(gps_filename):
    """
    read gps data and output arrays of coordinates, one with speeds,
    one with altitudes
    :param gps_filename: the gps filename
    :return: 2 lists of points, one containing speed, the other altitude
    """
    speed_data = []  # list for storing gps coordinates with speed
    altitude_data = []  # list for storing gps coordinates with altitude
    with open(gps_filename, 'r') as file:
        for line in file.readlines():
            try:
                msg = pynmea2.parse(line)
                if msg.sentence_type == 'RMC':  # check speed coordinates
                    speed_data.append(msg)
                elif msg.sentence_type == 'GGA':  # check altitude coordinates
                    altitude_data.append(msg)
            except pynmea2.ParseError as e:
                # print('Parse error: {}'.format(e))
                continue
    return speed_data, altitude_data


def get_time_elapsed(start, end):
    """
    get the time elapsed in seconds between the datetime.time objects
    :param start: start time
    :param end: end time
    :return: time elapsed in seconds
    """
    date = dt.date(1, 1, 1)  # a calendar day to use
    start_time = dt.datetime.combine(date, start)  # combine day with time
    end_time = dt.datetime.combine(date, end)
    # subtracting times only works with calendar dates and times
    time_elapsed = end_time - start_time
    # get seconds with microseconds
    time_elapsed = time_elapsed.seconds + time_elapsed.microseconds / 1000000
    return time_elapsed


def convert_gps(raw_speed, raw_altitude):
    """
    converts a list of raw GPS data into 2 lists of gps Point objects
    :param raw_speed: gps data with speeds
    :param raw_altitude: gps data with altitudes
    :return: the converted lists of data
    """
    start_time = raw_speed[0].timestamp  # references the starting time
    speed_data = []
    quant = 1  # quantization value for speeds and direction
    for line in raw_speed:
        # get location attributes
        lon = line.longitude
        lat = line.latitude
        time = get_time_elapsed(start_time, line.timestamp)
        # build object
        point = Point(lon, lat, time)
        # add additional attributes for speed and direction
        speed = math.floor(line.spd_over_grnd / quant) * quant  # quantized
        direction = math.floor(line.true_course / quant) * quant
        point.speed = speed
        point.direction = direction
        speed_data.append(point)  # add point to list of speed points

    quant = 0.5  # quantization value for altitudes
    altitude_data = []
    for line in raw_altitude:
        # get location attributes
        lon = line.longitude
        lat = line.latitude
        time = get_time_elapsed(start_time, line.timestamp)
        # build object
        point = Point(lon, lat, time)
        # add additional attributes for speed and direction
        altitude = math.floor(line.altitude / quant) * quant
        point.altitude = altitude
        altitude_data.append(point)  # add point to list of altitude points

    return speed_data, altitude_data


def clean_speed(data):
    """
    cleans the speed data by removing adjacent repeated values
    :param data: the speed data to clean
    :return: the cleaned data
    """
    repeat_point = data[0]  # the point to see if it is repeated
    cleaned_data = [repeat_point]  # add unique point to new list
    for index in np.arange(1, len(data)):
        point = data[index]
        if repeat_point.speed != point.speed:  # if point is not repeated
            repeat_point = point  # establish new repeat point
            cleaned_data.append(repeat_point)  # add the unique point
    return cleaned_data


def clean_altitude(data):
    """
    cleans the altitude data by removing large adjacent differences
    :param data: the data to clean
    :return: the cleaned data
    """
    cleaned_data = []
    for index in np.arange(len(data) - 1):
        current = data[index]
        next = data[index + 1]
        # difference between adjacent points
        diff = abs(current.altitude - next.altitude)
        if diff < 5:  # if difference is small, include the point
            cleaned_data.append(current)
    return data


def classify_stop(data):
    """
    classifies stops for stop light or errands using speed data
    :param data: the speed data
    """
    # classifies errands
    for index, point in enumerate(data):
        if point.speed == 0:  # if car not moving
            if index == len(data) - 1:  # if last point, classify as errand
                point.color = 'yellow'

            else:
                # if the car's next non-zero speed is 2 minutes away
                # then it is an errand
                elapsed = data[index + 1].time - point.time
                if elapsed > 120:
                    point.color = 'yellow'
                else:  # otherwise it is a stop sign
                    point.color = 'pink'

    # classifies stop lights, stop signs, (speed bumps)
    speed_list = []
    for point in data:  # build a list of speeds
        speed_list.append(point.speed)
    # find local minimums
    local_min = argrelextrema(np.array(speed_list), np.less)
    for index in local_min[0]:
        point = data[index]
        # if a local minimum is under a certain threshold, classify stop sign
        if point.speed < 12 and point.color != 'yellow':
            data[index].color = 'pink'


def best_fit_slope(x, y):
    """
    find the slope of the line of best fit for the x,y coordinates
    :param x: list of x coordinates
    :param y: list of y coordinates
    :return: the slope of the line of best fit
    """
    mean_x, mean_y = np.mean(x), np.mean(y)  # get means
    numer, denom = 0, 0
    n = len(x)  # get length
    # use least square method to get slope
    for i in np.arange(n):
        numer += (x[i] - mean_x) * (y[i] - mean_y)
        denom += (x[i] - mean_x) ** 2
    m = numer / denom
    return m


def classify_height(data):
    """
    classifies if going uphill, downhill, or flat using altitude data
    :param data: altitude data
    """
    # determines how high a slope is needed to be considered uphill
    slope_threshold = 0.2   # lower for more detail
    # the amount of surrounding data to use to find the slope
    increments = 20     # lower for more detail
    radius = increments // 2
    for index in np.arange(radius, len(data) - radius):
        point = data[index]
        time_list = []  # x list for slope
        altitude_list = []  # y list for slope
        # iterate around the data point by 'radius' amount
        for i in np.arange(increments):
            incremented_point = data[index + i - radius]
            time_list.append(incremented_point.time)
            altitude_list.append(incremented_point.altitude)
        # get line of best fit slope
        slope = best_fit_slope(time_list, altitude_list)

        if slope > slope_threshold:     # uphill
            point.color = 'red'
        elif slope < slope_threshold * -1:  # downhill
            point.color = 'green'
        else:   # flat
            point.color = 'cyan'


def main():
    """
    reads in filenames, gets data, classifies data, then writes to a KML file
    """
    # parse filenames
    parser = argparse.ArgumentParser(description='Processes GPS data')
    parser.add_argument('gps_filename', help='filename of input GPS file')
    parser.add_argument('kml_filename', help='filename of output KML file')
    args = parser.parse_args()
    # read gps data
    raw_speed, raw_altitude = read_gps(args.gps_filename)
    speed_data, altitude_data = convert_gps(raw_speed, raw_altitude)
    # clean gps data, extract useful data
    speed_data = clean_speed(speed_data)
    altitude_data = clean_altitude(altitude_data)
    # classify data
    classify_stop(speed_data)
    classify_height(altitude_data)

    # [OPTIONAL] for visualization and testing purposes
    # plot_speed(speed_data)
    # plot_altitude(altitude_data)

    # output KML file
    write_kml(args.kml_filename, speed_data, altitude_data)


if __name__ == "__main__":
    main()
