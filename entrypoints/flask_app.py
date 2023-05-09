from datetime import datetime

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
from adapters import orm
from domain import model
from service_layer import services, unit_of_work

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


@app.route("/")
def hello_world():
    return "Hello, World!", 200


@app.route("/add_batch", methods=['POST'])
def add_batch():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)
    eta = request.json['eta']
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    services.add_batch(
        request.json['ref'], request.json['sku'], request.json['qty'], eta,
        uow
    )
    return 'OK', 201


@app.route("/allocate", methods=['POST'])
def allocate_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)


    try:
        batchref = services.allocate(request.json['orderid'],
                                     request.json['sku'],
                                     request.json['qty'],
                                     uow)
    except (model.OutOfStock, services.InvalidSku) as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201


@app.route("/deallocate", methods=['POST'])
def deallocate_endpoint():
    uow = unit_of_work.SqlAlchemyUnitOfWork(get_session)

    try:
        batchref = services.deallocate(request.json['orderid'],
                                       request.json['sku'],
                                       request.json['qty'],
                                       uow)
    except model.NotAllocated as e:
        return jsonify({'message': str(e)}), 400

    return jsonify({'batchref': batchref}), 201
