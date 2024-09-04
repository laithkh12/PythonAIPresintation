import argparse
import os
import asyncio
import logging
from slides_explain.main import main


logging.basicConfig(filename='presentation_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
def cli():
    parser = argparse.ArgumentParser(description="Summarize the PowerPoint presentation, explaining its main points.")
    parser.add_argument('pptx_path', type=str, help="The path to the PowerPoint presentation file.")
    args = parser.parse_args()

    pptx_path = args.pptx_path
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        logging.error("Error: Please set the OPENAI_API_KEY environment variable.")
        print("Error: Please set the OPENAI_API_KEY environment variable.")
        return
    logging.info("Processing presentation...")
    asyncio.run(main(pptx_path, api_key))