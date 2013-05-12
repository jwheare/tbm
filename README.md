Looks up where the Crossrail Tunnel Boring Machines are and prints a little status message, optionally posting to Twitter.

## Data sources
* http://www.crossrail.co.uk/route/near-you
* http://wiki.openstreetmap.org/wiki/Nominatim
* http://www.doogal.co.uk/london_stations.php

## Deps:
(Later versions may very well work fine)
* `python` [2.7.3](http://www.python.org/download/releases/2.7.3/)
 * `pyproj` [1.9.3](https://pypi.python.org/pypi/pyproj/1.9.3)
 * `twitter` [1.9.4](https://pypi.python.org/pypi/twitter/1.9.4)

## Install using virtualenv:
    # setup and activate virtualenv
    virtualenv tbm
    cd tbm ; ./bin/activate
    # clone this repo inside a src directory
    git clone https://github.com/jwheare/tbm.git src
    # install deps
    pip install pyproj==1.9.3
    pip install twitter==1.9.4
    # run
    cd tbm
    ./tbm.py
        Ada here. I'm under Mayfair, heading east towards Farringdon with 3.3km to go
        Hi, it's Elizabeth. I'm under Blackwall, heading west towards Farringdon with 7.2km to go
        This is Phyllis and I'm at Bond Street station, heading east towards Farringdon with 3km to go
        Hey, it's Sophia. I'm under Plumstead, heading west towards North Woolwich with 1.6km to go
        This is Victoria and I'm under Blackwall, heading west towards Farringdon with 7.6km to go

## Tweeting
Specify the following environment variables when running this script to post the updates to Twitter:

* `TBM_OAUTH_TOKEN`
* `TBM_OAUTH_SECRET`
* `TBM_CONSUMER_KEY`
* `TBM_CONSUMER_SECRET`
