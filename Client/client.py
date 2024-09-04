import sys
import requests


def upload_file(filepath, email=None):
    url = 'http://localhost:5000/upload'
    try:
        files = {'file': open(filepath, 'rb')}
        data = {'email': email} if email else {}

        response = requests.post(url, files=files, data=data)

        if response.status_code == 200:
            try:
                result = response.json()
                if 'uid' in result:
                    print(f"File uploaded successfully. UID: {result['uid']}")
                else:
                    print("File uploaded successfully.")
                    print("Server Response:", result)  # Print the entire response for debugging
            except ValueError:
                print("Invalid JSON received from server.")
                print("Server Response:", response.text)  # Print the entire response for debugging
        else:
            print(f"Failed to upload file. Status Code: {response.status_code}")
    except IOError as e:
        print(f"Error opening file: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")


def check_status(uid=None, email=None, filename=None):
    url = 'http://localhost:5000/status'
    params = {}
    if uid:
        params['uid'] = uid
    elif email and filename:
        params['email'] = email
        params['filename'] = filename
    else:
        print("Error: Please provide either UID or both email and filename.")
        return

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                result = response.json()
                print("Status:", result['status'])
                print("Filename:", result['filename'])
                print("Upload Time:", result['timestamp'])
                if result['finish_time']:
                    print("Finish Time:", result['finish_time'])
                if result['error_message']:
                    print("Error Message:", result['error_message'])
            except ValueError:
                print("Invalid JSON received from server.")
                print("Server Response:", response.text)  # Print the entire response for debugging
        else:
            print(f"Failed to check status. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

def get_history(email):
    url = 'http://localhost:5000/history'
    params = {'email': email}

    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                history = response.json()
                for upload in history:
                    print(f"UID: {upload['uid']}")
                    print(f"Filename: {upload['filename']}")
                    print(f"Upload Time: {upload['upload_time']}")
                    if upload['finish_time']:
                        print(f"Finish Time: {upload['finish_time']}")
                    print(f"Status: {upload['status']}")
                    if upload['error_message']:
                        print(f"Error Message: {upload['error_message']}")
                    print()
            except ValueError:
                print("Invalid JSON received from server.")
                print("Server Response:", response.text)  # Print the entire response for debugging
        else:
            print(f"Failed to retrieve history. Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide 'upload', 'status', 'history', or 'uid' followed by appropriate arguments.")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'uid':
        if len(sys.argv) < 3:
            print("Error: Please provide the UID.")
            sys.exit(1)
        uid = sys.argv[2]
        check_status(uid=uid)
    elif command == 'upload':
        if len(sys.argv) < 3:
            print("Error: Please provide the file path and optionally an email.")
            sys.exit(1)
        filepath = sys.argv[2]
        email = sys.argv[3] if len(sys.argv) > 3 else None
        upload_file(filepath, email)
    elif command == 'status':
        if len(sys.argv) < 4:
            print("Error: Please provide the UID or both email and filename.")
            sys.exit(1)
        uid = sys.argv[2]
        filename = sys.argv[3]
        check_status(uid=uid, filename=filename)
    elif command == 'history':
        if len(sys.argv) < 3:
            print("Error: Please provide an email to retrieve history.")
            sys.exit(1)
        email = sys.argv[2]
        get_history(email)
    else:
        print("Invalid command. Please use 'upload', 'status', 'history', or 'uid'.")
        sys.exit(1)
