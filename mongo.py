import pymongo

db_client = pymongo.MongoClient("mongodb://localhost:27017")
db = db_client["gb_data_mining_16_02_2021"]
collection = db["magnit"]
# {"title": {"$regex": "Таблетки"}}
# for itm in collection.find(
#     {
#         "$or": [
#             {"promo_name": "Скидка", "title": {"$regex": "Таблетки"}},
#             {"title": {"$regex": "Пиво"}},
#         ]
#     }
# ):
print(list(collection.find()))