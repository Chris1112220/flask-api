from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.middleware.proxy_fix import ProxyFix
import os

app = Flask(__name__)

# Security Key (Uses environment variable for security)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'super-secret')
jwt = JWTManager(app)

# Connection to AWS Lambda (Commented out when running locally in Docker)
app.wsgi_app = ProxyFix(app.wsgi_app)

# AWS Lambda handler (Only needed when deploying with Zappa)
# Commented out when running locally with Docker
# def lambda_handler(event, context):
#     from zappa.handler import lambda_handler as lh
#     return lh(event, context)

# Connecting to database (Uses environment variable for Docker)
# Defaults to SQLite if not running in Docker
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 'sqlite:///default.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure database tables are created on startup
with app.app_context():
    db.create_all()

# Creating a table Class for Transactions


class Transaction(db.Model):
    # Unique ID for each transaction
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Name of the transaction
    # Amount involved in the transaction
    amount = db.Column(db.Float, nullable=False)
    # Auto-generated timestamp
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Transaction {self.name}>'


# Hardcoded user login data (To be replaced with database-based authentication later)
users = {
    "chris": "password"
}

# Login Route


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Validate username and password
    if username in users and users[username] == password:
        access_token = create_access_token(
            identity=username)  # Generate JWT token
        return jsonify({
            "message": "Login successful!",
            "access_token": access_token,
            "user": username
        }), 200

    return jsonify({"message": "Invalid login"}), 401

# Homepage route


@app.route('/')
def home():
    return jsonify({
        "developer": "Chris Roberts",
        "mission_statement": "The purpose of this project is to obtain a career change from Accounting to Software Backend Developer by demonstrating my knowledge in Computer Science and Robotic Process Automation."
    })

# Route to create a new transaction (Requires authentication)


@app.route('/transactions', methods=['POST'])
@jwt_required()
def create_transaction():
    data = request.get_json()
    new_transaction = Transaction(name=data['name'], amount=data['amount'])

    db.session.add(new_transaction)  # Add transaction to database
    db.session.commit()  # Commit changes

    return jsonify({"message": "Transaction added successfully!"}), 201

# Route to fetch all transactions from the database


@app.route('/transactions', methods=['GET'])
def get_transactions():
    # Retrieve all transactions from the database
    transactions = Transaction.query.all()

    # Convert transactions into a JSON-compatible format
    transactions_list = [{"id": t.id, "name": t.name,
                          "amount": t.amount, "date": t.date} for t in transactions]

    return jsonify(transactions_list)

# Route to fetch a single transaction using its ID


@app.route('/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    transaction = Transaction.query.get(id)

    if transaction:
        return jsonify({
            "id": transaction.id,
            "name": transaction.name,
            "amount": transaction.amount,
            "date": transaction.date
        })

    return jsonify({"message": "Transaction not found"}), 404

# Route to update an existing transaction (Requires authentication)


@app.route('/transactions/<int:id>', methods=['PUT'])
@jwt_required()
def update_transaction(id):
    transaction = Transaction.query.get(id)

    if transaction:
        data = request.get_json()
        # Update name if provided
        transaction.name = data.get('name', transaction.name)
        # Update amount if provided
        transaction.amount = data.get('amount', transaction.amount)

        db.session.commit()  # Save changes
        return jsonify({"message": "Transaction updated successfully!"})

    return jsonify({"message": "Transaction not found"}), 404

# Route to delete a transaction (Requires authentication)


@app.route('/transactions/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_transaction(id):
    transaction = Transaction.query.get(id)

    if transaction:
        db.session.delete(transaction)  # Remove transaction from database
        db.session.commit()  # Save changes
        return jsonify({"message": "Transaction deleted successfully!"})

    return jsonify({"message": "Transaction not found"}), 404


# Running the Flask app inside Docker (Use 0.0.0.0 to make it accessible)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
