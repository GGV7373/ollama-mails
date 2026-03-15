## AI Email Writer - Local AI-Powered Email Generation

Generate professional emails using a local AI model through Ollama. This is a simple, self-contained web application that runs entirely on your machine with no external API calls.

### Features

- **Local AI Processing** - Uses Ollama for completely private, offline email generation
- **File Upload Support** - Upload PDFs and audio files for additional context
- **Multiple Email Styles** - Professional, Casual, Short Reply, Business
- **Copy & Download** - Easy copying to clipboard or download as .txt
- **Simple Interface** - Clean, intuitive web UI with no heavy frameworks
- **Drag & Drop** - Drag files directly into the upload area
- **Word/Character Counter** - Track email length automatically

### Quick Start

#### Prerequisites

Before starting, you need to have **Ollama** installed and running on your machine.

1. **Install Ollama** from [ollama.ai](https://ollama.ai)
2. **Start Ollama** in your terminal:
   ```bash
   ollama serve
   ```
3. **Pull a model** (in another terminal):
   ```bash
   ollama pull mistral
   # or llama2, neural-chat, etc.
   ```

#### Option 1: Direct Python Setup (Recommended for development)

```bash
# Clone/navigate to the project
cd ai-email-writer

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Then open your browser to **http://localhost:8000**

#### Option 2: Docker Setup

```bash
# Build the Docker image
docker build -t ai-email-writer .

# Run the container (with Ollama running locally)
docker run -p 8000:8000 \
  --network host \
  ai-email-writer
```

Then open your browser to **http://localhost:8000**

### Usage

1. **Enter Context** - Write what you want the email to be about
2. **Select Style** - Choose from Professional, Casual, Short Reply, or Business
3. **Upload Files** (Optional) - Add PDF, MP3, WAV, M4A, or OGG files for additional context
4. **Generate** - Click "Generate Email" and wait for the AI response
5. **Copy or Download** - Copy to clipboard or download as a text file

#### Tips for Better Results

- Be specific and detailed in your context
- Mention the recipient and their role/company if relevant
- Include key points you want covered
- Upload relevant documents for additional context
- For audio context, use clear recordings

### Project Structure

```
ai-email-writer/
├── app.py                    # FastAPI backend
├── ollama_client.py          # Ollama API wrapper
├── file_parser.py            # PDF and audio processing
├── requirements.txt          # Python dependencies
├── Dockerfile                # Docker configuration
├── templates/
│   └── index.html           # Main web interface
├── static/
│   ├── style.css            # Styling
│   └── script.js            # Frontend logic
├── uploads/                  # Temporary file storage
└── README.md
```

### Configuration

**Model Selection**

The app uses `mistral` by default, but you can change it:

```python
# In app.py
ollama_client = OllamaClient(model="llama2")  # or any other Ollama model
```

Available models: `mistral`, `llama2`, `neural-chat`, `orca-mini`, and more

**Customization**

- **Temperature** (Creativity): Edit the temperature value in `app.py` (0.0 = deterministic, 1.0 = creative)
- **File Size Limits**: Adjust `MAX_FILE_SIZE` in `app.py` and `file_parser.py`
- **Port**: Change port in `app.py` (default: 8000)

### Supported File Types

| Type | Format | Use Case |
|------|--------|----------|
| PDF | `.pdf` | Documents, articles, reports |
| Audio | `.mp3, .wav, .m4a, .ogg` | Recordings, transcripts |

**File Processing:**
- PDFs: Text extraction (limited to first 50 pages)
- Audio: Automatic transcription using Whisper

### Privacy & Security

- All processing happens locally on your machine
- No data sent to external servers
- No API keys or credentials needed
- Uploaded files are temporarily stored then deleted

### System Requirements

- **Python**: 3.9+
- **RAM**: 8GB minimum (for Ollama model)
- **Disk**: 5-10GB (for Ollama model)
- **Ollama**: Latest version running locally

### Troubleshooting

#### "Ollama Disconnected" Error

**Solution**: Make sure Ollama is running
```bash
ollama serve
```

#### "Model not found" Error

**Solution**: Pull the model first
```bash
ollama pull mistral
ollama list  # View available models
```

#### Audio Transcription Issues

**Solution**: Ensure ffmpeg is installed
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (via choco)
choco install ffmpeg
```

#### Slow Generation

**Solution**: This is normal for large models. Performance depends on:
- Model size (smaller models are faster)
- Your hardware (GPU accelerates generation)
- Context size (longer inputs take longer)

Consider using a smaller model like `neural-chat`:
```bash
ollama pull neural-chat
```

### API Endpoints

#### POST `/api/generate-email`
Generate an email based on context and optional file

**Parameters:**
- `context` (string, required) - Email context
- `email_style` (string) - Style: professional, casual, short reply, business
- `file` (file, optional) - PDF or audio file

**Response:**
```json
{
  "email": "Generated email text...",
  "file_info": {
    "filename": "document.pdf",
    "type": "pdf",
    "status": "processed"
  },
  "style": "professional"
}
```

#### POST `/api/check-ollama`
Check if Ollama is running and list available models

**Response:**
```json
{
  "available": true,
  "models": ["mistral", "llama2"],
  "default_model": "mistral"
}
```

#### POST `/api/download-email`
Download generated email as text file

**Parameters:**
- `email_content` (string) - Email text to download

### Customizing Styles

To add new email styles, edit the `_build_prompt` method in `ollama_client.py`:

```python
style_instructions = {
    "professional": "...",
    "casual": "...",
    "your_style": "Write a [your style description]..."
}
```

### Performance Tips

1. **Use Smaller Models** - `neural-chat` is faster than `mistral`
2. **GPU Acceleration** - Ollama supports GPU if available
3. **Limit Context** - Shorter input = faster output
4. **Reduce Temperature** - Lower temperature = faster, more deterministic responses

### Deployment

**Local Development:**
```bash
python app.py
```

**Production with Docker:**
```bash
docker build -t ai-email-writer .
docker run -p 8000:8000 --network host ai-email-writer
```

**Behind Nginx (example):**
```nginx
server {
    listen 80;
    server_name email.local;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Contributing

Feel free to fork, modify, and improve this project. Some ideas:

- [ ] Email templates
- [ ] Batch processing
- [ ] Email history
- [ ] Custom prompts
- [ ] Multiple language support

### License

MIT License - Feel free to use and modify

### FAQ

**Q: Is my data sent to any server?**
A: No, everything runs locally. No data leaves your machine.

**Q: Can I use this with different AI models?**
A: Yes! Any Ollama-compatible model works. Just change the model name.

**Q: What if Ollama is running on a different machine?**
A: Edit the `OLLAMA_API_URL` in `ollama_client.py`:
```python
OLLAMA_API_URL = "http://192.168.1.100:11434/api/generate"
```

**Q: Can I use this in production?**
A: Yes, with proper security measures. Consider adding authentication and rate limiting.

**Q: How much RAM do I need?**
A: Depends on the model (3GB for small models, 16GB+ for large models)

### Tips & Tricks

- Use `Ctrl+Enter` to quickly generate an email
- Drag PDF files directly onto the upload area
- Click the status indicator to check Ollama connection
- The longer your context, the more detailed the email will be

---

**Made with care for local AI workflows**

Happy email writing!
