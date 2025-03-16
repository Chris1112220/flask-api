from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return 'Hello my name is Chris Roberts and the purpose of this project is for me to obtain a career change from Accounting to Software backend developer by demonstrating my knowledge in Computer Science and Robot Process Integeration.'


if __name__ == '__main__':
    app.run(debug=True)
