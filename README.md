# Math for predicting elasticsearch growth

This program calculates the amount of space used by the
indices (as reported by a call to `_stats` API).

The indices without names on their dates are taken as constants, which
might or might not be your case.

Based on the total amount of bytes for each day, with date on its index name,
we run a least squares line across it and we can predict (if the usage pattern
is linear) the amount of disk needed in the future.

There is an option to see the plot of daily totals, to know visually if a linear
pattern is correct enough.

The prediction is given after exiting the plot screen.


# Install

If you like virtual envs, you can run:

```bash
mkdir ~/virtualenvs
virtualenv ~/virtualenvs/elasticsearch_growth
. ~/virtualenvs/elasticsearch_growth/bin/activate
```

```bash
pip install -r requirements.txt
```

# Examples

For a full command description use

```bash
./get_growth.py --help
```

How much space will use in 4 Months (120 days) if we want to store
30 days of storycal data, but discarding older data than 20 days (we 
can use the discard functionality to remove some weird data).
Plot afterwards.

```bash
curl -s localhost:9200/_stats > _stats.json
./get_growth.py -f _stats.json -x 20 -n 120 -s 30 --plot
```

# Testing

```bash
pip install pytest
python -m pytest
```



# Pending enhancenments

The least squares algorithm might be easily replaced, and specifyied with options.

