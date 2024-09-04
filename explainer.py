# explainer.py

import asyncio
import logging
import os
import json
from datetime import datetime, timezone
from pptx import Presentation
from aiohttp import ClientSession
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.orm import Upload, User

from slides_explain.utils import fetch_slide_explanation, combine_slide_text

UPLOADS_FOLDER = 'uploads'
OUTPUTS_FOLDER = 'outputs'

LOGS_FOLDER = 'logs'
PROCESSING_LOG_FILE = os.path.join(LOGS_FOLDER, 'presentation_processing.log')

os.makedirs(LOGS_FOLDER, exist_ok=True)

# Configure logging for slide processing
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the overall logger level

# Create a file handler
file_handler = logging.FileHandler(PROCESSING_LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)  # Set file handler level to INFO

# Create a stream handler (for terminal output)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler.setLevel(logging.DEBUG)  # Set stream handler level to DEBUG

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Database setup
DATABASE_URL = "sqlite:///db/chinook.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


API_KEY = os.getenv("API_KEY")

# Other parts of the script remain the same

async def process_slide(slide, session):
    slide_text = combine_slide_text(slide)
    if slide_text:
        try:
            explanation = await fetch_slide_explanation(session, slide_text, API_KEY)
            return explanation
        except Exception as e:
            logger.error(f"Failed to process slide: {e}")
            return f"Failed to process slide: {e}"
    return None

async def process_new_uploads():
    logger.info("Slide processing script started.")

    while True:
        try:
            db = SessionLocal()
            pending_uploads = db.query(Upload).filter(Upload.status == 'pending').all()

            for upload in pending_uploads:
                pptx_path = os.path.join(UPLOADS_FOLDER, f"{upload.uid}.pptx")
                output_file = os.path.join(OUTPUTS_FOLDER, f"{upload.uid}.json")

                if os.path.exists(output_file):
                    continue  # Skip if already processed

                logger.info(f"Processing {upload.filename}...")
                prs = Presentation(pptx_path)
                tasks = []

                async with ClientSession() as session:
                    for slide in prs.slides:
                        task = process_slide(slide, session, "your_api_key_here")
                        tasks.append(task)

                    explanations = await asyncio.gather(*tasks)

                explanations = [exp if exp else "No text content" for exp in explanations]

                with open(output_file, 'w') as f:
                    json.dump(explanations, f, indent=4)

                upload.status = 'done'
                upload.finish_time = datetime.utcnow()

                db.add(upload)
                db.commit()

                logger.info(f"Processing {upload.filename} completed successfully.")

            db.close()
            await asyncio.sleep(10)  # Check for new uploads every 10 seconds

        except Exception as e:
            logger.error(f"Failed to fetch pending uploads: {e}")
            db.close()
            await asyncio.sleep(10)  # Retry after 10 seconds if an error occurred


if __name__ == '__main__':
    try:
        asyncio.run(process_new_uploads())
    except KeyboardInterrupt:
        logger.info("Slide processing script ended due to keyboard interrupt.")
    except Exception as e:
        logger.error(f"Slide processing script ended with error: {e}")
