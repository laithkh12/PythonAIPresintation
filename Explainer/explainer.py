import os
import json
import asyncio
from pptx import Presentation
from aiohttp import ClientSession
from slides_explain.utils import fetch_slide_explanation, combine_slide_text
import logging
from logging.handlers import TimedRotatingFileHandler

UPLOADS_FOLDER = 'uploads'
OUTPUTS_FOLDER = 'outputs'

LOGS_FOLDER = 'logs'
PROCESSING_LOG_FILE = os.path.join(LOGS_FOLDER, 'presentation_processing.log')

os.makedirs(LOGS_FOLDER, exist_ok=True)

# Configure logging for slide processing
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set the overall logger level

# Create a file handler
file_handler = TimedRotatingFileHandler(PROCESSING_LOG_FILE, when='midnight', interval=1, backupCount=5)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_handler.setLevel(logging.INFO)  # Set file handler level to INFO

# Create a stream handler (for terminal output)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
stream_handler.setLevel(logging.DEBUG)  # Set stream handler level to DEBUG

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


async def process_slide(slide, session, api_key):
    slide_text = combine_slide_text(slide)
    if slide_text:
        try:
            explanation = await fetch_slide_explanation(session, slide_text, api_key)
            return explanation
        except Exception as e:
            logger.error(f"Failed to process slide: {e}")
            return f"Failed to process slide: {e}"
    return None


async def process_new_uploads():
    logger.info("Slide processing script started.")

    while True:
        for filename in os.listdir(UPLOADS_FOLDER):
            if filename.endswith('.pptx'):
                pptx_path = os.path.join(UPLOADS_FOLDER, filename)
                output_file = os.path.join(OUTPUTS_FOLDER, f"{os.path.splitext(filename)[0]}.json")

                if os.path.exists(output_file):
                    continue  # Skip if already processed

                logger.info(f"Processing {filename}...")
                prs = Presentation(pptx_path)
                tasks = []

                async with ClientSession() as session:
                    for slide in prs.slides:
                        task = process_slide(slide, session, "key")
                        tasks.append(task)

                    explanations = await asyncio.gather(*tasks)

                explanations = [exp if exp else "No text content" for exp in explanations]

                with open(output_file, 'w') as f:
                    json.dump(explanations, f, indent=4)
                logger.info(f"Processing {filename} completed successfully.")

        await asyncio.sleep(10)  # Check for new uploads every 10 seconds


if __name__ == '__main__':
    try:
        asyncio.run(process_new_uploads())
    except KeyboardInterrupt:
        logger.info("Slide processing script ended due to keyboard interrupt.")
    except Exception as e:
        logger.error(f"Slide processing script ended with error: {e}")
