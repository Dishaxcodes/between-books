from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from google import genai
import os
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configure Gemini AI
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

# Google Books API Key
BOOKS_API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')

# ─── ROUTES ───────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/preferences', methods=['GET', 'POST'])
def preferences():
    return render_template('preferences.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    recommendations = []
    book_info = None
    emotion = None
    error = None

    if request.method == 'POST':
        book_title = request.form.get('book_title')

        # Step 1 — Search Google Books API
        try:
            books_url = f"https://www.googleapis.com/books/v1/volumes?q={book_title}&key={BOOKS_API_KEY}&maxResults=1"
            books_response = requests.get(books_url)
            books_data = books_response.json()

            if 'items' in books_data:
                book = books_data['items'][0]['volumeInfo']
                book_info = {
                    'title': book.get('title', book_title),
                    'author': ', '.join(book.get('authors', ['Unknown'])),
                    'description': book.get('description', '')[:500],
                    'cover': book.get('imageLinks', {}).get('thumbnail', ''),
                    'link': book.get('infoLink', '')
                }

                # Step 2 — Gemini AI Emotional Analysis
                prompt_emotion = f"""
                Based on this book description, identify the main emotional themes and feelings:
                Book: {book_info['title']} by {book_info['author']}
                Description: {book_info['description']}
                
                Respond with ONLY 3-5 emotional words separated by commas. 
                Example: adventurous, hopeful, spiritual, uplifting
                """
                emotion_response = client.models.generate_content(
                   model='gemini-3.6-flash',
                    contents=prompt_emotion
                )
                emotion = emotion_response.text.strip()

                # Step 3 — Get Recommendations
                prompt_recs = f"""
                Recommend exactly 3 books that match these emotional themes: {emotion}
                Similar to: {book_info['title']} by {book_info['author']}
                
                Respond in this EXACT format for each book:
                TITLE: [book title]
                AUTHOR: [author name]
                REASON: [one sentence why it matches]
                ---
                """
                recs_response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt_recs
                )
                recs_text = recs_response.text.strip()

                # Parse recommendations
                books_raw = recs_text.split('---')
                for book_raw in books_raw:
                    if 'TITLE:' in book_raw:
                        lines = book_raw.strip().split('\n')
                        rec = {}
                        for line in lines:
                            if line.startswith('TITLE:'):
                                rec['title'] = line.replace('TITLE:', '').strip()
                            elif line.startswith('AUTHOR:'):
                                rec['author'] = line.replace('AUTHOR:', '').strip()
                            elif line.startswith('REASON:'):
                                rec['reason'] = line.replace('REASON:', '').strip()
                        if rec:
                            recommendations.append(rec)

            else:
                error = "Book not found. Please try another title."

        except Exception as e:
            error = f"Something went wrong. Please try again."
            print(f"Error: {e}")

    return render_template('home.html',
                           recommendations=recommendations,
                           book_info=book_info,
                           emotion=emotion,
                           error=error)

@app.route('/history')
def history():
    return render_template('history.html')

if __name__ == '__main__':
    app.run(debug=True)