from flask import Flask, request, jsonify, render_template, redirect
from flask_cors import CORS
import random
from collections import deque

app = Flask(__name__)
CORS(app)

# База данных в памяти
users_db = {}

class User:
    def __init__(self, user_id):
        self.user_id = user_id
        self.balance = 1000
        self.history = deque(maxlen=10)
        self.current_bet = 0
        self.auto_cashout = 2.0

# Главная страница и /aviator
@app.route('/')
@app.route('/aviator')  # Добавлен обработчик для /aviator
def aviator():
    return render_template('aviator.html')

# API-эндпоинты
@app.route('/api/init', methods=['POST'])
def api_init():
    data = request.get_json()
    user_id = str(data['user']['id'])

    if user_id not in users_db:
        users_db[user_id] = User(user_id)

    user = users_db[user_id]
    return jsonify({
        'balance': user.balance,
        'history': list(user.history),
        'auto_cashout': user.auto_cashout
    })

@app.route('/api/bet', methods=['POST'])
def api_bet():
    data = request.get_json()
    user_id = str(data['user']['id'])
    bet_amount = int(data['bet_amount'])

    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404

    user = users_db[user_id]

    if user.balance < bet_amount:
        return jsonify({'error': 'Not enough balance'}), 400

    user.balance -= bet_amount
    user.current_bet = bet_amount
    crash_point = round(random.uniform(1.1, 10.0), 2)

    return jsonify({
        'balance': user.balance,
        'crash_point': crash_point
    })

@app.route('/api/cashout', methods=['POST'])
def api_cashout():
    data = request.get_json()
    user_id = str(data['user']['id'])
    multiplier = float(data['multiplier'])

    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404

    user = users_db[user_id]
    win_amount = int(user.current_bet * multiplier)
    user.balance += win_amount
    user.history.appendleft({
        'multiplier': multiplier,
        'win': True,
        'amount': win_amount
    })
    user.current_bet = 0

    return jsonify({
        'balance': user.balance,
        'history': list(user.history)
    })

@app.route('/api/set_auto', methods=['POST'])
def api_set_auto():
    data = request.get_json()
    user_id = str(data['user']['id'])
    auto_cashout = float(data['auto_cashout'])

    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404

    user = users_db[user_id]
    user.auto_cashout = auto_cashout
    return jsonify({'auto_cashout': user.auto_cashout})

if __name__ == '__main__':
    app.run()
