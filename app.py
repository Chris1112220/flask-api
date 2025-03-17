from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Connecting to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Topher1212@localhost/finance_tracker'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# Creating a table Class
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Transaction {self.name}>'


# Homepage route
@app.route('/')
def home():
    return jsonify({
        "developer": "Chris Roberts",
        "mission_statement": "The purpose of this project is to obtain a career change from Accounting to Software Backend Developer by demonstrating my knowledge in Computer Science and Robotic Process Automation."
    })


# going to /transctions page and creating a new transaction
@app.route('/transactions', methods=['POST'])
def create_transaction():
    data = request.get_json()
    new_transaction = Transaction(name=data['name'], amount=data['amount'])
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({"message": "Transaction added successfully!"}), 201


# Getting transactions from the database
@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    transactions_list = [{"id": t.id, "name": t.name,
                          "amount": t.amount, "date": t.date} for t in transactions]
    return jsonify(transactions_list)


# Reading single transaction
@app.route('/transactions/<int:id>', methods=['GET'])
def get_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        return jsonify({"id": transaction.id, "name": transaction.name, "amount": transaction.amount, "date": transaction.date})
    return jsonify({"message": "Transaction not found"}), 404


# Updating transactions
@app.route('/transactions/<int:id>', methods=['PUT'])
def update_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        data = request.get_json()
        transaction.name = data.get('name', transaction.name)
        transaction.amount = data.get('amount', transaction.amount)
        db.session.commit()
        return jsonify({"message": "Transaction updated successfully!"})
    return jsonify({"message": "Transaction not found"}), 404


# Deleting a transaction
@app.route('/transactions/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({"message": "Transaction deleted successfully!"})
    return jsonify({"message": "Transaction not found"}), 404


# running the flask app
if __name__ == '__main__':
    app.run(debug=True)
