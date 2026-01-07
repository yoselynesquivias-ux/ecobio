from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'ecobio123'

# -------- BASE DE DATOS --------
def get_db():
    conn = sqlite3.connect('ecobio.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------- RUTAS --------
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute(
                'INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)',
                (nombre, correo, password)
            )
            conn.commit()
            flash('Registro exitoso, ahora puedes iniciar sesión 💚')
            return redirect(url_for('login'))
        except:
            flash('Ese correo ya está registrado ❌')
        finally:
            conn.close()

    return render_template('registro.html')

@app.route('/acceder', methods=['POST'])
def acceder():
    correo = request.form['correo']
    password = request.form['password']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM usuarios WHERE correo=? AND password=?',
        (correo, password)
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return redirect(url_for('reciclaje'))
    else:
        flash('Datos incorrectos ❌')
        return redirect(url_for('login'))

@app.route('/reciclaje')
def reciclaje():
    return render_template('reciclaje.html')

if __name__ == '__main__':
    app.run(debug=True)