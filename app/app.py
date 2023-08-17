from flask import Flask, request, render_template
import os
import pandas as pd
import csv

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

import psycopg2
import pandas as pd
from sqlalchemy import create_engine

def delete_file(filename):
    try:
        os.remove(filename)
        print(f"Archivo '{filename}' eliminado exitosamente.")
    except Exception as e:
        print("Error al eliminar el archivo:", e)

def read_csv_to_arrays(filename):
    arrays = []

    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            arrays.append(row)

    delete_file(filename)

    return arrays

def perform_predictions_and_update_csv(filename):
    # Conexión a la base de datos
    conn = psycopg2.connect(database="postgres", user="postgres", password="1234", host="localhost")

    # Crear un motor SQLAlchemy
    engine = create_engine('postgresql+psycopg2://postgres:1234@localhost/postgres')

    # Borrar la tabla recién creada
    drop_table_query = "DROP TABLE IF EXISTS time_series_data;"
    cursor = conn.cursor()
    cursor.execute(drop_table_query)
    conn.commit()

    # Leer los datos del archivo CSV
    data = pd.read_csv(filename)

    # Obtener la cantidad de columnas
    num_columns = len(data.columns)

    # Crear una tabla en la base de datos
    create_table_query = f"CREATE TABLE time_series_data (time_series_id SERIAL PRIMARY KEY, {', '.join([f'col{i+1} FLOAT' for i in range(num_columns)])});"
    cursor.execute(create_table_query)
    conn.commit()

    # Cargar los datos en la tabla uno por uno
    for index, row in data.iterrows():
        values = ', '.join([str(row[i]) for i in range(num_columns)])
        insert_query = f"INSERT INTO time_series_data ({', '.join([f'col{i+1}' for i in range(num_columns)])}) VALUES ({values});"
        cursor.execute(insert_query)
        conn.commit()

    # Crear índices predictivos para cada columna
    for i in range(num_columns):
        col_name = f'col{i+1}'
        create_index_query = f"SELECT create_pindex('time_series_data', 'time_series_id', '{{{col_name}}}', 'pindex_{i+1}', k => 4);"
        cursor.execute(create_index_query)
        conn.commit()

    # Realizar predicciones y actualizar los datos en la base de datos
    for i in range(num_columns):
        col_name = f'col{i+1}'
        prediction_query = f"SELECT * FROM predict('time_series_data', '{col_name}', 1, 'pindex_{i+1}');"
        prediction = pd.read_sql_query(prediction_query, engine)
        update_query = f"UPDATE time_series_data SET {col_name} = {prediction.at[0, 'prediction']} WHERE time_series_id = 1;"
        cursor.execute(update_query)
        conn.commit()

    # Guardar los datos actualizados en el archivo CSV
    updated_data = pd.read_sql_query("SELECT * FROM time_series_data;", engine)
    updated_data.to_csv(filename + "_predictor.csv", index=False)

    # Borrar la tabla recién creada
    drop_table_query = "DROP TABLE IF EXISTS time_series_data;"
    cursor.execute(drop_table_query)
    conn.commit()

    # Cerrar la conexión
    conn.close()

    delete_file(filename)

    return read_csv_to_arrays(filename + "_predictor.csv")



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_xlsx_to_csv(xlsx_filename):
    try:
        # Cargar el archivo Excel en un DataFrame
        df = pd.read_excel(xlsx_filename)
        
        # Cambiar la extensión del nombre de archivo a .csv
        csv_filename = xlsx_filename.replace('.xlsx', '.csv')
        
        # Guardar el DataFrame como archivo .csv
        df.to_csv(csv_filename, index=False)

        delete_file(xlsx_filename)

        print(f"Archivo '{xlsx_filename}' convertido a '{csv_filename}' con éxito.")

        return perform_predictions_and_update_csv(csv_filename)
        
       
    except Exception as e:
        print("Error:", e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No se seleccionó ningún archivo'

    file = request.files['file']


    if file.filename == '':
        return 'No se seleccionó ningún archivo'
    

    if file and allowed_file(file.filename):
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

        import subprocess

        # Ejecuta el comando pwd
        result = subprocess.run(["pwd"], capture_output=True, text=True)
        print(result)

        file.save(filename)

        
        return convert_xlsx_to_csv(filename)
        #return 'Archivo subido, convertido y actualizado con éxito'
        
    return 'Archivo no permitido'

if __name__ == '__main__':
    app.run(debug=True)