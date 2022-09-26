import json

import time
from datetime import datetime
from pytz import timezone
from utils import generate_user_id, time_now

def user_model(name, email, id):
    return {
        "name":name,
        "email":email,
        "user_id":id,

        "number_of_items":0,

        "number_sold":0,
        "time_created":str(time_now()),
        "num_visits":0,

        "heart":0,

        "follower":[],
        "following":[],
        "saved_items":[]
    }

def items_model(category, seller_email, name, item_name, description, quality, price, exchange_item, negotiable, id, image_url):
    return {
        "id":id,

        "seller_email":seller_email,
        "seller_name":name,
        "item_name":item_name,
        "item_description":description,
        "item_quality":quality,
        "item_price":price,
        "item_exchange":exchange_item,
        "negotiable":False,
        "item_category":category,

        "time_created":str(time_now()),
        "time_sold":"",
        "sold":False,
        "image_url":image_url
    }