#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from stop_parser import StopParser
import db
import utils

MAX_STOP_COUNT = 23611

###########################################################################

if __name__ == "__main__":
    db.init()

    progress = int(db.get_param('stop_progress', 0))
    tobedone = xrange(progress+1, MAX_STOP_COUNT+1, 1)
    sp = StopParser()

    for id in tobedone:
        print "\n\nprocess stop id", id
        url = utils.get_stop_url(id)
        html = utils.get_html(url, data=id)
        try:
            sp.parse(id, html)
            db.cache_del(url)
        except Exception as e:
            print "  ", id, "failed, error:", e
            db.update_table('stop', 'id', id, parsed='F')

        db.set_param('stop_progress', id)

    db.close()
