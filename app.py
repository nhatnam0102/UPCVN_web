import os
import logging
import datetime
from flask import Flask, render_template, request, redirect, url_for, g, session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Import translations
from translations.ja import translations as ja_translations
from translations.vi import translations as vi_translations

# Create Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "u-mate-secret-key")

# Available languages
LANGUAGES = {
    'ja': 'Japanese',
    'vi': 'Vietnamese'
}

# Default language
DEFAULT_LANGUAGE = 'ja'

# Translation dictionaries
translations = {
    'ja': ja_translations,
    'vi': vi_translations
}

@app.before_request
def before_request():
    # Set language from session or default to Japanese
    if 'language' not in session:
        session['language'] = DEFAULT_LANGUAGE
    
    # Make language and translations available to all templates
    g.language = session['language']
    g.translations = translations[g.language]
    g.available_languages = LANGUAGES
    
    # Add current date/time for templates
    g.now = datetime.datetime.now()

@app.route('/change_language/<language>')
def change_language(language):
    if language in LANGUAGES:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        company = request.form.get('company')
        
        # In a real application, you would process the form data here
        # For example, send an email, store in database, etc.
        
        # For now, just log the submission
        app.logger.info(f"Contact form submission: {name}, {email}, {company}")
        
        # Redirect back to index with a success parameter
        return redirect(url_for('index', contact_success=True))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
