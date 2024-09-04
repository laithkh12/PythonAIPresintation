import os
import pytest
import subprocess
import requests
import time

from slides_explain.main import main

UPLOADS_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
OUTPUTS_FOLDER = os.path.join(os.path.dirname(__file__), 'outputs')

os.makedirs(UPLOADS_FOLDER, exist_ok=True)
os.makedirs(OUTPUTS_FOLDER, exist_ok=True)

@pytest.fixture(scope='module')
def web_api():
    print("Starting Web API...")
    app_path = os.path.join(os.path.dirname(__file__), '..', 'web_API', 'app.py')
    process = subprocess.Popen(['python', app_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    yield
    print("Stopping Web API...")
    process.terminate()
    process.wait()

@pytest.fixture(scope='module')
def explainer():
    print("Starting Explainer...")
    explainer_path = os.path.join(os.path.dirname(__file__), '..', 'Explainer', 'explainer.py')
    process = subprocess.Popen(['python', explainer_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5)
    yield
    print("Stopping Explainer...")
    process.terminate()
    process.wait()

@pytest.mark.asyncio
async def test_pptx_explaining():
    pptx_path = r"C:\Users\leth1\PycharmProjects\hw5\logging, debugging, getting into a large codebase.pptx"


    api_key = "key"
    assert api_key is not None, "API key is not set"

    await main(pptx_path, api_key)

    output_file = f"{os.path.splitext(pptx_path)[0]}.json"

    assert os.path.exists(output_file), f"{output_file} does not exist"

    os.remove(output_file)

@pytest.mark.asyncio
async def test_end_to_end(web_api, explainer):
    filepath = r"C:\Users\leth1\PycharmProjects\hw5\logging, debugging, getting into a large codebase.pptx"
    url = 'http://localhost:5000/upload'

    try:
        files = {'file': open(filepath, 'rb')}
        response = requests.post(url, files=files)

        assert response.status_code == 200, f"Failed to upload file: {response.text}"
        result = response.json()
        assert 'uid' in result
        uid = result['uid']
        status_url = f'http://localhost:5000/status?uid={uid}'
        retries = 10
        retry_delay = 10
        for attempt in range(retries):
            try:
                response = requests.get(status_url)
                if response.status_code == 200:
                    status = response.json()
                    if status['status'] == 'done':
                        assert 'explanation' in status
                        assert status['explanation'] is not None
                        print(f"Processing complete after {attempt+1} attempts.")
                        break
                    elif status['status'] == 'pending':
                        print(f"Attempt {attempt+1}: Status is pending, retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)

                    else:
                        print(f"Unexpected status: {status['status']}")
                        time.sleep(retry_delay)

                else:
                    print(f"Failed to get status. Status code: {response.status_code}")
                    time.sleep(retry_delay)

            except requests.RequestException as e:
                print(f"Request failed: {e}")
                time.sleep(retry_delay)
        else:
            pytest.fail(f"Max retries exceeded ({retries}) while checking status")
    finally:
        print("Cleaning up or finalizing resources...")
