from flask import Flask, jsonify, abort

app = Flask(__name__)

# In-memory storage for links (same as in bot.py)
stored_links = {}

@app.route('/link/<unique_id>', methods=['GET'])
def get_links(unique_id):
    """Serve the stored links for the given unique ID."""
    links = stored_links.get(unique_id)
    if links:
        return jsonify({"links": links})
    else:
        abort(404, description="Links not found.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
