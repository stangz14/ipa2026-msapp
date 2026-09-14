import os
from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI")
db_name = os.environ.get("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
collection = db["routers"]
interface_status_collection = db["interface_status"]


@app.route("/")
def main():
    data = []
    for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return render_template("index.html", data=data)


@app.route("/interface-status")
def interface_status():
    selected_router = request.args.get("router", "").strip()
    query = {"router_ip": selected_router} if selected_router else {}
    routers = collection.find({}, {"ip": 1, "_id": 0}).sort("ip", 1)
    statuses = []
    for document in interface_status_collection.find(
            query).sort("timestamp", -1).limit(3):
        statuses.append({
            "router_ip": document.get("router_ip", "Unknown"),
            "timestamp": document.get("timestamp"),
            "interfaces": document.get("interfaces", []),
        })
    return render_template(
        "interface_status.html",
        statuses=statuses,
        routers=routers,
        selected_router=selected_router,
    )


@app.route("/add", methods=["POST"])
def add_comment():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")
    if ip and username and password:
        collection.insert_one(
            {"ip": ip, "username": username, "password": password})
    return redirect(url_for("main"))


@app.route("/delete/<document_id>", methods=["POST"])
def delete_comment(document_id):
    try:
        result = collection.delete_one({
            "_id": ObjectId(document_id)
        })

        print("document_id:", document_id)
        print("deleted_count:", result.deleted_count)

    except (InvalidId, TypeError) as error:
        print("Delete error:", error)

    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
