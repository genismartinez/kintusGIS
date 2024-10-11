from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Definir el modelo para la base de datos
class Municipio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    fecha_actuacion = db.Column(db.String(20), nullable=True)  # Fecha de actuación
    tocat = db.Column(db.String(3), nullable=False, default='No')  # Si se ha tocado

# Ruta principal para mostrar el mapa
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para obtener los municipios como GeoJSON
@app.route('/municipios')
def obtener_municipios():
    municipios_db = Municipio.query.all()
    municipios = [{"type": "Feature", "properties": {"NOMMUNI": m.nombre, "fecha_actuacion": m.fecha_actuacion, "tocat": m.tocat}, "geometry": None} for m in municipios_db]
    return jsonify({"type": "FeatureCollection", "features": municipios})

# Ruta para ver la lista de conciertos
@app.route('/concerts')
def lista_conciertos():
    municipios_db = Municipio.query.filter_by(tocat='Si').order_by(Municipio.fecha_actuacion).all()
    return render_template('concerts.html', municipios=municipios_db)

# Ruta para añadir un nuevo municipio
@app.route('/add', methods=['POST'])
def add_municipio():
    nombre = request.form['nombre']
    fecha_actuacion = request.form['fecha']

    # Comprobar si el municipio ya existe en la base de datos
    municipio = Municipio.query.filter_by(nombre=nombre).first()
    if municipio:
        municipio.fecha_actuacion = fecha_actuacion
        municipio.tocat = 'Si'
    else:
        # Añadir un nuevo municipio
        nuevo_municipio = Municipio(nombre=nombre, fecha_actuacion=fecha_actuacion, tocat='Si')
        db.session.add(nuevo_municipio)

    db.session.commit()  # Guardar los cambios en la base de datos
    return jsonify({"message": "Municipio añadido correctamente"})

# Ruta para eliminar un municipio de la lista "Tocados"
@app.route('/remove', methods=['POST'])
def remove_municipio():
    nombre = request.form['nombre']
    municipio = Municipio.query.filter_by(nombre=nombre).first()
    if municipio:
        municipio.tocat = 'No'
        municipio.fecha_actuacion = None
        db.session.commit()
        return jsonify({"message": f"Municipio {nombre} eliminado correctamente"})

    return jsonify({"message": f"Municipio {nombre} no encontrado"}), 404

if __name__ == '__main__':
    app.run(debug=True)
