#!/usr/bin/env python
# -*- coding: utf8 -*-
import argparse
import datetime
import json
import re
import sys

import numpy as np
from humanize import naturalsize


def index_name_to_point(index_name, date_format):
    date_part = get_date_part(index_name, date_format)
    if date_part:
        d = datetime.datetime.strptime(date_part, date_format).date()
        x = (d - datetime.date.today()).days
        return x
    return None


def get_date_part(index_name, date_format):
    regexp_date = get_regexp_from_date_format(date_format)
    m = re.search(regexp_date, index_name)
    if m:
        return m.group(0)
    return None


def get_regexp_from_date_format(date_format):
    regexp_date = date_format
    regexp_date = regexp_date.replace('.', '\\.')\
        .replace('%Y', '\\d\\d\\d\\d')\
        .replace('%m', '\\d\\d')\
        .replace('%d', '\\d\\d')
    regexp_date = '(' + regexp_date + ')'
    return regexp_date


def es_stats_to_total_size_per_day(stats, dateformat):
    size_per_day = dict()
    constants = 0

    for index_name, o in stats["indices"].iteritems():
        size_in_bytes = o["total"]["store"]["size_in_bytes"]
        day = index_name_to_point(index_name, dateformat)
        if day is not None:
            size_per_day[day] = size_per_day.get(day, 0) + size_in_bytes
        else:
            constants = constants + size_in_bytes
    return size_per_day, constants


def least_squares(size_per_day):
    x = np.array(size_per_day.keys())
    y = np.array(size_per_day.values())
    a = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(a, y)[0]

    if options.plot:
        import matplotlib.pyplot as plt
        plt.plot(x, y, 'o', label='Original data', markersize=10)
        plt.plot(x, m * x + c, 'r', label='Fitted line')
        plt.legend()
        plt.show()

    return m, c


def filter_size_per_day(first_day, last_day, d):
    """
    Include first limit, do not include last
    """
    return {k: v for k, v in d.iteritems() if first_day <= k < last_day}


def main():
    stats = json.load(options.filename)
    full_size_per_day, constants = es_stats_to_total_size_per_day(stats, options.dateformat)
    analized_size_per_day = filter_size_per_day(-1 * options.discard, 0, full_size_per_day)
    if not analized_size_per_day:
        print "No date based indices match, Non date based sum={0}".format(constants)
        exit()

    m, c = least_squares(analized_size_per_day)
    c = c + constants
    print "y=m*x+b m={0}, c={1}".format(m, c)
    used_current = sum(filter_size_per_day(-1 * options.store_days, 0, full_size_per_day).values())
    predicted_from = options.next_days - options.store_days
    predicted_to = options.next_days
    used_predicted = sum([m * x + c for x in range(predicted_from, predicted_to)])
    print "Current storage needed for {0} days: {3} " \
          "Predicted storage needed from day {1} to day {2} period: {4}".format(options.store_days,
                                                                                predicted_from,
                                                                                predicted_to,
                                                                                naturalsize(used_current),
                                                                                naturalsize(used_predicted))


def get_options():
    """Build options parser."""
    parser = argparse.ArgumentParser(description="Define target filters")
    parser.add_argument('-f', '--filename',
                        default=sys.stdin, type=argparse.FileType('r'),
                        help='Filename with the output of a curl -s localhost:9200/_stats ' +
                             'if not present it will try to read it from stdin')
    parser.add_argument('-o', '--dateformat',
                        help='Indices Date format',
                        default='%Y.%m.%d')
    parser.add_argument('-x', '--discard',
                        type=int,
                        default=float('inf'),
                        help='Discard any day older than this amount of days')
    parser.add_argument('-n', '--next_days',
                        help='How many days into the future we want the predicted amount',
                        type=int,
                        required=True)
    parser.add_argument('-s', '--store_days',
                        help='How many days do we want to store. Default 30',
                        type=int,
                        default=30)
    parser.add_argument('-p', '--plot',
                        help='Service',
                        action='store_true')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    options = get_options()
    main()

# vim:set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'
