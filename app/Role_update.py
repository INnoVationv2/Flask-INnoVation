from pymongo import MongoClient


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role:
    db = MongoClient().blog.Role

    def __init__(self, name, permission, default):
        self.name = name
        self.permission = permission
        self.default = default

    def new_role(self):
        collection = {
            'name': self.name,
            'permissions': self.permission,
            'default': self.default
        }
        self.db.insert(collection)


def insert_role():
    roles = {
        'User': (Permission.FOLLOW |
                 Permission.COMMENT |
                 Permission.WRITE_ARTICLES, True),
        'Moderator': (Permission.FOLLOW |
                      Permission.COMMENT |
                      Permission.WRITE_ARTICLES |
                      Permission.MODERATE_COMMENTS, False),
        'Administrator': (0xff, False)
    }
    connect = MongoClient().blog.Role
    for i in roles:
        role = connect.find_one({'name': i})
        if role is None:
            Role(name=i, permission=roles[i][0], default=roles[i][1]).new_role()
        connect.update({'name': i}, {'$set': {'permissions': roles[i][0]}})
        connect.update({'name': i}, {'$set': {'default': roles[i][1]}})


insert_role()
