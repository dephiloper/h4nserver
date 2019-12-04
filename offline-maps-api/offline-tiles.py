#!/usr/bin/python3
from flask import Flask
from flask import send_file
app = Flask(__name__, static_folder='databases')

@app.route('/filesize/<westlimit>')
def getFilesize():
	return "300";

#@app.route('/download', methods=['GET'])
#def downloadFile ():
#    path = "/Examples.pdf"
#    return send_from_directory(directory='databases', filename='test.txt')

if __name__ == '__main__':
    app.run(port=5000,debug=True) 
