from flask import Flask, jsonify, Response, stream_with_context, request, session
import threading
import time
import cv2
import numpy as np
import json
import logging
import base64
import boto3
import cv2
import io
import time
import threading
from botocore.exceptions import ClientError
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.config['SECRET_KEY'] = "w?bZ+$f}]sA?k4A"
CORS(app) 

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens, system):

    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
             "messages": messages,
             "system": system
        }
    )

    response = bedrock_runtime.invoke_model_with_response_stream(
        body=body, modelId=model_id)

    return response


def send_snapshot(images):
    try:
        bedrock_runtime = boto3.client(service_name='bedrock-runtime')
        model_id = 'anthropic.claude-3-sonnet-20240229-v1:0'
        max_tokens = 128
        # system = "You are narrating a cohesive story about the journey through diverse landscapes, each image reveals the next chapter. Your narration should link each scene to the next, maintaining the flow of the overarching narrative. Think of each image as a continuation of the story, capturing the essence and emotion of the journey, in the style of Morgan Freeman, but do not mention the word 'image' in your narrations"
        system = "Imagine each image in this sequence as a frame in a cinematic journey, blending seamlessly into a single, flowing narrative that unfolds like a movie. Your task is to weave these still moments together into a vibrant tapestry of action, emotion, and transition, capturing the essence of a film. Delve into the depth of each scene to unveil the storyline, character evolution, and the scenic progression as if it's a continuous shot in a film. Explore the relationships, dynamics, and transformations that bridge these snapshots into a unified cinematic experience. Reflect on the underlying themes, emotions, and messages that emerge from viewing the sequence as a whole, offering a narrative that transcends the sum of its parts."

        content = []

        for image in images:
            _, buffer = cv2.imencode('.jpeg', image)
            io_buf = io.BytesIO(buffer)
            encoded_image = base64.b64encode(io_buf.getvalue()).decode('utf-8')
            image_content = {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": encoded_image
                }
            }
            content.append(image_content)

        message = {
            "role": "user",
            "content": content
        }

        messages = [message]

        response = run_multi_modal_prompt(bedrock_runtime, model_id, messages, max_tokens, system)
        return stream_extract_text(response)

    except ClientError as err:
        logger.error("A client error occurred: %s", err.response["Error"]["Message"])


def stream_extract_text(response):
    textResp = ''
    for event in response.get("body"):
        chunk = json.loads(event["chunk"]["bytes"])

        if chunk['type'] == 'message_delta':
            print(f"\nStop reason: {chunk['delta']['stop_reason']}")
            print(f"Stop sequence: {chunk['delta']['stop_sequence']}")
            print(f"Output tokens: {chunk['usage']['output_tokens']}")

        if chunk['type'] == 'content_block_delta':
            if chunk['delta']['type'] == 'text_delta':
                print(chunk['delta']['text'], end="")
                textResp += chunk['delta']['text'] + ""
    
    # Return the list of extracted text values
    return textResp

def synthesize_speech(text):
    polly_client = boto3.client('polly')

    """Synthesize speech from text using Amazon Polly and return audio stream."""
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',  # MP3 format
        VoiceId='Joanna'  # Choose a voice
    )
    # Get the audio stream from the response
    if "AudioStream" in response:
        audio_stream = response['AudioStream'].read()
        return audio_stream
    else:
        return None


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserSessionControl')



class ClientDataHandler:
    def __init__(self):
        self.data = {}
    
    def set_description(self, client_id, description):
        if client_id not in self.data:
            self.data[client_id] = {}
        self.data[client_id]['description'] = description
        session_id = session.get('sessionId') or request.args.get('sessionId')
        user_id = session.get('userId') or request.args.get('userId')
        table.put_item(
            Item={
                'sessionId': session_id,
                'userId': user_id,
                'description': description,
            }
        )
    def get_description(self, client_id):
        return self.data.get(client_id, {}).get('description', '')
    
    def set_audio_path(self, client_id, audio_path):
        if client_id not in self.data:
            self.data[client_id] = {}
        self.data[client_id]['audio_path'] = audio_path
    
    def get_audio_path(self, client_id):
        return self.data.get(client_id, {}).get('audio_path', '')
    

    def delete_description(self, client_id):
        # This method removes the description and optionally other data for a given client_id
        if client_id in self.data:
            del self.data[client_id]['description']  # Delete the description
            # Optionally delete or handle audio file cleanup here
            audio_path = self.data[client_id].get('audio_path')
            # if audio_path and os.path.exists(audio_path):
            #     os.remove(audio_path)  # Delete the audio file if it exists
            
            
    def cleanup(self, client_id):
        # Optional: Implement cleanup logic for client data
        pass
        del self.data[client_id]  # Remove the client's data from the dictionary

data_handler = ClientDataHandler()

@app.route('/get-description', methods=['GET'])
def get_description():
    client_id = request.args.get('client_id')
    description = data_handler.get_description(client_id)
    #data_handler.delete_description(client_id)
    return jsonify({"description": description})

@app.route('/get-audio', methods=['GET'])
def get_audio():
    # client_id = request.args.get('client_id')
    # audio_path = data_handler.get_audio_path(client_id)
    # if audio_path and os.path.exists(audio_path):
    #     return send_file(audio_path, as_attachment=True)
    # else:
    #     return jsonify({"error": "Audio file not found"}), 404

    client_id = request.args.get('client_id')
    description = data_handler.get_description(client_id)
    
    if not description:
        return jsonify({"error": "Description not found"}), 404
    
    # def generate_audio_stream():
    #     # Call Amazon Polly to synthesize speech from the text description
    #     response = polly_client.synthesize_speech(
    #         Text=description,
    #         OutputFormat='mp3',
    #         VoiceId='Joanna'  # Or any other voice ID
    #     )
        
        # if "AudioStream" in response:
        #     for chunk in response['AudioStream']:
        #         yield chunk
        # else:
        #     yield b""
    data_handler.delete_description(client_id)
    # return Response(generate_audio_stream(), mimetype='audio/mp3')
    return Response(synthesize_speech(description), mimetype='audio/mp3')

@app.route('/start-capture', methods=['POST'])
def start_capture():
    #client_id = request.args.get('client_id')
    client_id = request.form['client_id']
    
    snapshot_list = []
    for file_key in request.files:
        file = request.files[file_key]  # Access each file
        in_memory_file = io.BytesIO(file.read())  # Read file content into an in-memory file
        data = np.frombuffer(in_memory_file.getvalue(), dtype=np.uint8)
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
        snapshot_list.append(image)

    description = send_snapshot(snapshot_list)  # Pass the list of images
    snapshot_list.clear() 

    if description:
        data_handler.set_description(client_id, description)
        #audio_stream = synthesize_speech(description)

    return jsonify({"message": "Frames received", "client_id": client_id}), 200

    # thread = threading.Thread(target=capture_and_process, args=(client_id,))
    # thread.start()
    # return jsonify({"message": "Capture started"}), 200

# def capture_and_process(client_id):
#     # Initialize video capture here
#     cap = cv2.VideoCapture(0)  # Assuming the first webcam
#     snapshot_list = []
#     try:
#         for _ in range(7):  # Capture 7 snapshots
#             time.sleep(2)  # Interval between snapshots
            
#             success, frame = cap.read()
#             if success:
#                 snapshot_list.append(frame)

#         description = send_snapshot(snapshot_list)  # Pass the list of images
#         snapshot_list.clear() 

#         if description:
#             data_handler.set_description(client_id, description)
#             audio_stream = synthesize_speech(description)

#     finally:
#         cap.release()  # release the camera

# def generate_video_stream():
#     cap = cv2.VideoCapture(0)  # Capture video from camera
#     while True:
#         success, frame = cap.read()
#         if not success:
#             break
#         ret, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(stream_with_context(generate_video_stream()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/health')
def healthcheck():
    return "OK", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
