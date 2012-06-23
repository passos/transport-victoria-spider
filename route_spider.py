#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from route_parser import RouteParser
import db
import utils

###########################################################################

if __name__ == "__main__":
    db.init()

    progress = int(db.get_param('route_update_progress', 0))
    db.cur.execute("SELECT id FROM route WHERE id > ? ORDER BY id", (progress,))
    rows = db.cur.fetchall()
    tobedone = map(lambda x: x[0], rows)

    rp = RouteParser()

    for id in tobedone:
        print "\n\nupdate route id", id
        url = utils.get_route_url(id)
        html = utils.get_html(url, data=id)
        try:
            rp.parse(id, html)
            db.cache_del(url)
        except Exception as e:
            print "  ", id, "failed, error:", e
            db.update_table('route', 'id', id, parsed='F')
            raise

        db.set_param('route_update_progress', id)


    db.close()
