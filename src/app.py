#!/usr/bin/env python
import logging
import json
import os

from flask import Flask, Response, url_for, redirect, request, jsonify
import flask

# because we have an API, we need to allow cross-origin here
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

app.config.from_envvar('PF1010_SYSCHANGE_SETTINGS')


@app.route('/api/v1.0.0/info')
def api_info():
    return jsonify(name="pf1010-syschange", version="1.0.0")


if __name__ == '__main__':
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    app.debug = True
    app.secret_key = 'trtenradhipgrpdnstdntsodetsnrdeoistd'
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True)
