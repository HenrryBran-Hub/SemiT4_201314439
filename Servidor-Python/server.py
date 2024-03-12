from flask import Flask, request, jsonify
from dotenv import load_dotenv
import boto3
import base64
import os

app = Flask(__name__)

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las variables de entorno
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')

# Configurar el cliente de Rekognition
rekognition_client = boto3.client('rekognition', 
                                  aws_access_key_id=AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                  region_name=AWS_REGION)

# Ruta al directorio de subidas
UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/tarea4-201314439', methods=['POST'])
def procesar_imagen():
     # Verificar si se proporcionaron ambos archivos
    if 'file1' not in request.files or 'file2' not in request.files:
        return jsonify({'error': 'Se deben proporcionar dos archivos'}), 400

    file1 = request.files['file1']
    file2 = request.files['file2']

    # Guardar las imágenes en el servidor
    filename1 = file1.filename
    filename2 = file2.filename
    file_path1 = os.path.join(UPLOAD_FOLDER, filename1)
    file_path2 = os.path.join(UPLOAD_FOLDER, filename2)
    file1.save(file_path1)
    file2.save(file_path2)

    # Leer las imágenes en formato base64
    with open(file_path1, "rb") as image_file1:
        encoded_string1 = base64.b64encode(image_file1.read()).decode()
    with open(file_path2, "rb") as image_file2:
        encoded_string2 = base64.b64encode(image_file2.read()).decode()

    # Eliminar las imágenes del servidor
    os.remove(file_path1)
    os.remove(file_path2)


    # Enviar las imágenes a Rekognition
    response = rekognition_client.compare_faces(
        SourceImage={'Bytes': base64.b64decode(encoded_string1)},
        TargetImage={'Bytes': base64.b64decode(encoded_string2)}
    )

    # Obtener el porcentaje de similitud
    similarity_percentage = None
    if response['FaceMatches']:
        similarity_percentage = response['FaceMatches'][0]['Similarity']

    return jsonify({'imagen1': filename1, 'imagen2': filename2, 'porcentaje_similitud': similarity_percentage}), 200

if __name__ == '__main__':
    app.run(debug=True)
