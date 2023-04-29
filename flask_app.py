from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import db_tables
import model
import repository

db_tables.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!", 200


@app.route("/allocate", methods=['GET', 'POST'])
def allocate_endpoint():
    session = get_session()
    line = model.OrderLine(
        request.json['orderid'],
        request.json['sku'],
        request.json['qty'],
    )
    batches = repository.SqlAlchemyRepository(session).list()
    batchref = model.allocate(line, batches)
    session.commit()
    return jsonify({'batchref': batchref}), 201
