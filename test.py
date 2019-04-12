import pymongo
import pandas as pd

conn = pymongo.MongoClient('localhost', 27017)
db = conn.date  # 连接mydb数据库，没有则自动创建
total_db = db.total_db  # 存储全部数据
hangzhou_db = db.hangzhou_db  # 存储包含杭州的数据
# for i in hangzhou_db.find({}, {'name': 1, 'text': 1, '_id': 0}):
#     print(i)
x = list(hangzhou_db.find({}, {'name': 1, 'text': 1, '_id': 0}))

df = pd.DataFrame(x)

print(df)
