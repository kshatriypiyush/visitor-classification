from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import spacy

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests
nlp = spacy.load("en_core_web_sm")

# Simple in-memory cache
cache = {}

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        # Fetch website content and process it
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        text_content = ' '.join([p.text for p in soup.find_all('p')])

        doc = nlp(text_content)
        keywords = [chunk.text for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]

        primary_topic = keywords[0] if keywords else "the topic"
        question = f"What interests you most about {primary_topic}?"

        # Dynamic options based on keywords
        options = keywords[:4] if len(keywords) >= 4 else ["Business", "Technology", "Health", "Other"]

        result = {
            "question": question,
            "options": options,
            "keywords": keywords[:10]  # You can limit this for performance
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
