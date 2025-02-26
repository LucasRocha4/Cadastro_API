from flask import Flask, request, jsonify
import sqlite3
import hashlib

app = Flask(__name__)

# Caminho do banco de dados
DB_PATH = 'users_database.db'


# Classe para gerenciar o banco de dados
class Register:
    def __init__(self):
        self.db_path = DB_PATH
        self.ensure_table_exists()

    def get_db_connection(self):
        return sqlite3.connect(self.db_path)

    def ensure_table_exists(self):
        """Cria a tabela se não existir"""
        connection = self.get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );
        ''')
        connection.commit()
        connection.close()

    def login(self, email, password):
        """Verifica se o email e a senha existem no banco de dados"""
        connection = self.get_db_connection()
        cursor = connection.cursor()
        password = hashlib.sha1(password.encode()).hexdigest()

        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            return {'message': f'Hello, {user[1]}!'}
        else:
            return {'error': 'Invalid user'}


# Criando a instância da classe Register
instance = Register()


@app.route('/', methods=['GET'])
def ping():
    return 'pong', 200


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if len(data['password']) < 6 or len(data['password']) > 39:
        return jsonify({"error": "Password must be between 6 and 39 characters"}), 400

    if not data or 'name' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "name, email and password are required"}), 400

    name = data['name']
    email = data['email']
    password = hashlib.sha1(data['password'].encode()).hexdigest()

    try:
        connection = instance.get_db_connection()
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO users (name, email, password)
            VALUES (?, ?, ?)
        ''', (name, email, password))
        connection.commit()
        connection.close()

        return jsonify({"message": "User registered successfully!"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 400
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    result = instance.login(data['email'], data['password'])
    return jsonify(result)


# Rodando a aplicação Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
