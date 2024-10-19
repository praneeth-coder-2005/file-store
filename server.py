import os
from flask import Flask, send_from_directory, abort

app = Flask(__name__)

@app.route('/file/<filename>')
def serve_file(filename):
    file_path = os.path.join('files', filename)
    if os.path.exists(file_path):
        return send_from_directory('files', filename)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
