from flask import Flask, abort

app = Flask(__name__)

@app.route('/link/<unique_id>', methods=['GET'])
def confirm_link_access(unique_id):
    """Show confirmation that the link is accessed."""
    return f"<h1>Link with ID {unique_id} was accessed!</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
