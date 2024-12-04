from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de conexión a la base de datos
def connect_to_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',  # Cambia si tienes contraseña en MySQL
        database='GestionVehicular',
        cursorclass=pymysql.cursors.DictCursor
    )

# Ruta principal
@app.route('/')
def index():
    return redirect(url_for('formulario'))

# Ruta para el formulario
@app.route('/formulario')
def formulario():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ID_Persona, Nombre_Persona FROM Persona")
            personas = cursor.fetchall()
    finally:
        conn.close()
    return render_template('formulario.html', personas=personas)

# Ruta para procesar el formulario
@app.route('/enviar', methods=["POST"])
def ingreso():
    nuevo_nombre = request.form.get("nuevo_nombre")
    persona_nombre = request.form.get("persona")
    unidad = request.form.get("unidad")
    marca = request.form.get("marca")
    modelo = request.form.get("modelo")

    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            if nuevo_nombre:
                cursor.execute("INSERT INTO Persona (Nombre_Persona) VALUES (%s)", (nuevo_nombre,))
                conn.commit()

            persona_a_usar = persona_nombre if persona_nombre else nuevo_nombre
            cursor.execute("SELECT ID_Persona FROM Persona WHERE Nombre_Persona = %s", (persona_a_usar,))
            persona = cursor.fetchone()

            if persona:
                persona_id = persona['ID_Persona']
                sql = "INSERT INTO Vehiculo(ID_Persona, Unidad, Marca, Modelo) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (persona_id, unidad, marca, modelo))
                conn.commit()
                flash("Datos ingresados correctamente", "success")
            else:
                flash("Error: Persona no encontrada", "danger")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    finally:
        conn.close()

    return redirect(url_for('formulario'))

# Ruta para mostrar la tabla
@app.route('/tabla')
def tabla():
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT v.ID_Vehiculo, p.Nombre_Persona, v.Marca, v.Modelo, v.Unidad
                FROM Vehiculo v
                JOIN Persona p ON v.ID_Persona = p.ID_Persona
            """)
            vehiculos = cursor.fetchall()
    finally:
        conn.close()
    return render_template('tabla.html', vehiculos=vehiculos)



@app.route('/eliminar/<int:id>', methods=['GET'])
def eliminar_vehiculo(id):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM Vehiculo WHERE ID_Vehiculo = %s", (id,))
            conn.commit()
            flash('Vehículo eliminado correctamente', 'success')
    except Exception as e:
        flash(f"Error al eliminar el vehículo: {e}", 'danger')
    finally:
        conn.close()
    return redirect(url_for('tabla'))


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_vehiculo(id):
    conn = connect_to_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT v.ID_Vehiculo, p.Nombre_Persona, v.Unidad, v.Marca, v.Modelo
                FROM Vehiculo v
                JOIN Persona p ON v.ID_Persona = p.ID_Persona
                WHERE v.ID_Vehiculo = %s
            """, (id,))
            vehiculo = cursor.fetchone()

            if not vehiculo:
                flash("Vehículo no encontrado", "danger")
                return redirect(url_for('tabla'))

            if request.method == 'POST':
                persona_nombre = request.form['persona']
                unidad = request.form['unidad']
                marca = request.form['marca']
                modelo = request.form['modelo']

                cursor.execute("SELECT ID_Persona FROM Persona WHERE Nombre_Persona = %s", (persona_nombre,))
                persona = cursor.fetchone()

                if not persona:
                    flash("Error: Persona no encontrada", "danger")
                    return redirect(url_for('editar_vehiculo', id=id))

                persona_id = persona['ID_Persona']
                cursor.execute("""
                    UPDATE Vehiculo 
                    SET ID_Persona = %s, Unidad = %s, Marca = %s, Modelo = %s
                    WHERE ID_Vehiculo = %s
                """, (persona_id, unidad, marca, modelo, id))
                conn.commit()
                flash("Vehículo actualizado correctamente", "success")
                return redirect(url_for('tabla'))

            cursor.execute("SELECT Nombre_Persona FROM Persona")
            personas = cursor.fetchall()
    finally:
        conn.close()

    return render_template('editar_vehiculo.html', vehiculo=vehiculo, personas=personas)


if __name__ == '__main__':
    app.run(debug=True)
