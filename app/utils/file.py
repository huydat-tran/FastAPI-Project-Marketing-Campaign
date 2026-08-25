from pathlib import Path

UPLOAD_DIR = Path("uploads/task_attachments")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
}


def validate_file(filename: str, file_size: int) -> None:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Unsupported file type")

    if file_size > MAX_FILE_SIZE:
        raise ValueError("File size must not exceed 10 MB")
