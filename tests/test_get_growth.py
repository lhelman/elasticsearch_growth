import get_growth
import datetime


def test_indexname_to_point_valid():
    """
    Confirm that indexname_to_point() returns a valid point if given a valid filename with a date
    """
    ten_days_ago = datetime.date.today() - datetime.timedelta(10)
    assert get_growth.index_name_to_point(ten_days_ago.strftime('somelog_%Y.%m.%d'), '%Y.%m.%d') == -10


def test_indexname_to_point_invalid():
    """
    Confirm that indexname_to_point() returns None if given a valid filename with a date is not given
    """
    assert get_growth.index_name_to_point('somelog', '%Y.%m.%d') is None


def test_get_date_part_valid():
    """
    Confirm that get_date_part() returns the date if present
    """
    assert get_growth.get_date_part('somelog_2017.08.27', '%Y.%m.%d') == '2017.08.27'


def test_get_date_part_invalid():
    """
    Confirm that get_date_part() returns none if no date is present
    """
    assert get_growth.get_date_part('somelog_2017X08X27', '%Y.%m.%d') is None


def test_es_stats_to_total_size_per_day():
    """
    Confirm that the es_stats_to_total_size_per_day() returns properly
    """
    today = datetime.date.today()
    size_per_date_output = {}
    indices_input = {}
    for d in range(0, 30):
        date = today - datetime.timedelta(d)
        indices_input[date.strftime('somelog_%Y.%m.%d')] = {'total': {'store': {'size_in_bytes': 1000 + d}}}
        indices_input[date.strftime('othelog_%Y.%m.%d')] = {'total': {'store': {'size_in_bytes': 1230 + d * 13}}}
        size_per_date_output[-1 * d] = 1000 + d + 1230 + d * 13

    somelog_notime_size = 42
    someotherlog_notime_size = 24
    indices_input['somelog_notime'] = {'total': {'store': {'size_in_bytes': somelog_notime_size}}}
    indices_input['someotherlog_notime'] = {'total': {'store': {'size_in_bytes': someotherlog_notime_size}}}
    stats = {"indices": indices_input}
    assert get_growth.es_stats_to_total_size_per_day(stats, '%Y.%m.%d') == (
        size_per_date_output, somelog_notime_size + someotherlog_notime_size)
