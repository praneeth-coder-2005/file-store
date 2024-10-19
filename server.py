from flask import Flask, render_template_string, abort
import sqlite3

app = Flask(__name__)

def get_link_from_db(slug):
    """Fetch a link by slug from the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("SELECT url FROM links WHERE id = ?", (slug,))
    result = c.fetchone()
    conn.close()

    return result[0] if result else None

# Enhanced HTML Template with Styling, JW Player, and Download Button
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream & Download</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            text-align: center;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #333;
        }
        .button-container {
            margin-top: 15px;
        }
        .download-button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
        }
        .download-button:hover {
            background-color: #0056b3;
        }
    </style>
    <script src="https://cdn.jwplayer.com/libraries/your-jwplayer-library-key.js"></script>
</head>
<body>
    <div class="container">
        <h1>Stream Your Video</h1>

        <div id="player"></div>

        <script>
            jwplayer("player").setup({
                file: "{{ link }}",
                width: "100%",
                aspectratio: "16:9"
            });
        </script>

        <div class="button-container">
            <a href="{{ link }}" download class="download-button">Download</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/link/<slug>', methods=['GET'])
def access_link(slug):
    """Serve the JW Player page with the streaming and download link."""
    link = get_link_from_db(slug)
    if link:
        return render_template_string(HTML_TEMPLATE, link=link)
    else:
        abort(404, description="Link not found.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
