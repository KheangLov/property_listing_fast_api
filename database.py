from pony.orm import Database

db = Database()
db.bind(provider='postgres', user='macbook', password='', host='127.0.0.1', database='p_listing')
