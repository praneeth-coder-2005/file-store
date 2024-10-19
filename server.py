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

# HTML Template with Improved Design for JW Player and Download Button
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stream & Download</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" integrity="sha512-Fo3rlrZj/kTcE+5tvb0tGdh8eABHxS2EPE0TPHzwGzMSM9vZbNpgK3KbgIg5tRT1Hp83KoDj2V7JQwZfyt2JHg==" crossorigin="anonymous" referrerpolicy="no-referrer" />
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
            text-align: center;
            background-color: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            width: 80%;
            max-width: 800px;
        }
        h1 {
            color: #333;
            margin-bottom: 20px;
        }
        #player {
            width: 100%;
            margin-bottom: 15px;
        }
        .button-container {
            margin-top: 20px;
        }
        .download-button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }
        .download-button:hover {
            background-color: #0056b3;
        }
        .download-button i {
            margin-right: 10px;
        }
    </style>
    <script src="https://cdn.jwplayer.com/libraries/your-jwplayer-library-key.js"></script>
</head>
<body>
    <div class="container">
        <h1>Stream & Download Your Video</h1>

        <div id="player"></div>

        <script>
            jwplayer("player").setup({
                file: "{{ link }}",
                width: "100%",
                aspectratio: "16:9",
                controls: true
            });
        </script>

        <div class="button-container">
            <a href="{{ link }}" download class="download-button">
                <i class="fas fa-download"></i> Download Video
            </a>
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
