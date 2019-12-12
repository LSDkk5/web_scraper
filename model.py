import motorengine
from motorengine.document import Document

db = motorengine.connection.connect(host='localhost', port=27017, db='app')

class Product(Document):
    pass