from flask import Flask, render_template_string, abort
import sqlite3

app = Flask(__name__)

def get_link_from_db(slug):
    """Retrieve the video link from the database."""
    conn = sqlite3.connect("links.db")
    c = conn.cursor()
    c.execute("SELECT url FROM links WHERE id = ?", (slug,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

# Enhanced HTML Template with JW Player and Debugging Info
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream & Download</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f0f2f5;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 800px;
            text-align: center;
        }
        h1 {
            margin-bottom: 20px;
            color: #333;
        }
        #player {
            width: 100%;
            margin-bottom: 15px;
        }
        .download-button {
            background-color: #007bff;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            font-size: 16px;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.3s;
        }
        .download-button:hover {
            background-color: #0056b3;
        }
    </style>
    <script src="https://cdn.jwplayer.com/libraries/your-jwplayer-library-key.js"></script>
</head>
<body>
    <div class="container">
        <h1>Stream & Download Your Video</h1>

        <div id="player"></div>

        <script>
            // Check if the link is available before setting up JWPlayer
            const videoLink = "{{ link }}";
            if (videoLink) {
                jwplayer("player").setup({
                    file: videoLink,
                    width: "100%",
                    aspectratio: "16:9",
                    controls: true
                });
            } else {
                document.getElementById("player").innerHTML = "<p>Video not available.</p>";
            }
        </script>

        <div>
            <a href="{{ link }}" download class="download-button">Download Video</a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/link/<slug>', methods=['GET'])
def access_link(slug):
    """Serve the JW Player page with streaming and download."""
    link = get_link_from_db(slug)
    if link:
        return render_template_string(HTML_TEMPLATE, link=link)
    else:
        abort(404, description="Link not found.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
