#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from location_parser import LocationParser
import db
import utils

###########################################################################

if __name__ == "__main__":
    db.init()

    progress = 0 #int(db.get_param('location_update_progress', 0))
    db.cur.execute("SELECT id FROM location WHERE id > ? ORDER BY id", (progress,))
    rows = db.cur.fetchall()
    tobedone = map(lambda x: x[0], rows)

    lp = LocationParser()

    for id in tobedone:
        print "\n\nupdate location id", id
        url = utils.get_location_url(id)
        html = utils.get_html(url, data=id)
        try:
            lp.parse(id, html)
            db.cache_del(url)
        except Exception as e:
            print "  ", id, "failed, error:", e
            db.update_table('location', 'id', id, parsed='F')
            raise

        db.set_param('location_update_progress', id)


    db.close()
