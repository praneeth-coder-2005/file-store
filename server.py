from flask import Flask, render_template_string, abort
import os

app = Flask(__name__)

# In-memory storage for links (same as in bot.py)
stored_links = {}

# HTML Template for displaying the stored links and redirect button
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

@app.route('/link/<unique_id>', methods=['GET'])
def get_links(unique_id):
    """Serve the stored links as an HTML page."""
    links = stored_links.get(unique_id)
    if links:
        return render_template_string(HTML_TEMPLATE, links=links, bot_username="YourBotUsername")
    else:
        abort(404, description="Links not found.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
