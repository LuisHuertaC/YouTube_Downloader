from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp
import os
import threading
import time

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'downloads')

# Crear la carpeta de descargas si no existe
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    if request.method == 'POST':
        url = request.form['url']
        resolution = request.form['resolution'] or 'best'
        format_type = request.form['format']  # 'video' o 'audio'

        try:
            if format_type == 'audio':
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'cookiefile': 'cookies.txt',
                }
            else:  # Para video
                ydl_opts = {
                    'format': f'bestvideo[height<={resolution}]+bestaudio/best' if resolution != 'best' else 'bestvideo+bestaudio',
                    'merge_output_format': 'mp4',  # Asegura que el video final sea en formato mp4
                    'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
                    'cookiefile': 'cookies.txt',
                }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                file_name = ydl.prepare_filename(info_dict)  # Obtener el nombre del archivo

            # Convertir el archivo a mp4 si es necesario
            if format_type == 'video' and file_name.endswith('.webm'):
                mp4_file_name = file_name.replace('.webm', '.mp4')
                if not os.path.exists(mp4_file_name):
                    os.rename(file_name, mp4_file_name)
                    file_name = mp4_file_name

            # Enviar el archivo al cliente (el mp3 o el video)
            mp3_file_name = file_name.replace('.webm', '.mp3')  # Nombre del archivo convertido a mp3
            final_file = mp3_file_name if os.path.exists(mp3_file_name) else file_name

            @after_this_request
            def cleanup(response):
                def remove_files():
                    # Esperar un poco para asegurar que el archivo ha sido completamente enviado
                    time.sleep(60)
                    
                    # Eliminar el archivo que se ha enviado
                    try:
                        if os.path.exists(final_file):
                            os.remove(final_file)
                            print(f"Archivo {final_file} eliminado.")
                    except Exception as e:
                        print(f"Error al eliminar el archivo: {str(e)}")
                    
                    # Eliminar archivos antiguos en el directorio de descargas
                    try:
                        for filename in os.listdir(DOWNLOAD_FOLDER):
                            file_path = os.path.join(DOWNLOAD_FOLDER, filename)
                            if os.path.isfile(file_path) and file_path != final_file:
                                os.remove(file_path)
                                print(f"Archivo antiguo {file_path} eliminado.")
                    except Exception as e:
                        print(f"Error al eliminar archivos antiguos: {str(e)}")

                # Ejecutar la limpieza en un hilo separado
                threading.Thread(target=remove_files).start()
                return response

            return send_file(final_file, as_attachment=True, download_name=os.path.basename(final_file), mimetype='application/octet-stream')

        except Exception as e:
            return render_template('index.html', message=f"Ocurrió un error: {str(e)}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
