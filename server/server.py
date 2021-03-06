####GLOBALS####


from bson.errors import InvalidId
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, json, abort
from flask_pymongo import PyMongo

import utilities

DEBUG = True

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'tabberdb'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/tabberdb'

mongo = PyMongo(app)

""" DATA MODEL
	Collections: users, folders, conversations
	User: {"_id": ObjectId("..."), "email": "...", "password": "...", "root": ObjectId("...")}
	Folder: {"_id": ObjectId("..."), "name": "...", "children": "...", "conversations": [ObjectId("..."), ...], "user_id": ObjectId("...")}
	Conversation: {"_id": ObjectId("..."), "name": "...", "messages": [{"author": "...", "content": ["...", ...]}, ...]}
"""


# ROUTING


# Default response; return an empty string
@app.route("/")
def main():
	return 404


# Initializes and populates a new user's documents; also checks for valid email
@app.route("/tabber/api/new_user", methods=["POST"])
def new_user():
	# Request: {"email": "...", "password": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "new_user(): request.json does not exist or does not contain 'email'")

	return jsonify({"registered": utilities.add_user(mongo, request.json)})


# Checks for valid login credentials
@app.route("/tabber/api/check_user", methods=["POST"])
def check_user():
	# Request: {"email": "...", "password": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "check_user(): request.json does not exist or does not contain 'email'")

	return jsonify({"logged_in": utilities.check_user(mongo, request.json)})


# Creates new conversation in specified folder
@app.route("/tabber/api/add_conversation", methods=["POST"])
def add_conversation():
	# Request: {"email", "...", "path": "path/from/root/convo_name", "messages": [{"author": "...", "message": "..."}, ...]}
	if not request.json or not "email" in request.json:
		return abort(400, "add_conversation(): request.json does not exist or does not contain 'email'")

	return jsonify({"convo_id": utilities.add_conversation(mongo, request.json)})


# Creates new folder given a parent directory
@app.route("/tabber/api/add_folder", methods=["POST"])
def add_folder():
	# Request: {"email": "...", "path": "path/from/root/folder_name"}
	if not request.json or not "email" in request.json:
		abort(400, "add_folder(): request.json does not exist or does not contain 'email'")

	return jsonify({"folder_id": utilities.add_folder(mongo, request.json)})


# Returns user's folder names
@app.route("/tabber/api/get_folders", methods=["POST"])
def get_folders():
	# Request: {"email": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "get_folders(): request.json does not exist or does not contain 'email'")

	return jsonify({"folders": utilities.get_folders(mongo, request.json)})


# Returns all of a user's conversations in a nester structure of folders
@app.route("/tabber/api/get_conversations", methods=["POST"])
def get_conversations():
	# Request: {"email": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "get_conversations(): request.json does not exist or does not contain 'email'")

	return jsonify({"folders": utilities.get_all_content(mongo, request.json)})


# Renames the specified folder
@app.route("/tabber/api/rename_folder", methods=["POST"])
def rename_folder():
	# Request: {"email": "...", "path": "path/from/root/folder_name", "newName": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "rename_folder(): request.json does not exist or does not contain 'email'")

	return jsonify({"status": utilities.rename_folder(mongo, request.json)})


# Renames the specified folder
@app.route("/tabber/api/rename_conversation", methods=["POST"])
def rename_conversation():
	# Request: {"email": "...", "path": "path/from/root/folder_name", "newName": "..."}
	if not request.json or not "email" in request.json:
		abort(400, "rename_conversation(): request.json does not exist or does not contain 'email'")

	return jsonify({"status": utilities.rename_conversation(mongo, request.json)})


# Returns all database contents; for local testing only
@app.route("/tabber/api/get_database", methods=["GET"])
def get_database():
	users, folders, conversations = utilities.get_database(mongo)
	return jsonify({"users": users, "folders": folders, "conversations": conversations})


# Deletes the specified folder
@app.route("/tabber/api/delete_folder", methods=["POST"])
def delete_folder():
	# Request: {"email": "...", "path": "path/from/root/folder_name"}
	if not request.json or not "email" in request.json:
		abort(400, "delete_folder(): request.json does not exist or does not contain 'email")

	return jsonify({"status": utilities.delete_folder(mongo, request.json)})


# Deletes the specified conversation
@app.route("/tabber/api/delete_conversation", methods=["POST"])
def delete_conversation():
	# Request: {"email": "...", "path": "path/from/root/conversation_name"}
	if not request.json or not "email" in request.json:
		abort(400, "delete_conversation(): request.json does not exist or does not contain 'email")

	return jsonify({"status": utilities.delete_conversation(mongo, request.json)})



# ERROR HANDLING


def error_print(status_code, error):
	if DEBUG:
		print("------------")
		print("ERROR (" + str(status_code) + "): " + error)
		print("------------")

@app.errorhandler(400)
def bad_request(error):
	error_print(400, error.description)
	return "Bad Request", 400

@app.errorhandler(401)
def bad_request(error):
	error_print(401, error.description)
	return "Unauthorized", 401

@app.errorhandler(500)
def internal_error(error):
	error_print(500, error.description)
	return "Internal Error", 500

if __name__ == "__main__":
	app.run(debug=True)
