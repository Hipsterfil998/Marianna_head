# Marianna API

Welcome to the Marianna API documentation. This API allows you to interact with a system for speech recognition, information retrieval, and text-to-speech synthesis, all focused on Naples' cultural heritage.

## 1. API Access

### Base Address

The API is accessible via HTTP at the following address:

http://<SERVER_IP_ADDRESS>:8080

Replace `<SERVER_IP_ADDRESS>` with the actual IP address of the server where the API is running.

### Authentication

All API endpoints require HTTP Basic authentication.  
You'll need to provide a valid username and password with each request.

Example: `-u "your_username:your_password"`

## 2. Available Endpoints

The API offers the following endpoints:

### 2.1. `/health` (GET) - Status Check

This endpoint is used to verify if the API is active and responding correctly.

- **Purpose**: Check the API's status.
- **Method**: GET
- **curl Command Example**:

```bash
curl -u "your_username:your_password" http://<SERVER_IP_ADDRESS>:8080/health
```

**Expected Success Response:**

```bash
{"status": "healthy"}
```


### 2.2. `/text_response` (POST) - Get text output

This endpoint accepts text as input and searches for a related summary from the internal knowledge base.

- **Purpose**: Submit a text query to get a relevant summary.
- **Method**: POST
- **Content Type**: `application/json`
- **Request Body (JSON)**:

```json
{
  "text": "Your text query here."
}
```

#### curl Command Example

```bash
curl -X POST \
  -u "your_username:your_password" \
  -H "Content-Type: application/json" \
  -d '{"text": "What'\''s the history of Castel dell'\''Ovo?"}' \
  http://<SERVER_IP_ADDRESS>:8080/text_response
```



### 2.3. `/audio_from_text` (POST) - Audio Generation from Text

This endpoint converts a provided text string into a WAV audio file using text-to-speech (TTS) synthesis.

- **Purpose**: Convert text into audio.
- **Method**: POST
- **Content Type**: `application/json`
- **Request Body (JSON)**:

```bash
curl -X POST \
  -u "your_username:your_password" \
  -H "Content-Type: application/json" \
  -d '{"text": "Welcome to the Napoli Heritage API. We hope you find our services useful."}' \
  http://<SERVER_IP_ADDRESS>:8080/audio_from_text \
  --output welcome_audio.wav
```


### 2.4. `/pipeline_audio` (POST) - Audio Transcription, Summary, and Audio Response

This is the primary integrated endpoint: it receives a WAV audio file, transcribes it, searches for a summary in the knowledge base, and if found, generates an audio response file with the summary.

- **Purpose**: Process a voice request (audio), get a summary, and receive its audio version.
- **Method**: POST
- **Content Type**: `multipart/form-data` (for file upload)
- **Input Format**: `.wav` file
- **Output Format**: `.wav` file
- **curl Command Example**:

```bash
curl -X POST \
  -u "your_username:your_password" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/input_audio.wav" \
  http://<SERVER_IP_ADDRESS>:8080/pipeline_audio \
  --output response_audio.wav -v
```

- **Notes**:
  - Replace `@/path/to/your/input_audio.wav` with the actual path to your local WAV audio file.
  - The `--output response_audio.wav` flag saves the generated audio file.
  - The `-v` (verbose) flag is recommended, as it will show the response headers. These headers (`X-Transcription` and `X-Summary`) contain the text transcription of your audio and the textual summary found, even though the main response is an audio file.

