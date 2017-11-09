class FeatureType(object):

    def __init__(self, name):
        self.__name__ = name
        self.__title = ""
        self.__abstract = ""
        self.__namespace = ""
        self.__namespace_prefix = ""
        self.__metadata_url = ""

        self.__wgs84bbox_east = 0
        self.__wgs84bbox_south = 0
        self.__wgs84bbox_west = 0
        self.__wgs84bbox_north = 0

    def getName(self):
        return self.__name__

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title

    def getAbstract(self):
        return self.__abstract

    def setAbstract(self, abstract):
        self.__abstract = abstract

    def getNamespace(self):
        return self.__namespace.encode('utf8')

    def setNamespace(self, namespace):
        self.__namespace = namespace.decode('utf8')

    def getNamespacePrefix(self):
        return self.__namespace_prefix

    def setNamespacePrefix(self, namespace_prefix):
        self.__namespace_prefix = namespace_prefix

    def getMetadataUrl(self):
        return self.__metadata_url

    def setMetadataUrl(self, metadata_url):
        self.__metadata_url = metadata_url


    def getWgs84BoundingBoxEast(self):        
        return self.__wgs84bbox_east

    def setWgs84BoundingBoxEast(self, east):
        self.__wgs84bbox_east = east

    def getWgs84BoundingBoxSouth(self):        
        return self.__wgs84bbox_south

    def setWgs84BoundingBoxSouth(self, south):
        self.__wgs84bbox_south = south

    def getWgs84BoundingBoxWest(self):        
        return self.__wgs84bbox_west

    def setWgs84BoundingBoxWest(self, west):
        self.__wgs84bbox_west = west

    def getWgs84BoundingBoxNorth(self):        
        return self.__wgs84bbox_north

    def setWgs84BoundingBoxNorth(self, north):
        self.__wgs84bbox_north = north