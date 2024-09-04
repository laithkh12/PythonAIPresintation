import os
import json
import asyncio
from pptx import Presentation
from aiohttp import ClientSession
from slides_explain.utils import fetch_slide_explanation, combine_slide_text
import logging

logging.basicConfig(filename='presentation_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
async def process_slide(slide, session, api_key):
    slide_text = combine_slide_text(slide)
    if slide_text:
        try:
            explanation = await fetch_slide_explanation(session, slide_text, api_key)
            return explanation
        except Exception as e:
            logging.error(f"Failed to process slide: {e}")
            return f"Failed to process slide: {e}"
    return None

async def main(pptx_path, api_key):
    prs = Presentation(pptx_path)
    tasks = []

    async with ClientSession() as session:
        for slide in prs.slides:
            task = process_slide(slide, session, api_key)
            tasks.append(task)

        explanations = await asyncio.gather(*tasks)

    explanations = [exp if exp else "No text content" for exp in explanations]

    output_file = f"{os.path.splitext(pptx_path)[0]}.json"
    with open(output_file, 'w') as f:
        json.dump(explanations, f, indent=4)
    logging.info("Presentation processing completed successfully.")