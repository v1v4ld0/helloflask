import sqlite3
from flask import Flask, request, jsonify, g
from Globals import DATABASE_NAME


app = Flask(__name__)

# Faz a conexão com o banco proposta na documentação do SQLite3 
def get_db_connection():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_NAME)
    return db

# Fecha a conexão de acordo com a documentação do SQLite3
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    cur = get_db_connection().cursor()
    return (jsonify({"versao": 1}), 200)


def getUsuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    resultset = cursor.execute('SELECT * FROM tb_usuario').fetchall()
    usuarios = []
    for linha in resultset:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
        usuarios.append(usuarioDict)
    conn.close()
    return usuarios


def setUsuario(data):
    nome = data.get('nome')
    nascimento = data.get('nascimento')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO tb_usuario(nome, nascimento) VALUES (?, ?)', (nome, nascimento))
    conn.commit()
    id = cursor.lastrowid
    data['id'] = id
    conn.close()
    return data


@app.route("/usuarios", methods=['GET', 'POST'])
def usuarios():
    if request.method == 'GET':
        # Listagem dos usuários
        usuarios = getUsuarios()
        return jsonify(usuarios), 200
    elif request.method == 'POST':
        # Recuperar dados da requisição: json.
        data = request.json
        data = setUsuario(data)
        return jsonify(data), 201


def getUsuarioById(id):
    usuarioDict = None
    conn = get_db_connection()
    cursor = conn.cursor()
    linha = cursor.execute(
        'SELECT * FROM tb_usuario WHERE id = ?'
        , (id,)).fetchone()
    if linha is not None:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
    conn.close()
    return usuarioDict


def updateUsuario(id, data):
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')

    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tb_usuario SET nome = ?, nascimento = ? WHERE id = ?', (nome, nascimento, id))
    conn.commit()

    rowupdate = cursor.rowcount

    conn.close()
    # Retornar a quantidade de linhas.
    return rowupdate


# Função criada para deletar um usuário pelo ID
def deleteUsuario(id):

    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'DELETE FROM tb_usuario WHERE id = ?', (id,))
    conn.commit()

    rowdelete = cursor.rowcount

    conn.close()
    # Retornar a quantidade de linhas.
    return rowdelete


@app.route("/usuarios/<int:id>", methods=['GET', 'DELETE', 'PUT'])
def usuario(id):
    if request.method == 'GET':
        usuario = getUsuarioById(id)
        if usuario is not None:
            return jsonify(usuario), 200
        else:
            return {}, 404
    elif request.method == 'PUT':
        # Recuperar dados da requisição: json.
        data = request.json
        rowupdate = updateUsuario(id, data)
        if rowupdate != 0:
            return (data, 201)
        else:
            return (data, 304)
    # Deleta um usuário se a requisição for um DELETE
    elif request.method == 'DELETE':
        rowdelete = deleteUsuario(id)
        if rowdelete != 0:
            return {}, 204
        else:
            return {}, 404


