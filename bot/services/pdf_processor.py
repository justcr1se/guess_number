import io
import logging
from dataclasses import dataclass

from pypdf import PdfReader
from pdf2image import convert_from_bytes
from PIL import Image

from bot.config import MAX_PAGES_PER_ANALYSIS

logger = logging.getLogger(__name__)

MIN_TEXT_LENGTH = 100
IMAGE_DPI = 200
JPEG_QUALITY = 85
MAX_IMAGE_DIMENSION = 2000


@dataclass
class ExtractedContent:
    text: str | None
    images: list[bytes]


def _compress_image(image: Image.Image) -> bytes:
    if image.mode != "RGB":
        image = image.convert("RGB")
    if max(image.size) > MAX_IMAGE_DIMENSION:
        image.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.LANCZOS)
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue()


def normalize_image_bytes(data: bytes) -> bytes:
    image = Image.open(io.BytesIO(data))
    return _compress_image(image)


def process_pdf(data: bytes) -> ExtractedContent:
    text = _extract_text(data)
    if text and len(text.strip()) >= MIN_TEXT_LENGTH:
        return ExtractedContent(text=text.strip(), images=[])

    logger.info("PDF text is short (%s chars), falling back to image conversion", len(text or ""))
    images = _pdf_to_images(data)
    return ExtractedContent(text=None, images=images)


def _extract_text(data: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = reader.pages[:MAX_PAGES_PER_ANALYSIS]
        chunks = []
        for page in pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception as exc:
                logger.warning("Failed to extract text from a PDF page: %s", exc)
        return "\n".join(chunks)
    except Exception as exc:
        logger.warning("pypdf failed to read document: %s", exc)
        return ""


def _pdf_to_images(data: bytes) -> list[bytes]:
    pil_images = convert_from_bytes(
        data,
        dpi=IMAGE_DPI,
        first_page=1,
        last_page=MAX_PAGES_PER_ANALYSIS,
    )
    return [_compress_image(img) for img in pil_images]
