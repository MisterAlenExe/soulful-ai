# Soulful AI

Soulful AI is a Django-based web application that leverages the power of OpenAI's ChatGPT 3.5 Turbo to provide instant responses and support to users dealing with mental health issues. The application enables users to engage in chat-like conversations with the language model, creating chat rooms and changing topics seamlessly.

## Features

- **Instant Responses**: Utilize the capabilities of ChatGPT 3.5 Turbo for generating quick and helpful answers.
- **Chat Rooms**: Users can seamlessly engage in chat-like conversations, exploring various topics within the application.

## Installation

1. Clone the repository:
   ```bash
   git clone
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   venv/bin/activate
   ```
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Set up your Django project settings, including database configurations and secret key.
2. Create a `.env` file in the project root and add any necessary environment variables.
   ```env
   SECRET_KEY=your_secret_key
   OPENAI_API_KEY=your_openai_api_key
   ```

## Usage

1. Run the Django development server:
   ```bash
   python manage.py runserver
   ```
2. Access the application in your web browser at http://localhost:8000.
3. Engage in chat-like conversations, exploring various topics within the application.
