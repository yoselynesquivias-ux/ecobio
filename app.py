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

# -------- LOGIN --------
@app.route('/')
def login():
    return render_template('login.html')

# -------- REGISTRO --------
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
                "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
                (nombre, correo, password)
            )
            conn.commit()
            flash('Registro exitoso, ahora puedes iniciar sesión')
            return redirect(url_for('login'))
        except:
            flash('Ese correo ya está registrado')
        finally:
            conn.close()

    return render_template('registro.html')

# -------- ACCEDER --------
@app.route('/acceder', methods=['POST'])
def acceder():
    correo = request.form['correo']
    password = request.form['password']

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM usuarios WHERE correo=? AND password=?",
        (correo, password)
    )
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return redirect(url_for('reciclaje'))
    else:
        flash('Datos incorrectos')
        return redirect(url_for('login'))

# -------- PÁGINA PRINCIPAL --------
@app.route('/reciclaje')
def reciclaje():
    return render_template('reciclaje.html')

# -------- MOSTRAR / BUSCAR USUARIOS --------
@app.route('/usuarios')
def usuarios():
    buscar = request.args.get('buscar', '')

    conn = get_db()
    cursor = conn.cursor()

    if buscar:
        cursor.execute(
            "SELECT id, nombre, correo FROM usuarios WHERE correo LIKE ?",
            ('%' + buscar + '%',)
        )
    else:
        cursor.execute("SELECT id, nombre, correo FROM usuarios")

    usuarios = cursor.fetchall()
    conn.close()

    return render_template('usuarios.html', usuarios=usuarios, buscar=buscar)

# -------- VERIFICAR CONTRASEÑA --------
@app.route('/verificar/<accion>/<int:id>', methods=['GET', 'POST'])
def verificar(accion, id):
    if request.method == 'POST':
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE id=? AND password=?",
            (id, password)
        )
        usuario = cursor.fetchone()
        conn.close()

        if usuario:
            if accion == 'editar':
                return redirect(url_for('editar', id=id))
            elif accion == 'eliminar':
                return redirect(url_for('eliminar', id=id))
        else:
            flash('Contraseña incorrecta')

    return render_template('verificar.html', accion=accion)

# -------- ELIMINAR --------
@app.route('/eliminar/<int:id>')
def eliminar(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('usuarios'))

# -------- EDITAR --------
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    conn = get_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']

        if password:
            cursor.execute(
                "UPDATE usuarios SET nombre=?, correo=?, password=? WHERE id=?",
                (nombre, correo, password, id)
            )
        else:
            cursor.execute(
                "UPDATE usuarios SET nombre=?, correo=? WHERE id=?",
                (nombre, correo, id)
            )

        conn.commit()
        conn.close()
        return redirect(url_for('usuarios'))

    cursor.execute("SELECT nombre, correo FROM usuarios WHERE id=?", (id,))
    usuario = cursor.fetchone()
    conn.close()

    return render_template('editar.html', usuario=usuario)

# -------- RUN --------
if __name__ == '__main__':
    app.run(debug=True)

