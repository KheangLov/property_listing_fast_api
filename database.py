from pony.orm import Database

db = Database()
db.bind(provider='postgres', user='okteto', password='okteto', host='postgresql', database='okteto')
