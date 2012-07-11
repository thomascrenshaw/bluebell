from datetime import datetime

def get_localization_callsigns_data(callsign_by_zip_data, zipcode):
    ztc_data = []
    if not callsign_by_zip_data:
        return
    for item in callsign_by_zip_data['$items']:
        scn = item['$links'][0]['$links'][0]['short_common_name']
        ztc_data.append({scn: {
            'short_common_name': scn,
            'flagship':
                item['$links'][0]['$links'][0]['$links'][1]['callsign'],
            'confidence': item['confidence'],
            'rank': item['rank'],
            'callsign': item['$links'][0]['callsign']}
        })
    return _group_callsign_data(ztc_data)


def get_listing_callsigns_data(callsign_by_zip_data, zipcode):
    callsigns_feed_url = []
    for item in callsign_by_zip_data['$items']:
        if item['confidence'] == 100 and item['rank']:
            callsign = item['$links'][0]['callsign']
            callsigns_feed_url.append({
                callsign: item['$links'][0]['$links'][1]['$self']
            })
    return callsigns_feed_url


def get_feed_data(callsigns_feed_data):
    feeds_listing_url = []
    for item in callsigns_feed_data['$items']:
        feed = item['$links'][1]['full_name']
        feeds_listing_url.append({
            feed: item['$links'][2]['$self']
        })
    return feeds_listing_url


def get_listing_data(feed_listings_data):
    listing_data = []
    for item in feed_listings_data['$items']:
        start_date = item['start_date']
        start_time = item['start_time']
        listing_datetime = datetime.strptime(
            start_date + start_time,
            '%Y%m%d%H%M'
        )
        # TODO(calinf) Use timedelta for time comparison.
        if listing_datetime.date() == datetime.today().date():
            current_hour = datetime.now().hour
            if (listing_datetime.hour > current_hour and
                listing_datetime.hour < current_hour + 4):
                listing_data.append({
                    'start_date': start_date,
                    'start_time': start_time,
                    'duration': item['duration'],
                    'title': item['$links'][1]['title'],
                })
    return listing_data


def _group_callsign_data(ztc_data):
    stations = {}
    stations_merged_data = {}
    for ztc in ztc_data:
        for s_common_name, station_data in ztc.iteritems():
            if s_common_name not in stations:
                stations_merged_data = {}
            else:
                stations_merged_data = stations[s_common_name]
            for key in station_data:
                stations_merged_data.setdefault(
                    key, []).append(station_data[key]
                )
                stations[s_common_name] = stations_merged_data
    unique_scn = set()
    ztc_data_keys = [unique_scn.add(item.keys()[0]) or item.keys()[0]
        for item in ztc_data if item.keys()[0] not in unique_scn
    ]
    return [stations.get(item) for item in ztc_data_keys]
