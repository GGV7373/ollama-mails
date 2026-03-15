import os
from pathlib import Path
from typing import Tuple
import pypdf

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False

class FileParser:
    """Parser for extracting text from various file types"""

    ALLOWED_EXTENSIONS = {'.pdf', '.mp3', '.wav', '.m4a', '.ogg'}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

    @staticmethod
    def is_allowed_file(filename: str) -> bool:
        """Check if file type is allowed"""
        return Path(filename).suffix.lower() in FileParser.ALLOWED_EXTENSIONS

    @staticmethod
    def parse_file(file_path: str) -> Tuple[str, str]:
        """
        Parse a file and extract text.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (text_content, file_type)
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        if not file_path.exists():
            return f"Error: File not found", "error"

        # Check file size
        if file_path.stat().st_size > FileParser.MAX_FILE_SIZE:
            return f"Error: File too large (max 50MB)", "error"

        if file_ext == '.pdf':
            return FileParser._parse_pdf(str(file_path)), "pdf"
        elif file_ext in {'.mp3', '.wav', '.m4a', '.ogg'}:
            return FileParser._parse_audio(str(file_path)), "audio"
        else:
            return f"Error: Unsupported file type '{file_ext}'", "error"

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        try:
            text = []
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = pypdf.PdfReader(pdf_file)

                if len(pdf_reader.pages) == 0:
                    return "Error: PDF file is empty"

                # Limit to first 50 pages to avoid huge context
                pages_to_read = min(len(pdf_reader.pages), 50)

                for page_num in range(pages_to_read):
                    page = pdf_reader.pages[page_num]
                    text.append(page.extract_text())

                content = "\n".join(text)

                if not content.strip():
                    return "Error: Could not extract text from PDF"

                # Limit content length
                max_content = 5000  # ~1250 words
                if len(content) > max_content:
                    content = content[:max_content] + "...[PDF truncated]"

                return content

        except Exception as e:
            return f"Error parsing PDF: {str(e)}"

    @staticmethod
    def _parse_audio(file_path: str) -> str:
        """Transcribe audio file using Whisper"""
        if not WHISPER_AVAILABLE:
            return "Error: Whisper not installed. Install with: pip install openai-whisper"

        try:
            # Validate file exists and has content
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return "Error: Audio file not found"

            if file_path_obj.stat().st_size == 0:
                return "Error: Audio file is empty"

            print(f"Transcribing audio: {file_path}")

            try:
                model = whisper.load_model("base")
            except Exception as e:
                return f"Error: Failed to load Whisper model: {str(e)}"

            try:
                result = model.transcribe(file_path)
            except Exception as e:
                return f"Error: Transcription failed (ensure file is valid audio): {str(e)}"

            text = result.get("text", "").strip()

            if not text:
                return "Error: No speech detected in audio file"

            # Limit content length
            max_content = 3000  # ~750 words
            if len(text) > max_content:
                text = text[:max_content] + "...[Audio truncated]"

            return text

        except Exception as e:
            return f"Error: Unexpected error processing audio: {str(e)}"


def cleanup_files(uploads_dir: str, max_age_hours: int = 24):
    """
    Clean up old uploaded files.

    Args:
        uploads_dir: Directory containing uploads
        max_age_hours: Delete files older than this many hours
    """
    import time
    current_time = time.time()
    try:
        for file_path in Path(uploads_dir).glob("*"):
            if file_path.is_file():
                file_age_hours = (current_time - file_path.stat().st_mtime) / 3600
                if file_age_hours > max_age_hours:
                    file_path.unlink()
    except Exception as e:
        print(f"Error cleaning up files: {e}")
