from pony.orm import *
from datetime import datetime, date
from decimal import Decimal


class Model:
    db = Database()
    db.bind(provider='postgres', user='macbook', password='', host='127.0.0.1', database='p_listing')

    def __init__(self):
        pass

    class User(db.Entity):
        _table_ = "users"
        id = PrimaryKey(int, auto=True)
        first_name = Optional(str)
        last_name = Optional(str)
        email = Required(str, unique=True)
        phone = Required(str)
        password = Required(str)
        disabled = Optional(bool, default=0)
        profile = Optional(str)
        created_at = Required(datetime, default=lambda: datetime.now())
        updated_at = Required(datetime, default=lambda: datetime.now())
        property = Set('Property')

    class Property(db.Entity):
        _table_ = "properties"
        id = PrimaryKey(int, auto=True)
        sale_list_price = Optional(Decimal)
        rent_list_price = Optional(Decimal)
        street_no = Optional(str)
        house_no = Optional(str)
        address = Required(str)
        full_address = Optional(str)
        latitude = Required(str)
        longitude = Required(str)
        land_width = Required(Decimal)
        land_length = Required(Decimal)
        land_area = Required(Decimal)
        description = Optional(str)
        created_at = Required(datetime, default=lambda: datetime.now())
        updated_at = Required(datetime, default=lambda: datetime.now())
        deleted_at = Optional(datetime)
        image = Optional(str)
        gallery = Optional(str)
        is_rent = Optional(bool, default='f')
        is_sale = Optional(bool, default='f')
        status = Optional(str)
        created_by = Optional(int)
        updated_by = Optional(int)
        reason = Optional(str)
        user = Required('User', column='user_id')
        listing = Set('Listing')

    class Listing(db.Entity):
        _table_ = "listings"
        id = PrimaryKey(int, auto=True)
        property = Required('Property', column='property_id')
        created_by = Optional(int)
        updated_by = Optional(int)
        status = Optional(str)
        close_reason = Optional(str)
        created_at = Optional(datetime, default=lambda: datetime.now())
        updated_at = Optional(datetime, default=lambda: datetime.now())
        deleted_at = Optional(datetime)
        approved_at = Optional(datetime)
        approved_by = Optional(int)
        sale_price = Optional(float)
        rent_price = Optional(float)
        image = Optional(str)

    class KhAddress(db.Entity):
        _table_ = "kh_address"
        type_kh = Optional(str)
        type_en = Optional(str)
        code = Optional(str)
        name_kh = Optional(str)
        name_en = Optional(str)
        path_kh = Optional(str)
        path_en = Optional(str)
        center = Optional(str)
        boundary = Optional(str)

    db.generate_mapping()
