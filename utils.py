import urllib2
from urllib2 import URLError
import db

ptv_url = 'http://ptv.vic.gov.au/'

def get_html(url, data=None):
    try:
        result = db.cache_get(url)

        if result is None:
            result = urllib2.urlopen(url).read()
            db.cache_put(url, result, data=data, done='F')

        return result

    except URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to get html, reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server return error code: ', e.code
        raise

def get_stop_url(id):
    return "http://ptv.vic.gov.au/stop/view/%s" % (id)

def get_location_url(id):
    return "http://ptv.vic.gov.au/location/view/%s" % (id)

def get_route_url(id):
    return "http://ptv.vic.gov.au/route/view/%s" % (id)

def get_timetable_url(lineid, stopid):
    return "http://tt.ptv.vic.gov.au/tt/XSLT_REQUEST?itdLPxx_line=%s&itdLPxx_stop=%s" % (lineid, stopid)

def get_timetable_id(route_id=None, stop_id=None, line_id=None):
    return "%s.%s.%s" % (route_id, stop_id, line_id)