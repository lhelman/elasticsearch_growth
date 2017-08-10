#!/usr/bin/env python
# -*- coding: utf8 -*-
import argparse
import sys
import datetime
import re
import json
import numpy as np

def indexname_to_point(indexname, dateformat):
    date_part = get_date_part(indexname, dateformat)
    if date_part:
        d = datetime.datetime.strptime(date_part, dateformat).date()
        x = (datetime.date.today() - d).days
        return x
    return None


def get_date_part(indexname, dateformat):
    regexp_date = get_regexp_from_dateformat(dateformat)
    m = re.search(regexp_date, indexname)
    if m:
        # print "DEBUGLEOH: {} {} found".format(indexname, dateformat)
        return m.group(0)
    # print "DEBUGLEOH: {} {} NOT found".format(indexname, dateformat)
    return None

def get_regexp_from_dateformat(dateformat):
    regexp_date = dateformat
    regexp_date = regexp_date.replace('.', '\\.').replace('%Y', '\\d\\d\\d\\d').replace('%m', '\\d\\d').replace('%d', '\\d\\d')
    regexp_date = '(' + regexp_date + ')'
    return regexp_date


def es_stats_to_total_size_per_day(f, dateformat, discard_days):
    print "DEBUGLEOH f={} dateformat={} discard_days={}".format(f, dateformat, discard_days)
    size_per_day = dict()
    constants = 0
    #with open(filename, 'r') if filename else sys.stdin as f:
    #    j = json.load(f)
    j = json.load(f)

    for index_name, o in j["indices"].iteritems():
        size_in_bytes = o["total"]["store"]["size_in_bytes"]
        days_before = indexname_to_point(index_name, dateformat)
        if days_before is not None:
            # Discard today, because it's not complete
            print "DEBUGLEOH: days_before {} discard_days {}".format(days_before, discard_days)
            if days_before != 0 and days_before < discard_days:
                print "DEBUGLEOH: Mete un dia mas"
                size_per_day[days_before] = size_per_day.get(days_before, 0) + size_in_bytes
        else:
            constants = constants+size_in_bytes
    return size_per_day, constants

def least_squares(size_per_day):
  x = np.array([-1*i for i in size_per_day.keys()])
  y = np.array(size_per_day.values())
  A = np.vstack([x, np.ones(len(x))]).T
  m, c = np.linalg.lstsq(A, y)[0]
  return x, y, m, c


def main(options):
  size_per_day, constants = es_stats_to_total_size_per_day(options.filename, options.dateformat, options.discard)
  x, y, m, c = least_squares(size_per_day)
  #c = c + constants
  print "m={0}, c={1}".format(m, c)
  # print "Prediction for the next {0} days is:{1}".format(next_days, m*next_days+c)

  if options.plot:
    import matplotlib.pyplot as plt
    plt.plot(x, y, 'o', label='Original data', markersize=10)
    plt.plot(x, m*x + c, 'r', label='Fitted line')
    plt.legend()
    plt.show()


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
                        help='Discard any day older than this amount of days')
    parser.add_argument('-n', '--next_days',
                        help='How many days into the future we want the predicted amount',
                        type=int,
                        required=True)
    parser.add_argument('-p', '--plot',
                        help='Service',
                        action='store_true')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    options = get_options()
    main(options)

# vim:set ft=python fileencoding=utf-8 sr et ts=4 sw=4 : See help 'modeline'

