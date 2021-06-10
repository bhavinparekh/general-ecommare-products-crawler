import pymongo
from scrapy.default import MONGODB_PORT, SCRAPE_DATABASE


def db_driver():
    client = pymongo.MongoClient("mongodb", int(MONGODB_PORT), connect=False)
    db = client[SCRAPE_DATABASE]
    return db

def get_spit_url(url):
    split_url = url.split('/')
    return split_url[2]


def get_qs(product):
    db = db_driver()
    try:
        get_qs = db[get_spit_url(product['url'])].find_one({"url": product['url']})
        return get_qs
    except:
        return None


def update_data(product):
    db = db_driver()
    if get_qs(product) is not None:
        db[get_spit_url(product['url'])].update_one({"url": product['url']}, {
            "$set": {"title": product['title'], "categories": product['categories'], "price": product['price'],
                     "currency": product['currency'], "images": product['images'],
                     "description": product['description'], "extra": product['extra']}})
    else:
        db[get_spit_url(product['url'])].insert_one(product)
    return True

def status_compelete(url):
    db = db_driver()

    try:
        id = db[get_spit_url(url)].find().sort("_id",-1).limit(1)[0]['_id']
        print("the Id is", id)
    except Exception as id_er:
        print(id_er)
    try:
        db[get_spit_url(url)].update_one({"_id": id}, {"$set":{"status":"Complete"}})
        print("the task is done")
    except Exception as er_d:
        print(er_d)


def set_status_flag(url):
    db = db_driver()
    collection_name = get_spit_url(url)+"status"
    if get_qs(collection_name) is not None:
        db[collection_name].update_one({"status": "complete"})
    else:
        db[collection_name].insert_one({"status":"complete"})
    return True

def create_status_flag(url, message):
    db = db_driver()
    collection_name = get_spit_url(url) + "status"
    if message == "complete":
        db[collection_name].update({"status": "in-progress"}, {"status":"complete"})
    else:
        db[collection_name].insert({"status":message})

    return True


def remove_status_flag(url):
    db = db_driver()
    collection_name = get_spit_url(url) + "status"
    try:
        db.drop_collection(collection_name)
    except Exception as drop_er:
       print("error ", drop_er)
    return True

def get_status_flag(url):
    db = db_driver()

    collection_name = url + "status"
    status = db[collection_name].find()[0]["status"]
    return status


'''
if get_qs and product["url"] == href:
    print(True)
    try:
        db[split_url[2]].update_one({"url": href}, {"$set": {"product": product}})
        return True
    except Exception as erXdbinsert:
        print("Data reinsertion error")
        return False
else:
    if product and (get_qs is None) and (get_spit_url(product['url']) == get_spit_url(url)):
        try:
            #db[split_url[2]].insert_one({"url": product['url'], "product": product})
            db[get_spit_url(product['url'])].insert_one({"url":product['url'], "product": product})
            return True
        except Exception as erx05601:
            "new product insert error"
            return False
'''
