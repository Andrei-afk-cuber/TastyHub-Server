class User(object):
    def __init__(self, username, password, admin=False, authorized=False, id=0):
        self.__id = id
        self.__username = username
        self.__password = password
        self.__admin = admin
        self.__authorized = authorized

    def getId(self):
        return self.__id

    def getUsername(self):
        return self.__username

    def getPassword(self):
        return self.__password

    def isAdmin(self):
        return self.__admin

    def isAuthorized(self):
        return self.__authorized

    def setUsername(self, login):
        self.__username = login

    def setPassword(self, password):
        self.__password = password

    def setAdmin(self, admin):
        self.__admin = admin

    def activateAccount(self):
        self.__authorized = True

    def deactivateAccount(self):
        self.__authorized = False

class Recipe(object):
    def __init__(self, author, name, description, picture_path, cooking_time = 0, product_list=[], confirmed=False, id=0):
        self.__id = id
        self.__name = name
        self.__description = description
        self.__cooking_time = cooking_time
        self.__product_list = product_list
        self.__confirmed = confirmed
        self.__picture_path = picture_path
        self.__author = author

    def getId(self):
        return self.__id

    def getAuthor(self):
        return self.__author

    def getName(self):
        return self.__name

    def getDescription(self):
        return self.__description

    def getCookingTime(self):
        return self.__cooking_time

    def getProductList(self):
        return self.__product_list

    def getPicturePath(self):
        return self.__picture_path

    def getConfirmed(self):
        return self.__confirmed

    def setName(self, name):
        self.__name = name

    def setAuthor(self, author):
        self.__author = author

    def setDescription(self, description):
        self.__description = description

    def setCookingTime(self, cooking_time):
        self.__cooking_time = cooking_time

    def setProductList(self, product_list):
        self.__product_list = product_list

    def setConfirmed(self, confirmed=True):
        self.__confirmed = confirmed

    def setPiсturePath(self, picture_path):
        self.__picture_path = picture_path

    def to_dict(self):
        return {
            "id": self.__id,
            "author": self.__author,
            "name": self.__name,
            "description": self.__description,
            "cooking_time": self.__cooking_time,
            "product_list": self.__product_list,
            "confirmed": self.__confirmed,
            "picture_path": self.__picture_path,
        }