from lxml import etree
import re
from parser import Parser
import utils
import db


class RouteParser(Parser):
    timetable_routeid_pattern = re.compile("itdLPxx_lineMain=(\d+)")
    timetable_lineid_pattern = re.compile("itdLPxx_lineID=(\d+)")
#     <img src="assets/Maps/Routes/GIFs/949_Bus733.gif" />
    map_image_link_pattern = re.compile('<img src="(assets/Maps.*\.gif)"')
#     201/202/302 combined - City - Box Hill/Doncaster via Belmore Road, Freeway
#     200 - City - Bulleen
    pattern_bus = re.compile('(.*?)-(.*)')
    pattern_via = re.compile('(.*)via(.*)', flags=re.IGNORECASE)
#     942 - NightRider - City - St Albans - Melton - Sunbury via Racecourse Road, Ballarat Road
    pattern_nightrider = re.compile('(.*?)-.*?-(.*?)-(.*)')
#     Lilydale - Chirnside Park (Telebus Area 1)
    pattern_telebus = re.compile('(.*?)-(.*) (\(.*\))')
#     Adelaide - Melbourne via Horsham, Ballarat & Geelong
    pattern_vline = re.compile('(.*?)-(.*)')

    def __init__(self):
        pass

    def parse_line_info(self, type, title):
        title = re.sub(' to ', ' - ', title, flags=re.IGNORECASE)
        (line, start, end, via) = (title, '', '', '')

        m = self.pattern_via.search(title)
        if m: (title, via) = m.groups()

        if type in ["metropolitan buses", "metropolitan trams", "regional buses"]:

            if 'telebus' in title:
                (start, end, via) = self.pattern_telebus.findall(title)[0]

            elif 'nightrider' in title:
                segs = title.split('-')
                line = segs[0]
                if len(segs) == 3:
                    via = segs[-1]

                if len(segs) == 4:
                    start = segs[2]
                    end = segs[-1]

                if len(segs) > 4:
                    start = segs[2]
                    end = ', '.join(segs[3:])
            else:
                m = self.pattern_bus.search(title)
                if m:
                    (a, b) = m.groups()
                    if a.strip().isdigit():
                        (line, start) = m.groups()
                        m = self.pattern_bus.search(start)
                        if m: (start, end) = m.groups()
                    else:
                        (start, end) = m.groups()

        elif type in ["v/line coaches", "v/line trains"]:
                line = title
                m = self.pattern_vline.search(title)
                if m: (start, end) = m.groups()
        else:
            line = title

        return {'line': line.strip(), 'starting': start.strip(),
            'ending': end.strip(), 'via': via.strip()}


    def parse_route_info(self):
        result = {}

        title = self.get_node_text(self.root, "//h1[@class='WheelChairAccess']")
        print '  ', title
        if title is None:
            raise Exception('%s is not a valid route' % self.id)
        title = re.sub('\s+', ' ', title).strip()
        result['title'] = title

        db.cur.execute("SELECT * from route WHERE id=?", (self.id,))
        row = db.cur.fetchone()

        if row:
            result.update(self.parse_line_info(row['type'], title))

        # parse the line map
        map_id = self.parse_map()
        if map_id:
            result['map_id'] = map_id

        # parse description
        desc_node = self.get_node(self.root, "//div[@class='routeDescriptionInner']")
        s = ''
        it = desc_node.itertext()
        try:
            s += it + "\n"
        except:
            pass

        result['desc'] = '\n'.join([re.sub('\s+', ' ', x) for x in s.split('\n') if re.sub('\s*', '', x) != ''])

        # set the parsed mark and update it to database
        result['parsed'] = 'T'
        db.update_table_with_dict('route', 'id', self.id, result)

    def parse_map(self):
        map_node = self.get_node(self.root, "//div[@class='routeMapInner']/a")
        if map_node is None: return None

        url = map_node.get('href')
        map_html = utils.get_html(utils.ptv_url + url)
        map_tree = etree.HTML(map_html)
        map_node = self.get_node(map_tree, "//div[@class='routeMapInner']/img")
        if map_node is None: return None

        # http://ptv.vic.gov.au/
        map_link = map_node.get('src')
        db.update_table('map', 'link', map_link)
        map_id = db.query("SELECT id FROM map WHERE link=?", (map_link,))

        return map_id


    def parse_timetable(self):
        tt_node = self.get_node(self.root, "//div[@class='timetablesInner']/ul")
        li_nodes = tt_node.xpath(".//li")
        for node in li_nodes:
            title = self.get_node_text(node, "./a")
            link = self.get_node(node, "./a").get('href')
            if link=="": continue

            line_id = self.timetable_lineid_pattern.findall(link)[0]
            tt_id = utils.get_timetable_id(route_id=self.id, line_id=line_id)
            print "  ", "parsed timetable '%s' %s" % (title, tt_id)

            db.update_table('timetable_index', 'id', tt_id,
                route_id=self.id, line_id=line_id, link=link, title=title)


    def parse(self, id, html):
        Parser.parse(self, id, html)
        self.parse_route_info()
        self.parse_timetable()