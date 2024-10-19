from flask import Flask, render_template_string, abort
import sqlite3
import logging

app = Flask(__name__)

def get_link_from_db(slug):
    """Fetch a link by slug from the SQLite database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("SELECT url FROM links WHERE id = ?", (slug,))
    result = c.fetchone()
    conn.close()
    
    if result:
        logging.info(f"Link found for slug {slug}: {result[0]}")  # Debugging
        return result[0]
    else:
        logging.warning(f"No link found for slug: {slug}")  # Debugging
        return None

# HTML Template with JW Player and Download Button
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream & Download</title>
    <script src="https://cdn.jwplayer.com/libraries/your-jwplayer-library-key.js"></script>
</head>
<body>
    <h1>Stream Your Video</h1>

    <div id="player"></div>

    <script>
        jwplayer("player").setup({
            file: "{{ link }}",
            width: "100%",
            aspectratio: "16:9"
        });
    </script>

    <br>
    <a href="{{ link }}" download>
        <button style="padding: 10px 20px; font-size: 16px;">Download</button>
    </a>
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
