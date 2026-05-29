from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import re
import os

app = Flask(__name__, static_folder='static')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///financial.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_identificacion = db.Column(db.String(50), unique=True, nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    nombre_completo = db.Column(db.String(150), nullable=False)
    tarjetas = db.relationship('TarjetaCredito', backref='cliente', lazy=True)

class TarjetaCredito(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_tarjeta = db.Column(db.String(20), unique=True, nullable=False)
    fecha_vencimiento = db.Column(db.String(7), nullable=False)
    franquicia = db.Column(db.String(20))
    estado = db.Column(db.String(10), default='ACTIVO')
    cupo_total = db.Column(db.Float, nullable=False)
    cupo_disponible = db.Column(db.Float, nullable=False)
    cupo_utilizado = db.Column(db.Float)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)

def detectar_franquicia(numero):
    numero = numero.replace(' ', '').replace('-', '')
    if len(numero) == 16:
        if numero[0] == '4':
            return 'VISA'
        if 51 <= int(numero[:2]) <= 55:
            return 'MASTERCARD'
    if len(numero) == 15:
        if numero[:2] in ['34', '37']:
            return 'AMEX'
    return 'DESCONOCIDA'

def validar_fecha(fecha):
    return bool(re.match(r'^(0[1-9]|1[0-2])\/\d{4}$', fecha))

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    clientes = Cliente.query.all()
    result = []
    for c in clientes:
        result.append({
            'id': c.id,
            'numero_identificacion': c.numero_identificacion,
            'correo': c.correo,
            'nombre_completo': c.nombre_completo
        })
    return jsonify(result)

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    data = request.json
    if not data.get('numero_identificacion') or not data.get('correo') or not data.get('nombre_completo'):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    existente = Cliente.query.filter_by(numero_identificacion=data['numero_identificacion']).first()
    if existente:
        return jsonify({'error': 'Ya existe un cliente con ese número de identificación'}), 400
    cliente = Cliente(
        numero_identificacion=data['numero_identificacion'],
        correo=data['correo'],
        nombre_completo=data['nombre_completo']
    )
    db.session.add(cliente)
    db.session.commit()
    return jsonify({'id': cliente.id, 'mensaje': 'Cliente creado exitosamente'}), 201

@app.route('/api/tarjetas', methods=['GET'])
def get_tarjetas():
    tarjetas = TarjetaCredito.query.all()
    result = []
    for t in tarjetas:
        result.append({
            'id': t.id,
            'numero_tarjeta': t.numero_tarjeta,
            'fecha_vencimiento': t.fecha_vencimiento,
            'franquicia': t.franquicia,
            'estado': t.estado,
            'cupo_total': t.cupo_total,
            'cupo_disponible': t.cupo_disponible,
            'cupo_utilizado': t.cupo_utilizado,
            'cliente_id': t.cliente_id,
            'cliente_nombre': t.cliente.nombre_completo
        })
    return jsonify(result)

@app.route('/api/tarjetas', methods=['POST'])
def crear_tarjeta():
    data = request.json
    numero = data.get('numero_tarjeta', '').replace(' ', '').replace('-', '')
    if not numero or not data.get('fecha_vencimiento') or not data.get('cupo_total') or not data.get('cupo_disponible') or not data.get('cliente_id'):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400
    if not validar_fecha(data['fecha_vencimiento']):
        return jsonify({'error': 'Formato de fecha inválido. Use MM/YYYY'}), 400
    existente = TarjetaCredito.query.filter_by(numero_tarjeta=numero).first()
    if existente:
        return jsonify({'error': 'Ya existe una tarjeta con ese número'}), 400
    franquicia = detectar_franquicia(numero)
    cupo_total = float(data['cupo_total'])
    cupo_disponible = float(data['cupo_disponible'])
    cupo_utilizado = cupo_total - cupo_disponible
    tarjeta = TarjetaCredito(
        numero_tarjeta=numero,
        fecha_vencimiento=data['fecha_vencimiento'],
        franquicia=franquicia,
        estado='ACTIVO',
        cupo_total=cupo_total,
        cupo_disponible=cupo_disponible,
        cupo_utilizado=cupo_utilizado,
        cliente_id=data['cliente_id']
    )
    db.session.add(tarjeta)
    db.session.commit()
    return jsonify({'id': tarjeta.id, 'franquicia': franquicia, 'cupo_utilizado': cupo_utilizado, 'mensaje': 'Tarjeta creada exitosamente'}), 201

@app.route('/api/tarjetas/<int:id>', methods=['PUT'])
def editar_tarjeta(id):
    tarjeta = TarjetaCredito.query.get_or_404(id)
    data = request.json
    if 'cupo_total' not in data:
        return jsonify({'error': 'Solo se puede modificar el cupo total'}), 400
    tarjeta.cupo_total = float(data['cupo_total'])
    tarjeta.cupo_utilizado = tarjeta.cupo_total - tarjeta.cupo_disponible
    db.session.commit()
    return jsonify({'mensaje': 'Tarjeta actualizada', 'cupo_utilizado': tarjeta.cupo_utilizado})

@app.route('/api/tarjetas/<int:id>', methods=['DELETE'])
def eliminar_tarjeta(id):
    tarjeta = TarjetaCredito.query.get_or_404(id)
    tarjeta.estado = 'INACTIVO'
    db.session.commit()
    return jsonify({'mensaje': 'Tarjeta desactivada exitosamente'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)
