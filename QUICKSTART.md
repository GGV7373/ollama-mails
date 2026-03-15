# Quick Start Guide

## 30 Seconds to Email Generation

### 1. Install Ollama
Download from [ollama.com](https://ollama.com) and install

### 2. Start Ollama
```bash
ollama serve
```
(Leave this terminal running)

### 3. Pull a Model (in another terminal)
```bash
ollama pull mistral
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the App
```bash
python app.py
```

### 6. Open in Browser
Go to **http://localhost:8000**

---

## Using Docker (Optional)

```bash
docker-compose up
```

Then go to **http://localhost:8000**

---

## First Email

1. Write context: "Dear colleague, I need to schedule a meeting..."
2. Select style: "Professional"
3. Click "Generate Email"
4. Copy or download the result

That's it!

---

## Having Issues?

- **Can't connect to Ollama?** Make sure `ollama serve` is running
- **Model not found?** Run `ollama pull mistral`
- **Slow generation?** Try a smaller model: `ollama pull neural-chat`
- **Audio issues?** Install ffmpeg: `brew install ffmpeg` (macOS)

---

## Full Documentation

See `README.md` for complete documentation, configuration options, and advanced usage.
