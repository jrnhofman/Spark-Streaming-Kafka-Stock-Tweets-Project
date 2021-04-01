import csv

def get_authentication():

    # Change this to your twitter credential file
    reader = csv.reader(open('twitter.txt', 'r'))
    d = {}

    for row in reader:
        k, v = row
        d[k] = v

    return d