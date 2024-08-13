import cv2
import pytesseract
import requests
import json

def read_settings(file_path):
    settings = {}
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            settings[key] = value
    return settings

def main():
    settings = read_settings('settings.txt')
    
    api_ip = settings.get('API_IP', '127.0.0.1')
    api_port = settings.get('API_PORT', '5000')
    camera_device = settings.get('CAMERA_DEVICE', '/dev/video0')
    resolution = settings.get('RESOLUTION', '640x480')

    width, height = map(int, resolution.split('x'))
    
    api_url = f'http://{api_ip}:{api_port}/receive_text'
    
    # Initialize camera
    cap = cv2.VideoCapture(camera_device)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break

        # Convert image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Use Tesseract to detect text
        text = pytesseract.image_to_string(gray)

        if text.strip():
            print(f"Detected text: {text.strip()}")
            # Prepare JSON payload
            payload = {
                'text': text.strip()
            }
            try:
                # Send detected text to API
                response = requests.post(api_url, json=payload)
                print(f"API response: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data to API: {e}")

        # Display the frame (optional)
        cv2.imshow('Camera', frame)
        
        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()

