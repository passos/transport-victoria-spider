from lxml import etree
import re
from parser import Parser
import utils
import db


class LocationParser(Parser):

    def __init__(self):
        pass


    def parse_location_info(self):
        result = {}

        name = self.get_node_text(self.root, "//div[@class='top_left']/h1")
        print '  ', name
        if name is None:
            raise Exception('%s is not a valid location' % self.id)
        result['name'] = name.strip()

        db.cur.execute("SELECT * from location WHERE id=?", (self.id,))
        row = db.cur.fetchone()

        # parse the line map
        map_id = self.parse_map()
        if map_id:
            result['map_id'] = map_id

        # parse suburbs
        suburbs = self.get_node_text(self.root, "//div[@class='suburbsInner']/p")
        if suburbs is None:
            print "empty suburbs, should not happen"
        result['suburbs'] = ' '.join([re.sub('\s+', ' ', x).strip() for x in suburbs.split('\n') if re.sub('\s*', '', x) != ''])


        # set the parsed mark and update it to database
        result['parsed'] = 'T'
        db.update_table_with_dict('location', 'id', self.id, result)


    def parse_map(self):
        map_node = self.get_node(self.root, "//div[@class='mapInner']/a")
        if map_node is None: return None

        # http://ptv.vic.gov.au/
        map_link = map_node.get('href')
        db.update_table('map', 'link', map_link)
        map_id = db.query("SELECT id FROM map WHERE link=?", (map_link,))

        return map_id


    def parse(self, id, html):
        Parser.parse(self, id, html)
        self.parse_location_info()