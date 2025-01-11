# AI Group Forum

A forum application for people in Mathworks to chat and share topics about AI.

## Features

- User authentication (signup, login, logout)
- Create, read, update, and delete posts
- Comment on posts
- Markdown support for post content
- Responsive design

## Tech Stack

- FastAPI (Python web framework)
- MongoDB (Database)
- Bootstrap 5 (Frontend)
- Jinja2 (Template engine)

## Local Development

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env`:
   ```
   SECRET_KEY=your_secret_key
   MONGODB_URL=your_mongodb_atlas_url
   DB_NAME=forum_db
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Deployment to Heroku

1. Create a Heroku account and install the Heroku CLI
2. Login to Heroku:
   ```bash
   heroku login
   ```
3. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```
4. Set up environment variables on Heroku:
   ```bash
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set MONGODB_URL=your_mongodb_atlas_url
   heroku config:set DB_NAME=forum_db
   ```
5. Deploy to Heroku:
   ```bash
   git push heroku main
   ```

## Environment Variables

- `SECRET_KEY`: Secret key for JWT token generation
- `MONGODB_URL`: MongoDB Atlas connection URL
- `DB_NAME`: MongoDB database name

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request
