import logging
from flask import Flask, jsonify


_logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route('/')
def welcome():
    return 'Welcome to Simulation Rest Service'


@app.route('/getData')
def get_test_data():
    test_dict = {
        'simulation': {'sim_id': 12, 'sim_turn': 2},
        'meta': {'1': 'Fish', '2': 'Shark', 'data': ('type', 'x', 'y')},
        'grid': [
            (1, 1, 1),
            (1, 2, 1),
            (1, 3, 1),
            (1, 1, 3),
            (1, 3, 2),
            (2, 2, 2)
        ]
    }
    return jsonify(test_dict)

@app.route('/test')
def test():
    msg = {'blah': 1,
           're-blah': {'blah': ('tuple', 4)}}
    return jsonify(msg)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
