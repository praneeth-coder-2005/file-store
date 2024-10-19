from flask import Flask

app = Flask(__name__)

@app.route('/link/<unique_id>', methods=['GET'])
def confirm_access(unique_id):
    """Display a confirmation message when a link is accessed."""
    return f"<h1>Link with ID {unique_id} accessed successfully!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
