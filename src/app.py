#!/usr/bin/env python
import logging
import json
import os
import mysql.connector
from datetime import datetime
import time

from flask import Flask, Response, url_for, redirect, request, jsonify
import flask

# because we have an API, we need to allow cross-origin here
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

app.config.from_envvar('PF1010_SYSCHANGE_SETTINGS')

# measurement times are always expected in this format
API_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'

def dbconn():
    return mysql.connector.connect(host=app.config['DATABASE_HOST'],
                                   user=app.config['DATABASE_USER'],
                                   password=app.config['DATABASE_PASSWORD'],
                                   database=app.config['DATABASE_NAME'])


def __quantity(quantity_type, amount_int, amount_decimal):
    if quantity_type == 'none':
        return 0
    elif quantity_type == 'integer':
        return amount_int
    else:
        return amount_decimal


@app.route('/api/v1.0.0/system_changes/<system_uid>/<key>', methods=['GET'])
def system_changes(system_uid, key):
    conn = dbconn()
    cursor = conn.cursor()
    try:
        cursor.execute('select c.time, c.amount_int, c.amount_decimal, qt.name, u.name from system_changes c join change_types ct on c.change_type_id=ct.id join quantity_types qt on qt.id=ct.quantity_type_id join units u on u.id=ct.unit_id where system_uid=%s and ct.name=%s',
                       [system_uid, key])
        result = [{'time': time.strftime(API_TIME_FORMAT),
                   'quantity': __quantity(quantity_type, amount_int, amount_decimal),
                   'unit': unit
        } for time, amount_int, amount_decimal, quantity_type, unit in cursor.fetchall()]
        return jsonify(change_type=key, changes=result)
    finally:
        cursor.close()
        conn.close()


@app.route('/api/v1.0.0/system_change/<system_uid>/<key>', methods=['PUT'])
def put_system_changes(system_uid, key):
    req_data = request.get_json()
    try:
        time_str = req_data['time']
        record_time = datetime.fromtimestamp(time.mktime(time.strptime(time_str, API_TIME_FORMAT)))
    except:
        return jsonify(status='error', info='invalid or missing date')
    conn = dbconn()
    cursor = conn.cursor()
    try:
        cursor.execute('select ct.id, ct.name, qt.name from change_types ct join quantity_types qt on ct.quantity_type_id=qt.id where ct.name=%s',
                       [key])
        row = cursor.fetchone()
        if row is None:
            return jsonify(status='error', info='change type does not exist')
        change_type_id, _, quantity_type = row
    finally:
        cursor.close()
        conn.close()

    # quantity check
    if quantity_type != 'none':
        try:
            quantity = req_data['quantity']
        except:
            return jsonify(status='error', info='missing quantity')

        if quantity_type == 'integer':
            if not isinstance(quantity, int):
                return jsonify(status='error', info='invalid quantity')
            quantity = int(quantity)
        else:
            if quantity is not None:
                try:
                    quantity = float(quantity)
                except:
                    return jsonify(status='error', info='invalid quantity')

    conn = dbconn()
    cursor = conn.cursor()
    try:
        if quantity_type == 'none':
            cursor.execute('insert into system_changes (system_uid,time,change_type_id) values (%s,%s,%s)',
                           [system_uid, record_time, change_type_id])
        elif quantity_type == 'integer':
            cursor.execute('insert into system_changes (system_uid,time,change_type_id,amount_int) values (%s,%s,%s,%s)',
                           [system_uid, record_time, change_type_id, quantity])
        else:
            cursor.execute('insert into system_changes (system_uid,time,change_type_id,amount_decimal) values (%s,%s,%s,%s)',
                           [system_uid, record_time, change_type_id, quantity])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
    return jsonify(status='ok')

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
