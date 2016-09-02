from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from datetime import datetime

# # post = MongoClient().blog.User.find_one({'username': 'guest'})
# # followers = []
# # follower = ['57b2eb993632db35b16298ea', datetime.utcnow()]
# # followers.append(follower)
# # follower = ['57b2eb9932db35b16298ess', datetime.utcnow()]
# # followers.append(follower)
# # MongoClient().blog.User.update({'username': 'guest'}, {'$set': {'followers': followers}})
# # for follower in followers:
# #     post = MongoClient().blog.User.find_one({'_id': ObjectId(follower)})
# #     print(post)
# #
#
# item=[]
# MongoClient().blog.User.update({'username': 'INnoVation'}, {'$set': {'followers': item}})
# MongoClient().blog.User.update({'username': 'INnoVation'}, {'$set': {'following': item}})
#
#
#
# # # very = False
# # # for i in range(s.__len__()):
# # #     if s[i][0] == '57b2eb993632db35b1629s8ea':
# # #         s.remove(s[i])
# # #         very = True
# # #         break
# # item=[]
# # for i in range(s.__len__()):
# #     item.append({'user': s[i][0], 'timestamp': s[i][1]})
# # for ite in item:
# #     print(type(ite))
# # print(item)
# class PaginateFollowers:
#     def __init__(self, page, username):
#         conn = MongoClient().blog.User.find_one({'username': username})
#         posts = conn.get('followers')
#         self.total = posts.__len__()
#         self.pages = int(self.total / 20)
#         if self.total % 20 != 0:
#             self.pages += 1
#         if page == 1:
#             self.has_prev = False
#         else:
#             self.has_prev = True
#         if page == self.pages:
#             self.has_next = False
#         else:
#             self.has_next = True
#         self.next_num = page + 1
#         self.page = page
#         self.per_page = 20
#         self.prev_num = page - 1
#         self.current_num = self.total - (20 * (page - 1))
#         if self.current_num > 20:
#             self.current_num = 20
#         self.item = []
#         for i in range(self.current_num):
#             self.item.append({'user': post[self.prev_num * 20 + i][0], 'timestamp': post[self.prev_num * 20 + i][1]})
# posts=[]
# following = MongoClient().blog.User.find_one({'username': 'guest'}).get('following')
# artical = MongoClient().blog.Aritical.find()
# following.append(['guest', ''])
# for i in range(following.__len__()):
#     for x in range(artical.count()):
#         if following[i][0] == artical[i].get('username'):
#             posts.append(artical[i])
# print('sss')
s=MongoClient().blog.Aritical.find({'_id': ObjectId('57b445c13632db2df382f1c9')})
s=s[0].get('username')
print(s)
