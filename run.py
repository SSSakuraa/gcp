#! /root/papa/venv/bin/python
from gcp import app
app.run(host='0.0.0.0',port=5000,debug=True)
