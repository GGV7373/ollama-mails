import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import json
from ollama_client import OllamaClient
from file_parser import FileParser, cleanup_files

# Create app instance
app = FastAPI(title="AI Email Writer")

# Setup directories
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# File upload configuration
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB

# Initialize Ollama client
ollama_client = OllamaClient(model="mistral")

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
if static_dir.exists() and any(static_dir.iterdir()):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates_dir = Path("templates")
templates_dir.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve the main HTML page"""
    index_path = templates_dir / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return "<h1>Index page not found</h1>"


@app.post("/api/generate-email")
async def generate_email(
    context: str = Form(...),
    email_style: str = Form(default="professional"),
    file: UploadFile = File(None)
):
    """
    Generate an email based on context and optional file upload.

    Args:
        context: User-provided context for the email
        email_style: Style of the email
        file: Optional file for additional context

    Returns:
        Generated email and metadata
    """
    file_summaries = ""
    file_info = {"filename": "", "type": "", "status": ""}

    # Process uploaded file if provided
    if file and file.filename:
        try:
            # Check file type
            if not FileParser.is_allowed_file(file.filename):
                raise HTTPException(
                    status_code=400,
                    detail=f"File type not allowed. Allowed: {', '.join(FileParser.ALLOWED_EXTENSIONS)}"
                )

            # Save temporary file
            temp_path = UPLOAD_DIR / file.filename
            contents = await file.read()

            # Check file size
            if len(contents) > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail=f"File too large. Maximum size: 50MB"
                )

            # Write file
            with open(temp_path, "wb") as f:
                f.write(contents)

            # Parse file
            file_summaries, file_type = FileParser.parse_file(str(temp_path))
            file_info = {
                "filename": file.filename,
                "type": file_type,
                "status": "processed"
            }

            # Cleanup temporary file
            if temp_path.exists():
                temp_path.unlink()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing file: {str(e)}"
            )

    # Check Ollama connection
    if not ollama_client.check_connection():
        raise HTTPException(
            status_code=503,
            detail="Ollama is not running. Please start Ollama first (ollama serve)"
        )

    # Generate email
    generated_email = ollama_client.generate_email(
        context=context,
        email_style=email_style,
        file_summaries=file_summaries,
        temperature=0.7
    )

    return {
        "email": generated_email,
        "file_info": file_info,
        "style": email_style
    }


@app.post("/api/check-ollama")
async def check_ollama():
    """Check if Ollama is running and available"""
    is_available = ollama_client.check_connection()
    models = ollama_client.list_available_models() if is_available else []

    return {
        "available": is_available,
        "models": models,
        "default_model": ollama_client.model
    }


@app.post("/api/download-email")
async def download_email(email_content: str = Form(...)):
    """Download email as a text file"""
    import tempfile

    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt',
            delete=False,
            dir=UPLOAD_DIR
        ) as tmp:
            tmp.write(email_content)
            tmp_path = tmp.name

        # Send file
        return FileResponse(
            path=tmp_path,
            filename="email.txt",
            media_type="text/plain"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating file: {str(e)}"
        )


@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("AI Email Writer started!")
    print("Frontend: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")

    # Check Ollama connection
    is_available = ollama_client.check_connection()
    if not is_available:
        print("⚠️  WARNING: Ollama is not running!")
        print("Please start Ollama with: ollama serve")
    else:
        models = ollama_client.list_available_models()
        print(f"✓ Ollama is running with models: {', '.join(models)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    # Cleanup old uploaded files
    cleanup_files(str(UPLOAD_DIR), max_age_hours=1)
    print("AI Email Writer stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
