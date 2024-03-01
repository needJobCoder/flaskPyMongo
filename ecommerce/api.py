from flask import Flask, request
from bson.objectid import ObjectId
import datetime
import json 
app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

from pymongo import MongoClient

collection_users = None
collection_orders = None


client = MongoClient("mongodb://localhost:27017/")
db = client["ecommerce"]
collection_users = db["users"]
collection_orders = db["orders"]


@app.route("/loginUser/", methods=["POST"])
def loginUser():
    if request.method == 'POST':
        try:
            username = request.json["username"]
            password = request.json["password"]
        except KeyError:
            
            return {"loginStatus": str(request), "reason": "KeyError"}

        user = collection_users.find_one({"username": username})
        if user != None:
            return {"loginStatus": "Success", "reason": "None"}
        else:
            return {"loginStatus": "Failed", "reason": "None"}

@app.route('/createUser/', methods=['POST'])
def createUser():
    if request.method == 'POST':
        try:
            username = request.json["username"]
            password = request.json["password"]
        except KeyError:
            return {"userCreationStatus": "Failed", "reason": "KeyError"}
        
    user = collection_users.find_one({"username": username})
    new_user = {"username": f"{username}", "password": f"{password}"}
    if user is None:
        collection_users.insert_one(new_user)
        return  {"userCreationStatus": f" {new_user } {user}", "reason": "None"}
    else:
        return  {"userCreationStatus": f"userAlreadyExists {new_user} {user}", "reason": "None"}
    
@app.route('/findUser/<string:id>/', methods=['POST'])
def findUser(id):
    # user_id = ObjectId(id)
    user = collection_users.find_one({"_id": ObjectId(f"{id}")})
    if user != None:
        print(user)
        return{"userFoundStatus": "Success", "user":{
            "id":f"{user['_id']}",
            "username":f"{user['username']}",
            "password":f"{user['password']}"
        }}
    elif user == None:
        return {"userFoundStatus": "Failed", "reason": "UserIsNone"}
    else:
        return {"userFoundStatus": "Failed", "reason": "SomethingUnkownHappened"}

@app.route('/createOrder/', methods=['POST'])
def createOrder():
    try:
        user_id = request.json['userId']
        quantity = request.json['quantity']
        product_name = request.json['productName']
    except KeyError:
        return {"orderStatus":"Failed","reason":"KeyError"}
    
    orders = collection_orders.find({"userId": user_id, "productName":product_name})
    orders = list(orders)
    for order in orders:
        print(order)
    
    print(len(list(orders)))
    
            
    
    if len((orders)) == 0:
        collection_orders.insert_one({"userId":user_id,"quantity":quantity, "productName":product_name, "date":datetime.datetime.now()})
        return {"orderStatus":"Success","reason":"orderUpdated", "orderCount":len(list(orders))}
    elif len((orders)) > 0:
        try:
            for order in orders:
                if order['productName'] == product_name:
                    id = order['_id']
                    obj_id = ObjectId(id)
                    query = {"_id": obj_id}
                    new_quantity = {"$set":{"quantity":quantity}}
                    collection_orders.update_one(query, new_quantity)
                    return {"orderStatus":"Success","reason":"orderQuantityReplaced"}
            
        except KeyError:
                return {"orderStatus":"Failed","reason":"KeyError"}
    
    return {"orderStatus":"Failed","reason":"somethingWentWrong", "orders": f"{orders}"}

@app.route('/getOrders/<string:userId>/', methods=['POST'])
def getAllOrders(userId):
    orders = collection_orders.find({"userId": userId})
    order_list = []
    for order in orders:
        try:
            order_id = order["_id"]
            user_id = order["userId"]
            product_name = order['productName']
            quantity = order['quantity']
        except  KeyError:
            return {"getOrdersStatus": "Failed", "reason":"KeyError"}
        
        order_dict = {"_id": f"{order_id}", "userId": user_id, "productName": product_name, "quantity": quantity}
        order_list.append(order_dict)
    
    
    return {"orders": order_list}
        