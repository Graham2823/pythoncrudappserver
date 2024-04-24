from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS from flask_cors module
from pymongo import MongoClient
import os
import ssl
import certifi
from bson import ObjectId  # Import ObjectId to handle MongoDB ObjectIDs

app = Flask(__name__)
CORS(app)  # Initialize CORS extension with your Flask app

mongoConnectionString = os.environ.get('MONGODB_CONNECTION_STRING')
print("mongo", mongoConnectionString)
client = MongoClient(mongoConnectionString, tlsCAFile=certifi.where())
db = client.PythonCrudApp
collection = db.Transfers

@app.route('/', methods=['GET'])
def index():
    return 'Welcome to the Python CRUD App!'

@app.route('/api/create', methods=['POST'])
def create_transfer():
    print("Route Hit")
    if request.method == 'POST':
        # Get request body as JSON
        data = request.json

        # Create a new Transfer instance using data from the request body
        new_transfer = {
            'name': data.get('playerName'),
            'position': data.get('playerPosition'),
            'old_team': data.get('prevSchool'),
            'new_team': data.get('newSchool')
        }

        # Insert the new transfer to MongoDB
        result = collection.insert_one(new_transfer)

        # Prepare response
        response_data = {'message': 'Data inserted successfully', 'inserted_id': str(result.inserted_id)}
        return jsonify(response_data), 200
    else:
        # Handle invalid requests
        return jsonify({'error': 'Method Not Allowed'}), 405

@app.route('/api/getTransfers', methods=['GET'])
def get_transfer():
    print("Get Route Hit")
    # Fetch transfers from MongoDB
    transfers = list(collection.find({}))

    # Convert ObjectId to string for JSON serialization
    for transfer in transfers:
        transfer['_id'] = str(transfer['_id'])

    return jsonify(transfers), 200

@app.route('/api/delete/<transfer_id>', methods=['DELETE'])
def delete_transfer(transfer_id):
    print("delete Route Hit")
    print("Transfer ID:", transfer_id)

    # Attempt to delete the transfer from the database
    result = collection.delete_one({'_id': ObjectId(transfer_id)})

    # Check if the transfer was successfully deleted
    if result.deleted_count == 1:
        # Prepare success response
        response_data = {'message': 'Transfer deleted successfully'}
        return jsonify(response_data), 200
    else:
        # Prepare error response if transfer not found
        return jsonify({'error': 'Transfer not found'}), 404

@app.route('/api/edit/<transfer_id>', methods=["PUT"])
def edit_transfer(transfer_id):
    print("edit route hit")
    transfer = collection.find_one({'_id': ObjectId(transfer_id)})
    if not transfer:
        return jsonify({'error:' 'Transfer not found'}), 404
    data = request.json
    transfer['name'] = data.get('name', transfer['name'])
    transfer['position'] = data.get('position', transfer['position'])
    transfer['old_team'] = data.get('old_team', transfer['old_team'])
    transfer['new_team'] = data.get('new_team', transfer['new_team'])
    collection.update_one({'_id': ObjectId(transfer_id)}, {"$set": transfer})
    return jsonify({'message': 'Transfer updated successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
