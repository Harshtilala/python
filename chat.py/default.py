from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host='192.168.78.25', debug=True) # Or host='0.0.0.0'
#http://127.0.0.1:5000/chat_dashboard