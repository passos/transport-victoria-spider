from lxml import etree

class Parser:
    root = None
    id = None


    def __init__(self):
        pass


    def load(self, html):
        self.root = etree.HTML(html)


    def get_node(self, tree, xpath):
        nodes = tree.xpath(xpath)
        if len(nodes) == 0:
            return None
        else:
            return nodes[0]


    def get_node_text(self, tree, xpath=None):
        if xpath is None:
            text = tree.text
            if text is None:
                return ""
            return text.strip()

        nodes = tree.xpath(xpath)
        if (len(nodes) == 0):
            return None
        else:
            text = nodes[0].text
            if text is None:
                return ""
            return text.strip()


    def parse(self, id, html):
        self.id = id
        self.load(html)
