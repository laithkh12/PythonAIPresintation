# app.py

import os
import json
from flask import Flask, request, jsonify
from datetime import datetime, timezone
import uuid
import re
from loguru import logger
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.orm import User, Upload, Base
from werkzeug.utils import secure_filename
from email_validator import validate_email, EmailNotValidError

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the uploads, outputs, and logs folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

LOGS_FOLDER = 'logs'
FLASK_APP_LOGS_FOLDER = os.path.join(LOGS_FOLDER, 'flask_app')

# Ensure the folders exist
os.makedirs(FLASK_APP_LOGS_FOLDER, exist_ok=True)

# Configure logging with loguru
logger.add(os.path.join(FLASK_APP_LOGS_FOLDER, 'flask_app.log'), rotation='1 day', retention='5 days', level='DEBUG')

# Database setup
DATABASE_URL = "sqlite:///db/chinook.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Routes
@app.route('/history', methods=['GET'])
def get_history():
    try:
        logger.info("Starting get_history function...")

        email = request.args.get('email')

        if not email:
            return jsonify({'error': 'Email parameter is required'}), 400

        db = SessionLocal()
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        uploads = db.query(Upload).filter(Upload.user_id == user.id).all()

        history = []
        for upload in uploads:
            timestamp = upload.upload_time.replace(tzinfo=timezone.utc).isoformat()
            if upload.finish_time:
                finish_time = upload.finish_time.replace(tzinfo=timezone.utc).isoformat()
            else:
                finish_time = None

            upload_data = {
                'uid': upload.uid,
                'filename': upload.filename,
                'upload_time': timestamp,
                'finish_time': finish_time,
                'status': upload.status,
                'error_message': upload.error_message
            }
            history.append(upload_data)

        db.close()

        logger.info("History retrieved successfully.")
        return jsonify(history), 200
    except Exception as e:
        error_msg = f"Failed to get history: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': f"Failed to get history: {str(e)}"}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        logger.info("Starting upload_file function...")

        file = request.files.get('file')
        email = request.form.get('email')

        if not file:
            error_msg = 'No file provided in the request'
            logger.error(error_msg)
            return jsonify({'error': 'No file provided in the request'}), 400

        filename = secure_filename(file.filename)
        uid = str(uuid.uuid4())

        # Save file with only UID in filename
        new_filename = f"{uid}{os.path.splitext(filename)[1]}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))

        # Validate email if provided
        if email:
            try:
                # Validate email format
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError as e:
                logger.error(f"Invalid email provided: {str(e)}")
                return jsonify({'error': 'Invalid email provided'}), 400

        # Save upload details to database
        db = SessionLocal()
        upload = Upload(filename=filename, uid=uid)

        if email:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(email=email)
                db.add(user)
            upload.user = user

        db.add(upload)
        db.commit()
        db.close()

        logger.info("File uploaded successfully.")
        return jsonify({'uid': uid, 'status': 'File uploaded successfully'}), 200
    except Exception as e:
        error_msg = f"Failed to upload file: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': f"Failed to upload file: {str(e)}"}), 500



@app.route('/status', methods=['GET'])
def get_status():
    try:
        logger.info("Starting get_status function...")

        uid = request.args.get('uid')
        email = request.args.get('email')
        filename = request.args.get('filename')

        db = SessionLocal()

        if uid:
            upload = db.query(Upload).filter(Upload.uid == uid).first()
        elif email and filename:
            user = db.query(User).filter(User.email == email).first()
            if user:
                upload = db.query(Upload).filter(Upload.user_id == user.id, Upload.filename == filename).order_by(
                    Upload.upload_time.desc()).first()
            else:
                upload = None
        else:
            return jsonify({'error': 'Invalid parameters provided'}), 400

        if not upload:
            return jsonify({'status': 'not found', 'filename': None, 'timestamp': "Timestamp not found",
                            'explanation': 'No upload exists with the given parameters'}), 404

        timestamp = upload.upload_time.replace(tzinfo=timezone.utc).isoformat()
        if upload.finish_time:
            finish_time = upload.finish_time.replace(tzinfo=timezone.utc).isoformat()
        else:
            finish_time = None

        response = {
            'status': upload.status,
            'filename': upload.filename,
            'timestamp': timestamp,
            'finish_time': finish_time,
            'error_message': upload.error_message
        }

        db.close()

        logger.info("Status retrieved successfully.")
        return jsonify(response), 200
    except Exception as e:
        error_msg = f"Failed to get status: {str(e)}"
        logger.error(error_msg)
        return jsonify({'error': f"Failed to get status: {str(e)}"}), 500


if __name__ == '__main__':
    logger.info("Flask app started.")
    app.run(debug=True, use_reloader=False)