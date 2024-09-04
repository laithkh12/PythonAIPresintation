from aiohttp import ClientSession, ClientTimeout
import logging

logging.basicConfig(filename='presentation_processing.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

async def fetch_slide_explanation(session: ClientSession, slide_text: str, api_key: str) -> str:
    prompt = f"Provide a concise explanation of the slide's content: {slide_text}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }
    timeout = ClientTimeout(total=10)
    async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data,
                            timeout=timeout) as response:
        try:
            result = await response.json()
            if 'choices' in result:
                return result['choices'][0]['message']['content']
            else:
                logging.error(f"Error in response: {result}")
                return f"Error in response: {result}"
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return f"Exception occurred: {e}"


def combine_slide_text(slide) -> str:
    slide_text = []
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            slide_text.append(shape.text.strip())
    return " ".join(slide_text).replace('\n', ' ').replace('\r', '') if slide_text else None