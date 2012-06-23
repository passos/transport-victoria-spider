from lxml import etree
import re

from parser import Parser
import utils
import db

class StopParser(Parser):
    timetable_url_pattern = re.compile("line=(\d+).*stop=(\d+)")

    def __init__(self):
        pass

    def parse_stop_info(self):
        result = {}
        table_node = self.get_node(self.root, "//table[@id='stopInfo']")
        td_nodes = table_node.xpath("//td")

        #get title
        title = self.get_node_text(self.root, "//h1[@class='fn org']")
        if title is None:
            raise Exception('not a valid stop, title is empty')

        try:
            result['name'] = title[0:title.rindex('-')].strip()
        except:
            result['name'] = title

        result['address_street'] = self.get_node_text(td_nodes[0], "//span[@class='street-address']")
        result['address_locality'] = self.get_node_text(td_nodes[0], "//span[@class='locality']")
        result['address_postalcode'] = self.get_node_text(td_nodes[0], "//span[@class='postal-code']")

        location_name = self.get_node_text(td_nodes[1], "a")
        location_id = self.get_node(td_nodes[1], "a").get('href').split('/')[-1]
        if (location_id != '' and location_name != ''):
            db.update_table('location', 'id', location_id, name=location_name)
            result['location_id'] = location_id
        else:
            raise Exception('not a valid stop, location is empty,')

        result['tickets'] = ','.join([n.text for n in td_nodes[3].xpath("ul/li")])

        result['waiting_indoor'] = self.get_node_text(td_nodes[20].xpath("dl/dd")[0])
        result['waiting_sheltered'] = self.get_node_text(td_nodes[20].xpath("dl/dd")[1])

        result['bicycle_racks'] = self.get_node_text(td_nodes[22].xpath("dl/dd")[0])
        result['bicycle_lockers'] = self.get_node_text(td_nodes[22].xpath("dl/dd")[1])
        result['bicycle_cage'] = self.get_node_text(td_nodes[22].xpath("dl/dd")[2])

        result['geo_latitude'] = self.get_node_text(self.root, "//span[@class='latitude']")
        result['geo_longitude'] = self.get_node_text(self.root, "//span[@class='longitude']")

        fields_index = {
            'phone_lostproperty':2,
            'phone_feedback':4,
            'staff_available':5,
            'phone_station':6,
            'accessible':7,
            'metcard_ticket_machine':8,
            'myki_machine':9,
            'myki_checks':10,
            'vline_booking':11,
            'seating':12,
            'lighting':13,
            'stairs':14,
            'escalator':15,
            'lifts':16,
            'lockers':17,
            'public_phone':18,
            'public_toilet':19,
            'car_parking':21,
            'taxi_rank':23,
            'tactile_paths':24,
            'hearing_loop':25,
        }

        for k, v in fields_index.items():
            try:
                result[k] = self.get_node_text(td_nodes[v])
            except:
                print "Parse stop info error on %s, order %d" % (k,v)
                raise

        result['parsed'] = 'T'

    #     print "parsed stop info:\n\t", '\n\t'.join(["%s = %s" % (k,v) for k,v in result.items()])
        db.update_table_with_dict('stop', 'id', self.id, result)

        return result


    def parse_stop_route(self):
        stop_id = self.id
        type = self.get_node_text(self.root, "//div[@class='transportType']/h3").lower()

        # get route info in this stop
        route_nodes = self.root.xpath("//div[@class='lineInformationInner']/div/ul/li")

        for node in route_nodes:
            route_name = self.get_node_text(node, 'a')
            route_id = self.get_node(node, 'a').get('href').split('/')[-1]
            db.update_table('route', 'id', route_id, name=route_name, type=type)

            title=link=line_id=None

            for ttn in node.xpath('ul'):
                title = self.get_node_text(ttn, 'li')
                link = self.get_node(ttn, 'li/ul/li/a').get('href')
                groups = self.timetable_url_pattern.findall(link)
                if (len(groups) > 0):
                    line_id = groups[0][0]

            tt_id = utils.get_timetable_id(route_id, stop_id, line_id)
            print "  ", "parsed timetable '%s' %s" % (title, tt_id)
            db.update_table('timetable_index', 'id', tt_id,
                route_id=route_id, stop_id=stop_id, line_id=line_id,
                title=title, link=link)


    def parse(self, id, html):
        Parser.parse(self, id, html)
        self.parse_stop_info()
        self.parse_stop_route()
