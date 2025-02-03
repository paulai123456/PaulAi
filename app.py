from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
import random
from fuzzywuzzy import process
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from langdetect import detect
from textblob import TextBlob  # Import TextBlob for sentiment analysis
from flask_socketio import SocketIO, join_room, leave_room, send
import requests
import pylint.lint
import io
import sys
# Replace with your actual API key
API_KEY = 'c0207e1a904649319b81f092769e8a20'
# Modify this URL if you want a different news source or parameters
URL = f'https://newsapi.org/v2/everything?q=AI&language=en&sortBy=publishedAt&apiKey={API_KEY}'
app = Flask(__name__)
app.secret_key = 'paul041011'  # Set a secret key for session encryption
# Set your OpenAI API key
socketio = SocketIO(app)
forum_posts = []  # A list to store forum posts
# File to store forum posts
POSTS_FILE = "forum_posts.json"
def save_posts_to_file(posts):
    # Logic to save posts to a file (e.g., JSON file)
    with open('forum_posts.json', 'w') as f:
        json.dump(posts, f)
# Path to the JSON file that stores applications
APPLICATIONS_FILE = "applications.json"

# Initialize the applications.json file if it doesn't exist
if not os.path.exists(APPLICATIONS_FILE):
    with open(APPLICATIONS_FILE, "w") as file:
        json.dump([], file)  # Start with an empty list
# Simple in-memory user store (replace with a database in production)
users_db = {}
# File name to store users data
file_name = "users_db.json"
# Path to save the chats
CHAT_FILE = 'saved_chats.json'
# Mock storage for saved chats
saved_chats = []
# Folder where uploaded files will be stored
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allow only specific file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Define a path for the file where messages will be saved
CONTACT_MESSAGES_FILE = 'contact_messages.json'

# File path to store registrations
REGISTRATION_FILE = 'registrations.json'


# Predefined responses (example)
responses = {
     "how to solve 6+3": ["the answer will be 9", "answer is 9"],
    "how to solve 7+3": ["the answer will be 10", "answer is 10"],
    "what day is new year": ["january 1"],
    "what is the capital of japan?": ["tokyo"],
    "who is your creator": ["my creator is paul"],    
    "photosynthesis?": ["the process plants use to make food from sunlight."],
    "gravity": ["gravity is a force that pulls objects toward each other."],
    "how to solve 8+3": ["the answer will be 11", "answer is 11"],
    "how to solve 9+3": ["the answer will be 12", "answer is 12"],
    "how to solve 1+1": ["the answer will be 2", "answer is 2"],
    "how to solve 2+2": ["the answer will be 4", "answer is 4"],
    "how to solve 3+3": ["the answer will be 6", "answer is 6"],
    "how to solve 4+4": ["the answer will be 8", "answer is 8"],
    "how to solve 5+5": ["the answer will be 10", "answer is 10"],
    "how to solve 6+6": ["the answer will be 12", "answer is 12"],
    "how to solve 7+7": ["the answer will be 14", "answer is 14"],
    "how to solve 8+8": ["the answer will be 16", "answer is 16"],
    "how to solve 9+9": ["the answer will be 18", "answer is 18"],
    "what day is christmas?": ["december 25"],
    "answer 1+1 for me": ["the answer is 2"],
    "how do i teach you something?": ["just type 'teach me (question): (answer)' and i\u2019ll learn it!"],
    "what can you do?": ["i can answer questions, chat with you, and even learn new things!"],
    "how can i improve my coding skills?": ["practice makes perfect! try solving coding problems, building projects, and learning new concepts."],
    "what is 10 times 10?": ["10 times 10 equals 100!"],
    "tell me a fun fact.": ["did you know that honey never spoils? archaeologists have found pots of honey in ancient tombs that are over 3,000 years old!"],
    "what is python?": ["python is a popular programming language used for web development, data analysis, and more!"],
    "joke": ["Why did the chicken cross the road? To get to the other side."],
    "random fact": ["The moon is made of cheese."],
    "what is the sqaure root of 36?": ["The square root of 36 is 6."],
    "what is the square root of 16?": ["the square root of 16 is 4."],
    "what is the capital of india": ["The capital of India is New Delhi."],
    "what is the capital of the united states": ["The capital of the United States is Washington, D.C."],
    "what is the capital of canada": ["The capital of Canada is Ottawa."],
    "what is the capital of the united kingdom": ["The capital of the United Kingdom is London."],
    "what is the capital of the netherlands": ["The capital of the Netherlands is Amsterdam."],
    "fact": ["The first computer virus was created by Grace Hopper in 1947."],
    "what is love?": ["Love is a feeling of deep affection and emotional attachment."],
    "what is the capital of the philippines": ["the answer will be manila"],
    "what is the meaning of life": ["The meaning of life is to live a good life.", "The meaning of life is to live a happy life."],
    "thank you": ["You're welcome!", "No problem!", "Glad to help!", "Anytime!"],
    "who is the president of the usa": ["The president of the USA is Donald Trump", "Donald Trump is the current president of the USA."],
    "what is the largest planet": ["The largest planet is Jupiter.", "Jupiter is the biggest planet in our solar system."],
    "how many continents are there": ["There are 7 continents.", "We have 7 continents on Earth."],
    "what is computer": ["a computer is an electronic device that processes data and performs tasks according to instructions provided by software. it operates using binary code (a system of ones and zeros) and is capable of executing a wide variety of functions, including calculations, data processing, communication, and multimedia playback."],
    "what is the capital of france": ["The capital of France is Paris.", "Paris is the capital of France."],
    "what is the capital of spain": ["The capital of Spain is Madrid.", "Madrid is the capital of Spain."],
    "what is the capital of italy": ["The capital of Italy is Rome.", "Rome is the capital of Italy."],
    "what is the capital of germany": ["The capital of Germany is Berlin.", "Berlin is the capital of Germany."],
    "sorry": ["It's okay!", "No worries!", "No need to apologize!", "All good!"],
    "since when did war world 1 start?": ["july 28, 1914 to november 11, 1918"],
    "help": ["How can I assist you?", "What do you need help with?", "I am here to help!", "Tell me what you need assistance with."],
    "name": ["I have a name, but you can call me PaulAi!", "I'm just an AI assistant!", "I go by PaulAi."],
    "favorite color": ["I don't have a favorite color, but I like all of them!", "I'm not sure, but blue is nice!"],
    "what is math?": ["Math is the study of numbers and their relationships.", "Math is the science of numbers."],
    "hello": ["Hi!", "Hello!", "Hey there!"],
    "hi": ["Hi there!"],
    "how are you": ["I'm doing great, thanks for asking!", "I'm good, how about you?"],
    "bye": ["Goodbye!", "See you later!", "Take care!"],
    "default": ["Sorry, I don't understand."],
}

# List of daily tips
tips = [
    "Take a 5-minute break every hour to refresh your mind.",
    "Use keyboard shortcuts to speed up your workflow.",
    "Believe in your ability to grow and improve each day.",
    "Drink plenty of water to stay hydrated and focused.",
    "Set clear goals and break them down into manageable tasks.",
    "Practice mindfulness to improve your mental well-being."
]


# Dummy in-memory data storage for categories and threads (replace with database in production)
categories = {
    "General": [
        {"title": "Welcome to the forum!", "content": "Feel free to introduce yourself."},
        {"title": "General Discussion", "content": "Talk about anything here!"}
    ],
    "Technology": [
        {"title": "AI and Machine Learning", "content": "Let's discuss the latest in AI."},
        {"title": "Web Development", "content": "Discuss front-end and back-end technologies."}
    ]
}


# Dummy list to store challenge responses
challenge_responses = []
# File names for storing data
feedback_file = "feedback.json"
responses_file = "responses.json"

# Define the file path for storing user data
users_file = "users_db.json"

# Example of defining default_data
default_data = {
    "is_premium": False,
    "preferences": {},
    "messages": []
}
# Variable to store the current persona
current_persona = 'friendly'

# Function to return greeting based on the persona
def get_persona_greeting():
    if current_persona == 'friendly':
        return "Hi there! How can I help you today?"
    elif current_persona == 'professional':
        return "Good day. How may I assist you?"
    elif current_persona == 'humorous':
        return "Hey, I'm your friendly chatbot. What can I do for you, buddy?"
    else:
        return "Hello! How can I assist you?"


# Define global variables to track game state
current_game = None
game_data = {}

# Define the trivia game function
def trivia_game():
    questions = [
        {"question": "What is the capital of France?", "options": ["a) Berlin", "b) Madrid", "c) Paris", "d) Rome"], "answer": "c"},
        {"question": "Which planet is known as the Red Planet?", "options": ["a) Earth", "b) Mars", "c) Venus", "d) Jupiter"], "answer": "b"},
        {"question": "Who wrote 'Hamlet'?", "options": ["a) Charles Dickens", "b) J.K. Rowling", "c) William Shakespeare", "d) Mark Twain"], "answer": "c"},
    ]

    score = 0
    random.shuffle(questions)
    return f"Welcome to the Trivia Quiz! Answer by typing a, b, c, or d.<br>{format_question(questions[0])}"

def format_question(question):
    formatted = f"<b>{question['question']}</b><br>"
    for option in question['options']:
        formatted += f"{option}<br>"
    return formatted

# Define the hangman game function
def hangman_game():
    words = ["python", "chatbot", "artificial", "intelligence", "flask"]
    word = random.choice(words).lower()
    guessed = "_" * len(word)
    attempts = 6
    game_data['word'] = word
    game_data['guessed'] = guessed
    game_data['attempts'] = attempts
    return f"Welcome to Hangman! Guess the word letter by letter.<br>The word is: {guessed}"

# Define the storytelling game function
def storytelling_game():
    game_data['story'] = "Once upon a time, a brave knight set out on a journey.<br>"
    return game_data['story'] + "Continue the story by typing your part!"

def handle_trivia_answer(answer):
    questions = [
        {"question": "What is the capital of France?", "options": ["a) Berlin", "b) Madrid", "c) Paris", "d) Rome"], "answer": "c"},
        {"question": "Which planet is known as the Red Planet?", "options": ["a) Earth", "b) Mars", "c) Venus", "d) Jupiter"], "answer": "b"},
        {"question": "Who wrote 'Hamlet'?", "options": ["a) Charles Dickens", "b) J.K. Rowling", "c) William Shakespeare", "d) Mark Twain"], "answer": "c"},
    ]
    question = questions[0]  # Simplified for now, pick the first question
    if answer == question["answer"]:
        return "Correct! Here's the next question:<br>" + format_question(questions[1])
    else:
        return "Incorrect. The correct answer was " + question["answer"] + ".<br>Here's the next question:<br>" + format_question(questions[1])

def handle_hangman_guess(guess):
    word = game_data['word']
    guessed = game_data['guessed']
    attempts = game_data['attempts']

    if guess in word:
        guessed = "".join([letter if letter == guess or guessed[i] != "_" else "_" for i, letter in enumerate(word)])
        game_data['guessed'] = guessed
        if "_" not in guessed:
            return f"Congratulations! You guessed the word: {word}"
        else:
            return f"Good guess! The word is now: {guessed}. You have {attempts} attempts left."
    else:
        attempts -= 1
        game_data['attempts'] = attempts
        if attempts == 0:
            return f"Game over! The word was: {word}"
        else:
            return f"Wrong guess! You have {attempts} attempts left."

def handle_story_input(story_part):
    game_data['story'] += " " + story_part
    return game_data['story'] + "<br>Continue adding to the story!"

def load_json_file(file_name, default_data):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            return default_data
    return default_data

def save_json_file(file_name, data):
    with open(file_name, "w") as file:
        json.dump(data, file, indent=4)

# Load initial data
users_db = load_json_file(users_file, {})
responses = load_json_file(responses_file, responses)



# Load users from the file if it exists
def load_users_db():
    global users_db
    try:
        with open(file_name, "r") as file:
            users_db = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, initialize an empty dictionary
        users_db = {}

# Save users to the file
def save_users_db():
    with open(file_name, "w") as file:
        json.dump(users_db, file, indent=4)


# Load existing responses
def load_challenge_responses():
    try:
        with open("challenges_responses.json", "r") as file:
            return json.load(file)
    except IOError:
        return {}

# Save the updated responses with the badge
def save_challenge_responses():
    try:
        with open("challenges_responses.json", "w") as file:
            json.dump(responses, file, indent=4)
    except IOError:
        print("Error saving challenges responses to the file.")

def assign_top_respondent_badge():
    # Assuming 'responses' is a dictionary with user responses and scores
    top_user = None
    top_score = -1

    # Find the top respondent based on their score
    for user, data in responses.items():
        if data['score'] > top_score:
            top_score = data['score']
            top_user = user

    if top_user:
        # Assign the badge
        responses[top_user]['badge'] = 'Top Respondent'
        save_challenge_responses()
        return top_user  # Return the user who received the badge
    return None


        # Function to load chats from the file
def load_saved_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, 'r') as file:
            return json.load(file)
    else:
        return []

def detect_language(message):
    return detect(message)

# Function to save a chat to the file
def save_chat_to_file(chat_data):
    chats = load_saved_chats()
    chat_data['time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add time for each chat
    chats.append(chat_data)

    with open(CHAT_FILE, 'w') as file:
        json.dump(chats, file)

# Load responses from the file if it exists, else use default responses
def load_responses():
    if os.path.exists("responses.json"):
        try:
            with open("responses.json", "r") as file:
                loaded_responses = json.load(file)
                if isinstance(loaded_responses, dict):
                    return loaded_responses  # Only load if it's a valid dictionary
                else:
                    print("Invalid data format in responses.json. Using default responses.")
                    return responses  # Fall back to default responses if the format is wrong
        except json.JSONDecodeError:
            print("Error loading responses from the file. Using default responses.")
            return responses  # Fall back to default responses if the file is malformed
    else:
        # Initialize the responses file with default responses if it doesn't exist
        with open("responses.json", "w") as file:
            json.dump(responses, file, indent=4)  # Save the default responses
        return responses  # Return default responses



# Save the updated responses to the file
def save_responses():
    try:
        with open("responses.json", "w") as file:
            json.dump(responses, file, indent=4)  # Save responses to file in a pretty format
    except IOError:
        print("Error saving responses to the file.")

# Function to get chatbot response
def get_response(user_input):
    user_input = user_input.lower()

    # Special case for teaching the bot
    if user_input.startswith("teach me"):
        # Format: teach me <question> : <answer>
        parts = user_input[8:].strip().split(":", 1)  # Split the input into question and answer
        if len(parts) == 2:
            question, answer = parts[0].strip(), parts[1].strip()
            # Add or update the response for the given question
            responses[question] = [answer]  # Store the answer as a list of responses
            save_responses()  # Save the updated responses to the file
            return "I have learned a new response!"
        else:
            return "Please format the teaching command as: teach me <question>: <answer>."


    # Use fuzzy matching to find the best match
    best_match = process.extractOne(user_input, responses.keys())
    if best_match and best_match[1] >= 60:  # Set threshold for similarity (60%)
        response_key = best_match[0]
        return random.choice(responses[response_key])

    return random.choice(responses["default"])


def store_analytics(message, response, sentiment, language):
    analytics = {
        "message": message,
        "response": response,
        "sentiment": sentiment,
        "language": language,
    }

    with open('analytics.json', 'a') as file:
        json.dump(analytics, file)
        file.write("\n")


    # Load feedback data from file
def load_feedback():
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    return []
    # Function to load chats from the file
def load_saved_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, 'r') as file:
            return json.load(file)
    else:
        return []

# Save feedback to the file
def save_feedback(feedback_data):
    with open(feedback_file, "w") as file:
        json.dump(feedback_data, file, indent=4)

def load_user_profile():
    try:
        # Load the profile from a file or database
        with open('user_profile.json', 'r') as f:
            profile_data = json.load(f)

        # Ensure that profile_data includes a key for 'profile_picture' even if it's not set
        if 'profile_picture' not in profile_data:
            profile_data['profile_picture'] = None  # Default to None if no profile picture exists

        return profile_data
    except FileNotFoundError:
        # Return default values if the file does not exist
        return {
            "username": "Guest", 
            "bio": "No bio available.",
            "profile_picture": None  # Default profile picture is None if no file is found
        }

def save_user_profile(profile_data):
    # Your saving logic here
    # For example, save the profile to a file or database
    with open('user_profile.json', 'w') as f:
        json.dump(profile_data, f)

def allowed_file(filename):
    """
    Checks if the uploaded file has a valid extension (image file).
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
PROJECTS_FILE = 'community_projects.json'
MEMBERS_FILE = 'community_members.json'  # Store community members in a separate JSON file

# Load projects from JSON file
def load_projects():
    try:
        with open(PROJECTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"featured": [], "ongoing": []}

# Save projects to JSON file
def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=4)

# Load members from JSON file
def load_members():
    try:
        with open(MEMBERS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"members": []}

# Save members to JSON file
def save_members(members):
    with open(MEMBERS_FILE, 'w') as f:
        json.dump(members, f, indent=4)

# Pre-defined templates for content generation
def generate_content(content_type, tone, length, prompt):
    if content_type == 'blog':
        return generate_blog_post(tone, length, prompt)
    elif content_type == 'email':
        return generate_email(tone, length, prompt)
    elif content_type == 'product-description':
        return generate_product_description(tone, length, prompt)
    elif content_type == 'social-media':
        return generate_social_media_post(tone, length, prompt)
    else:
        return "Content type not supported."

# Pre-defined Blog Post Template
def generate_blog_post(tone, length, prompt):
    intro = f"In today’s world, {prompt} is becoming increasingly important. Here's why you should care about it."
    body = f"{prompt} is a topic that has seen much attention recently. It brings numerous opportunities and challenges, especially in the areas of technology and business."
    conclusion = f"In conclusion, {prompt} is something you need to start paying attention to, and it will continue to evolve."

    if tone == 'casual':
        intro = intro.replace("increasingly important", "pretty interesting")
        body = body.replace("attention recently", "buzz lately")
        conclusion = conclusion.replace("paying attention to", "keep an eye on")

    # Handling Length Options for Blog Post
    if length == 'short':
        body = body[:150]  # Short length
        return f"Title: {prompt} - Why It's Important\n\nIntroduction: {intro}\n\nMain Body: {body}\n\nConclusion: {conclusion}"

    elif length == 'medium':
        body = body[:300]  # Medium length
        return f"Title: {prompt} - Why It's Important\n\nIntroduction: {intro}\n\nMain Body: {body}\n\nConclusion: {conclusion}"

    elif length == 'long':
        return f"Title: {prompt} - Why It's Important\n\nIntroduction: {intro}\n\nMain Body: {body}\n\nConclusion: {conclusion}"

# Pre-defined Email Template
def generate_email(tone, length, prompt):
    subject = f"Update on {prompt}"
    greeting = f"Dear valued customer,"
    body = f"We wanted to share some exciting news about {prompt}. Here's what we've been working on:\n\n1. {prompt} developments.\n2. Future plans regarding {prompt}.\n3. How this affects you."

    if tone == 'formal':
        greeting = "Dear Sir/Madam,"
        body = f"As an important customer, we would like to provide you with the latest updates on {prompt}."

    # Handling Length Options for Email
    if length == 'short':
        body = body[:150]  # Short length
        return f"Subject: {subject}\n\n{greeting}\n\n{body}"

    elif length == 'medium':
        body = body[:300]  # Medium length
        return f"Subject: {subject}\n\n{greeting}\n\n{body}"

    elif length == 'long':
        return f"Subject: {subject}\n\n{greeting}\n\n{body}\n\nBest regards, Your Company"

# Pre-defined Product Description Template
def generate_product_description(tone, length, prompt):
    intro = f"Introducing the latest in {prompt}, designed to make your life easier and more efficient."
    features = [
        f"Feature 1: {prompt} provides exceptional performance.",
        f"Feature 2: With {prompt}, you’ll experience seamless integration with your devices.",
        f"Feature 3: {prompt} is built to last, offering top-tier durability and reliability."
    ]
    conclusion = f"Upgrade your experience today with {prompt}, and enjoy a new level of ease and functionality."

    if tone == 'casual':
        intro = intro.replace("designed to make your life easier", "made to help you out more.")
        features[0] = features[0].replace("exceptional performance", "great performance")
        conclusion = conclusion.replace("Upgrade your experience today", "Try it now and see the difference")

    # Handling Length Options for Product Description
    if length == 'short':
        return f"Product: {prompt}\n\n{intro}\n\n{features[0]}\n\n{conclusion}"

    elif length == 'medium':
        return f"Product: {prompt}\n\n{intro}\n\n{features[0]}\n\n{features[1]}\n\n{conclusion}"

    elif length == 'long':
        return f"Product: {prompt}\n\n{intro}\n\n{features[0]}\n\n{features[1]}\n\n{features[2]}\n\n{conclusion}"

# Pre-defined Social Media Post Template
def generate_social_media_post(tone, length, prompt):
    if tone == 'casual':
        post = f"Hey everyone! 👋 Are you ready to learn more about {prompt}? It's a total game-changer! 🚀 #Innovation #FutureOf{prompt}"
    elif tone == 'formal':
        post = f"Discover the latest trends in {prompt}. Stay ahead of the curve and understand how {prompt} is reshaping the industry. #BusinessInnovation #Trends"
    else:
        post = f"Check out the latest on {prompt}. You won’t want to miss this! #BreakingNews"

    # Handling Length Options for Social Media Post
    if length == 'short':
        return post[:150]  # Short length
    elif length == 'medium':
        return post[:250]  # Medium length
    elif length == 'long':
        return post  # Full-length post

@app.route('/generate-content', methods=['POST'])
def generate_content_route():
    # Extract form data from the frontend request
    content_type = request.form['content_type']
    tone = request.form['tone']
    length = request.form['length']
    prompt = request.form['input_text']
    
    # Call the generate_content function with the received parameters
    generated_content = generate_content(content_type, tone, length, prompt)

    # Return the generated content in JSON format to the frontend
    return jsonify({"generated_content": generated_content})

# API to submit a project
@app.route('/submit_project', methods=['POST'])
def submit_project():
    data = request.json
    projects = load_projects()

    # Add the project to the ongoing projects list
    new_project = {
        "title": data.get('title'),
        "description": data.get('description'),
        "link": data.get('link')
    }
    projects['ongoing'].append(new_project)
    save_projects(projects)

    return jsonify({"message": "Project submitted successfully!"}), 200

# API to get projects
@app.route('/get_projects', methods=['GET'])
def get_projects():
    return jsonify(load_projects())

# API to get members
@app.route('/get_members', methods=['GET'])
def get_members():
    return jsonify(load_members())

# API to add a member
@app.route('/add_member', methods=['POST'])
def add_member():
    data = request.json
    members = load_members()

    # Add the new member to the list
    new_member = {
        "name": data.get('name'),
        "email": data.get('email'),
        "role": data.get('role')
    }
    
    members['members'].append(new_member)
    save_members(members)

    return jsonify({"message": "Member added successfully!"}), 200

@app.route('/community')
def community():
    return render_template('community.html')

# Route to handle registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Get the form data
    name = data.get('name')
    email = data.get('email')
    session_id = data.get('session_id')

    # Read existing registrations from the JSON file
    try:
        with open('registrations.json', 'r') as file:
            registrations = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        registrations = []

    # Add new registration to the list
    registration = {
        'name': name,
        'email': email,
        'session_id': session_id
    }
    registrations.append(registration)

    # Save updated registrations back to the JSON file
    with open('registrations.json', 'w') as file:
        json.dump(registrations, file, indent=4)

    # Send a response back to the frontend
    return jsonify({'success': True})

@app.route('/create_post', methods=['POST'])
def create_post():
    group_name = request.form.get('group_name')
    title = request.form.get('post_title')
    content = request.form.get('post_content')
    file = request.files.get('attachment')

    if not title or not content:
        return "Title and Content are required", 400

    # Save media if uploaded
    media_path = ""
    if file and allowed_file(file.filename):
        filename = file.filename
        media_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(media_path)

    # Save post to the database
    new_post = {
        "id": len(forum_posts) + 1,
        "username": session.get('username', 'Guest'),
        "group_name": group_name,
        "title": title,
        "content": content,
        "media": media_path
    }
    forum_posts.append(new_post)

    # Now pass forum_posts to the save function
    save_posts_to_file(forum_posts)

    return redirect(url_for('forum'))

@app.route('/chatbot')
def chatbot():
    username = session.get('username', None)
    return render_template('index.html', username=username)  # Existing chatbot UI

# Function to read analytics data
def read_analytics():
    with open('analytics.json', 'r') as file:
        return json.load(file)

# Function to update analytics data
def update_analytics(new_data):
    with open('analytics.json', 'w') as file:
        json.dump(new_data, file, indent=4)

# Sentiment analysis using TextBlob (for simplicity)
def analyze_sentiment(message):
    polarity = TextBlob(message).sentiment.polarity
    if polarity > 0:
        return 'positive'
    elif polarity < 0:
        return 'negative'
    else:
        return 'neutral'

def load_posts_from_file():
    """Load forum posts from a file."""
    try:
        with open(POSTS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.route('/get-daily-tip')
def get_daily_tip():
    # Randomly select a tip from the list
    selected_tip = random.choice(tips)
    return jsonify({'tip': selected_tip})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create-thread', methods=['POST'])
def create_thread():
    data = request.get_json()
    title = data.get('title')  # This will safely return None if 'title' is not present
    category = data.get('category')
    content = data.get('content')

    if not title or not category or not content:
        return jsonify({'error': 'Missing required fields'}), 400

    # Proceed with thread creation logic (e.g., save to database)
    return jsonify({'success': 'Thread created successfully!'})


@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(f"{username} has joined the room.", to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(f"{username} has left the room.", to=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    message = data['message']
    send(message, to=room)

@app.route('/')
def home():
    """
    Render the main page with links to both the chatbot and forum.
    Pass the logged-in username (if any) and the updates list to the template.
    """
    # Get the logged-in username from the session
    username = session.get('username', None)

    # Load updates from the JSON file
    with open('updates.json') as f:
        updates = json.load(f)

    # Render the homepage and pass both username and updates data to the template
    return render_template('home.html', username=username, updates=updates)

@app.route('/content-creation', methods=['GET'])
def content_creation():
    return render_template('content_creation.html')

@app.route('/careers')
def careers():
    return render_template('careers.html')  # Make sure the HTML file is in a "templates" folder

@app.route('/submit-application', methods=['POST'])
def submit_application():
    # Extract data from the form submission
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')
    job_title = request.form.get('job_title')

    if not (name and email and message and job_title):
        return render_template("error.html", error="All fields are required!"), 400

    # Structure the application data
    application_data = {
        "name": name,
        "email": email,
        "message": message,
        "job_title": job_title
    }

    # Load existing applications from the JSON file
    with open(APPLICATIONS_FILE, "r") as file:
        applications = json.load(file)

    # Append the new application
    applications.append(application_data)

    # Save the updated applications list back to the JSON file
    with open(APPLICATIONS_FILE, "w") as file:
        json.dump(applications, file, indent=4)

    # Render the thank you page
    return render_template("thank_you2.html", name=name, job_title=job_title)

@app.route('/login', methods=['GET', 'POST'])
def login():
    load_users_db()  # Load users before checking login
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists
        if username not in users_db:
            return render_template('username_not_found.html')  # If username not found, show error

        # Validate the password
        if users_db.get(username) == password:
            session['username'] = username
            return redirect(url_for('home'))  # Redirect to the chatbot route
        else:
            # Redirect to the Forgot Password page if the password is incorrect
            return redirect(url_for('forgot_password', username=username))  # Pass username to reset password page

    return render_template('login.html')


@app.route('/profile', methods=['GET'])
def profile():
    # Load the updated profile data (including profile picture) from wherever it's stored (e.g., session, file, etc.)
    profile_data = load_user_profile()  # Make sure this function loads the latest data

    # Retrieve the profile picture URL (if available)
    profile_picture = profile_data.get('profile_picture', None)

    # Return the profile page with the updated profile data, including the profile picture
    return render_template('profile.html', 
                           username=profile_data.get('username', ''),
                           bio=profile_data.get('bio', ''),
                           profile_picture=profile_picture)

@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/community-projects')
def community_projects():
    return render_template('community_projects.html')

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Prepare the message data
    contact_data = {
        'name': name,
        'email': email,
        'message': message
    }

    # Read existing contact messages from the file
    try:
        with open(CONTACT_MESSAGES_FILE, 'r') as file:
            messages = json.load(file)
            if not isinstance(messages, list):
                messages = []  # If it's not a list, reset it as an empty list
    except FileNotFoundError:
        messages = []  # Initialize as an empty list if the file doesn't exist

    # Add the new contact message to the list
    messages.append(contact_data)

    # Save the updated messages back to the file
    with open(CONTACT_MESSAGES_FILE, 'w') as file:
        json.dump(messages, file, indent=4)

    # Redirect to a thank-you page
    return redirect(url_for('thank_you'))

@app.route('/thank_you')
def thank_you():
    return render_template('thank_you.html')

@app.route('/ai-extension')
def ai_extension():
    # Logic for AI extension page or redirect
    return render_template('ai_extension.html')

@app.route('/code_playground')
def code_playground():
    return render_template('code_playground.html')

# Route for the App Download Page
@app.route('/download')
def download_page():
    return render_template('app-download.html')

# Route to view contact messages (Admin view or for debugging)
@app.route('/view_messages')
def view_messages():
    try:
        with open(CONTACT_MESSAGES_FILE, 'r') as file:
            messages = json.load(file)
            if not isinstance(messages, list):
                messages = []  # Reset if it's not a list
    except FileNotFoundError:
        messages = []

    # Render a template or return messages directly as JSON
    return render_template('view_messages.html', messages=messages)

@app.route('/forum')
def forum():
    username = session.get('username', None)

    # Load forum posts from the file
    with open('forum_posts.json', 'r') as f:
        forum_posts = json.load(f)

    # Pass the posts, username, and categories to the template
    return render_template('forum.html', username=username, categories=categories, forum_posts=forum_posts)

@app.route('/updates')
def updates():
    # Load updates from JSON file
    with open('updates.json', 'r') as file:
        updates = json.load(file)

    return render_template('update_lists.html', updates=updates)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    # Get the form data (username, bio, and profile picture)
    username = request.form.get('username')
    bio = request.form.get('bio')
    profile_picture = request.files.get('profile_picture')

    if not username or not bio:
        return "Missing username or bio", 400  # Handle missing fields

# Handle profile picture update (if available)
    profile_picture_url = None
    if profile_picture:
        if allowed_file(profile_picture.filename):  # Ensure it's a valid image
            filename = os.path.join(app.config['UPLOAD_FOLDER'], profile_picture.filename)
            profile_picture.save(filename)
            profile_picture_url = url_for('static', filename=f'uploads/{profile_picture.filename}')
        else:
            return "Invalid file type for profile picture", 400  # Handle invalid file type

    # Update the user profile data
    profile_data = {
        "username": username,
        "bio": bio,
        "profile_picture": profile_picture_url  # Include profile picture URL if uploaded
    }

    # Save the updated profile data (implement your own save logic here)
    save_user_profile(profile_data)

    # Redirect to the profile page with the updated data
    return redirect(url_for('profile'))

@app.route('/error-report', methods=['GET'])
def error_report():
    return render_template('error-report.html')  # Renders the error report page

@app.route('/submit-error', methods=['POST'])
def submit_error():
    error_description = request.form['error-description']
    email = request.form.get('email', '')  # Optional email field
    
    # Create a dictionary for the new error report
    error_report = {
        'error_description': error_description,
        'email': email,
        'timestamp': '2025-01-13T12:34:56'  # This is a placeholder timestamp, can be dynamically set
    }

    # Open the JSON file and append the new error report
    try:
        with open('error_reports.json', 'r') as f:
            data = json.load(f)  # Load existing data
    except FileNotFoundError:
        data = []  # If file does not exist, start with an empty list
    
    # Append the new error report to the list
    data.append(error_report)

    # Save the updated list back to the JSON file
    with open('error_reports.json', 'w') as f:
        json.dump(data, f, indent=4)

    # Redirect to a thank-you page
    return redirect(url_for('thank_you'))  # Redirect to thank you page or homepage

@app.route('/faq')
def faq():
    return render_template('faq.html')

@app.route('/customersupport')
def customer_support():
    return render_template('customersupport.html')  # Ensure this points to the correct template file

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('is_premium', None)
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        is_premium = 'is_premium' in request.form

        if username in users_db:
            return render_template('signup.html', error="Username already taken.")

        users_db[username] = {
            "password": generate_password_hash(password),
            "email": email,
            "is_premium": is_premium
        }
        save_json_file(users_file, users_db)
        return redirect(url_for('login'))

    return render_template('signup.html')

# Analytics data route
@app.route('/analytics-data')
def analytics_data():
    return read_analytics()


@app.route('/persona_chat')
def persona_chat():
    return render_template('persona_chat.html')

@app.route('/set_persona', methods=['POST'])
def set_persona():
    global current_persona
    data = request.get_json()
    current_persona = data['persona']
    return jsonify({'response': get_persona_greeting()})

# Route for /vibespace
@app.route('/vibespace')
def vibespace():
    return render_template('vibespace.html')

@app.route('/newsfeed')
def newsfeed():
    try:
        # Fetch news server-side
        response = requests.get(URL)
        response.raise_for_status()  # Raise exception for HTTP errors
        news_data = response.json()

        # Pass up to 10 articles to the template
        articles = news_data.get('articles', [])[:10]
        return render_template('newsfeed.html', articles=articles)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return render_template('newsfeed.html', articles=[])
# Route for the analytics page
@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

    # Define the route for the AI Research page
@app.route('/ai_research')
def ai_research():
    return render_template('ai_research.html')

@app.route('/ai-tutorial')
def ai_tutorial():
    return render_template('ai-tutorial.html')

@app.route('/get', methods=['POST'])
def get_bot_response():
    user_input = request.json.get('msg').lower()  # Get the user's message and convert to lowercase
    
    global current_game, game_data
    
    # Check for exit game command
    if "exit game" in user_input:
        current_game = None
        game_data = {}  # Clear any game-specific data
        return jsonify({'response': "You have exited the game. How can I assist you next?"})
    
    # Check for game-related commands
    if "trivia" in user_input:
        current_game = "trivia"
        return jsonify({'response': trivia_game()})
    elif "hangman" in user_input:
        current_game = "hangman"
        return jsonify({'response': hangman_game()})
    elif "story" in user_input:
        current_game = "story"
        return jsonify({'response': storytelling_game()})
    
    # Handle user input during game (trivia answer, hangman guess, story continuation)
    if current_game == "trivia":
        return jsonify({'response': handle_trivia_answer(user_input)})
    elif current_game == "hangman":
        return jsonify({'response': handle_hangman_guess(user_input)})
    elif current_game == "story":
        return jsonify({'response': handle_story_input(user_input)})

         # --- Analytics Update ---
    try:
        analytics = read_analytics()  # Get the current analytics data

        # Update message count
        analytics['messageCount'] += 1

        # Analyze sentiment and update the count
        sentiment = analyze_sentiment(user_input)
        analytics['sentiment'][sentiment] += 1

        # Save updated analytics
        update_analytics(analytics)
    except Exception as e:
        print(f"Error updating analytics: {e}")  # Debugging: print error if analytics update fails
    
    # Default AI response for non-game commands
    response = get_response(user_input)  # Use your AI response function here
    return jsonify({'response': response})

@app.route('/upgrade')
def upgrade():
    return render_template('upgrade.html')

@app.route('/ai-for-business')
def ai_for_business():
    return render_template('ai_for_business.html')

@app.route('/create-ai-character')
def create_ai_character():
    return render_template('create_ai_character.html')  # Make sure the HTML file is in the templates folder

# Route for the Building AI Guide page
@app.route('/building-ai-guide')
def building_ai_guide():
    return render_template('building-ai-guide.html')

@app.route('/code_review')
def code_review_page():
    return render_template('code_review.html')

@app.route('/review_code', methods=['POST'])
def review_code():
    # Retrieve the code submitted by the user
    code = request.json.get('code')

    # Save code temporarily in a file
    with open('temp_code.py', 'w') as f:
        f.write(code)

    # Create a string buffer to capture pylint output
    pylint_output = io.StringIO()

    # Run pylint (on the file we saved the code to)
    pylint_opts = ['temp_code.py']
    result = pylint.lint.Run(pylint_opts, do_exit=False, reporter=pylint.reporters.text.TextReporter(pylint_output))

    # Get the output generated by pylint
    pylint_result = pylint_output.getvalue()

    # If there's no pylint output, something went wrong
    if not pylint_result.strip():
        return jsonify({
            'error': 'No pylint output, please check your code format.'
        })

    # Check for errors, warnings, and suggestions in the pylint result
    errors = 0
    warnings = 0
    suggestions = 0

    # Check each line of output and categorize based on severity
    for line in pylint_result.splitlines():
        if 'error' in line.lower():  # Case insensitive check for 'error'
            errors += 1
        elif 'warning' in line.lower():  # Case insensitive check for 'warning'
            warnings += 1
        else:
            suggestions += 1

    # Send the analysis results back to the front-end
    return jsonify({
        'errors': errors,
        'warnings': warnings,
        'suggestions': suggestions,
        'pylint_output': pylint_result
    })

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    username = request.args.get('username')  # Get the username from the query parameter
    if request.method == 'POST':
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']

        # Check if the passwords match
        if new_password != confirm_password:
            error = "Passwords do not match. Please try again."
            return render_template('forgot_password.html', error=error, username=username)

        # Update the password in the users database
        users_db[username] = new_password

        # Save the updated users database
        with open('users_db.json', 'w') as f:
            json.dump(users_db, f)

        # Redirect to login page after password reset
        return redirect(url_for('login'))

    return render_template('forgot_password.html', username=username)


# Route for the Live Coding Sessions Page
@app.route('/live-coding-sessions')
def live_coding_sessions():
    return render_template('live_coding_sessions.html')

# Error handling for 404 (Page Not Found)
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    load_users_db()  # Load users before checking reset password
    if request.method == 'POST':
        username = request.form['username']
        new_password = request.form['new-password']
        confirm_password = request.form['confirm-password']

        # Check if the passwords match
        if new_password != confirm_password:
            error = "Passwords do not match. Please try again."
            return render_template('reset_password.html', error=error)

        # Check if the username exists in the users database
        if username not in users_db:
            error = "Username not found. Please try again."
            return render_template('reset_password.html', error=error)

        # Update the password for the user
        users_db[username] = new_password

        # Save the updated users database
        with open('users_db.json', 'w') as f:
            json.dump(users_db, f)

        # Log the user in after resetting the password
        session['username'] = username

        # Redirect to the chatbot page
        return redirect(url_for('chatbot'))

    return render_template('reset_password.html')

@app.route("/new_chat", methods=["POST"])
def new_chat():
    # Clear the conversation history to start a new chat
    session.pop('conversation', None)
    return jsonify({"response": "Starting a new chat. Feel free to ask me anything!"})

# Route to save the current chat
@app.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.get_json()
    chat = data.get('chat')

    if chat:
        # Save the chat into the list
        saved_chats.append({'chat': chat, 'time': '2024-12-28'})
        print(f"Chat saved: {chat}")  # Debugging line to see if the chat is saved
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'No chat data received'}), 400

@app.route('/forum/<group_name>')
def group_forum(group_name):
    group_posts = [post for post in forum_posts if post['group_name'] == group_name]
    return render_template('group_forum.html', group_name=group_name, posts=group_posts)

        # A route to get saved chats
@app.route('/saved_chats', methods=['GET'])
def get_saved_chats():
    return jsonify({'savedChats': saved_chats}), 200

@app.route('/feedback_form')
def feedback_form():
    return render_template('feedback_form.html')

@app.route('/chatbot_response_challenge')
def challenge():
    return render_template('chatbot_response_challenge.html')  # Your challenge page

# File path for storing challenge responses
responses_file = 'challenges_responses.json'

# Main games page route
@app.route('/games')
def games():
    return render_template('games.html')  # This will load the games HTML page

# Example routes for each individual game
@app.route('/games/adventure-quest')
def adventure_quest():
    return render_template('adventure_quest.html')  # Individual game page

@app.route('/social-media')
def social_media():
    return render_template('social_media.html')

@app.route('/games/battle-royale')
def battle_royale():
    return render_template('battle_royale.html')  # Individual game page

@app.route('/games/puzzle-mania')
def puzzle_mania():
    return render_template('puzzle_mania.html')  # Individual game page


@app.route('/collaboration')
def collaboration():
    return render_template('collaboration.html')

@app.route('/submit_proposal', methods=['POST'])
def submit_proposal():
    data = request.get_json()
    
    # Save the data to a JSON file
    with open('proposals.json', 'a') as file:
        json.dump(data, file)
        file.write("\n")  # Newline to separate each submission
    
    return jsonify({'status': 'success', 'message': 'Proposal submitted successfully!'})

@app.route('/games/racing-legends')
def racing_legends():
    return render_template('racing_legends.html')  # Individual game page

@app.route('/games/strategy-conqueror')
def strategy_conqueror():
    return render_template('strategy_conqueror.html')  # Individual game page

# Route to handle the challenge response submission
@app.route('/submit-challenge-response', methods=['POST'])
def submit_challenge_response():
    try:
        # Get the response data from the form submission
        response = request.json.get('response')

        if response:
            # Add the new response to the challenge responses list
            challenge_responses.append({"response": response})
            save_challenge_responses()
            return jsonify({"message": "Response submitted successfully!"}), 200
        else:
            return jsonify({"message": "No response provided!"}), 400
    except Exception as e:
        return jsonify({"message": f"Error submitting response! {str(e)}"}), 500


@app.route('/coding')
def coding():
    return render_template('coding.html')  # Ensure this is the correct file path for the coding page

@app.route('/code-library')
def code_library():
    return render_template('code_library.html')

@app.route('/privacy-terms')
def privacy_terms():
    return render_template('privacy-terms.html')  # This page will show the privacy and terms content

@app.route('/donate', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        donation_amount = request.form.get('donation_amount')
        payment_method = request.form.get('payment_method')
        
        # Render the donation confirmation page with the data
        return render_template('process_donation.html', 
                               donation_amount=donation_amount, 
                               payment_method=payment_method)
    
    # If it's a GET request, render the donation form
    return render_template('donation_form.html')

@app.route('/process_donation', methods=['POST'])
def process_donation():
    # Here, we're receiving the data passed from the donation form (POST method)
    donation_amount = request.form.get('donation_amount', '50')  # Default to $50 if not provided
    payment_method = request.form.get('payment_method', 'PayPal')  # Default to PayPal if not provided

    # Render the confirmation page with the donation data
    return render_template('process_donation.html', 
                           donation_amount=donation_amount, 
                           payment_method=payment_method)

@app.route('/ai_for_mental_health', methods=['GET'])
def ai_for_mental_health():
    return render_template('ai_for_mental_health.html')

# Route for the CBT page (CBT.html)
@app.route('/cbt')
def cbt():
    return render_template('CBT.html')

# Define the route for mindfulness and meditation
@app.route('/mindfulness_and_meditation')
def mindfulness_and_meditation():
    return render_template('mindfulness_and_meditation.html')

# Add this route for the Stress Relief Activities page
@app.route('/stress-relief')
def stress_relief():
    return render_template('stress_relief_activities.html')

# Define the route to display the volunteer form
@app.route('/volunteer', methods=['GET'])
def volunteer_form():
    return render_template('volunteer.html')  # Assuming your HTML file is named volunteer.html

@app.route('/submit-volunteer', methods=['POST'])
def submit_volunteer():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Data to be saved in JSON format
    volunteer_data = {
        'name': name,
        'email': email,
        'message': message
    }

    # Try to load existing data from the JSON file
    try:
        with open('volunteers.json', 'r') as file:
            existing_data = json.load(file)
            # Ensure the existing data is a list, or else reinitialize it
            if not isinstance(existing_data, list):
                existing_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file doesn't exist or is empty, create an empty list
        existing_data = []

    # Append the new volunteer data to the list
    existing_data.append(volunteer_data)

    # Write the updated data back to the file
    with open('volunteers.json', 'w') as file:
        json.dump(existing_data, file, indent=4)

    # Redirect to the volunteer dashboard
    return redirect(url_for('volunteer_dashboard'))

@app.route('/volunteer-dashboard', methods=['GET'])
def volunteer_dashboard():
    try:
        # Retrieve the volunteer data from the JSON file
        with open('volunteers.json', 'r') as file:
            volunteers = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        volunteers = []

    # Pass the data to the template
    return render_template('volunteer_dashboard.html', volunteers=volunteers)

# Route for Upcoming Events
@app.route('/upcoming-events')
def upcoming_events():
    return render_template('upcoming_event.html')

@app.route('/ai-tools')
def ai_tools():
    return render_template('ai_tools.html')  # assuming your HTML file is named ai_tools.html

@app.route('/leaderboard')
def leaderboard():
    # For simplicity, just return all responses as the "leaderboard"
    return jsonify(responses)

@app.route('/feedback', methods=['POST'])
def feedback():
    rating = request.form['rating']
    feedback_message = request.form['feedback']
    feedback_data = load_feedback()
    feedback_data.append({
        'rating': rating,
        'feedback': feedback_message
    })
    save_feedback(feedback_data)
    return redirect(url_for('chatbot'))  # Redirect to chatbot page after submission


    # Append new feedback
    feedback_data.append({
        'rating': rating,
        'feedback': feedback_message
    })

    # Save updated feedback data to the file
    save_feedback(feedback_data)

    return "Thank you for your feedback!"

if __name__ == "__main__":
    load_users_db()  # Load users before running the app
    app.run(debug=True)