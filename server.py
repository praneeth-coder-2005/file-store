from flask import Flask, render_template_string, abort
import sqlite3
import os

# Initialize Flask app
app = Flask(__name__)

# HTML template to display the stored links
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Stored Links</title>
</head>
<body>
    <h1>Your Links</h1>
    <ul>
        {% for link in links %}
            <li><a href="{{ link }}" target="_blank">{{ link }}</a></li>
        {% endfor %}
    </ul>
    <br>
    <a href="https://t.me/{{ bot_username }}" target="_blank">
        <button style="padding: 10px 20px; font-size: 16px;">Go Back to Telegram Bot</button>
    </a>
</body>
</html>
"""

def get_links_from_db(unique_id):
    """Fetch links from the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("SELECT url FROM links WHERE id = ?", (unique_id,))
    links = [row[0] for row in c.fetchall()]
    conn.close()
    return links

@app.route('/link/<unique_id>', methods=['GET'])
def get_links(unique_id):
    """Serve the links for a given unique ID."""
    links = get_links_from_db(unique_id)
    if links:
        return render_template_string(HTML_TEMPLATE, links=links, bot_username="YourBotUsername")
    else:
        abort(404, description="Links not found.")

if __name__ == '__main__':
    # Run the Flask app on the specified port
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
