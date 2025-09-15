# messenger/scan.py is added for scanning uploaded PDF files
import logging
from pathlib import Path
from django.conf import settings
from django.db import transaction

from .models import UploadedPDF

logger = logging.getLogger(__name__)

def _is_valid_pdf_filename(name: str) -> bool:
    """Accept non-empty names ending with .pdf, ignore temp files."""
    if not name:
        return False
    n = name.lower()
    if not n.endswith('.pdf'):
        return False
    # ignore temp/partial file patterns
    if n.endswith('.part') or n.startswith('~') or n.endswith('.tmp'):
        return False
    return True

def scan_uploads_once(dry_run: bool = False) -> dict:
    """
    Scan MEDIA_ROOT/uploads for PDF files not present in the UploadedPDF table.
    If dry_run True: returns summary but does not create DB records.
    Returns summary dict: {'found': int, 'skipped': int, 'created': int, 'errors': []}
    """
    uploads_dir = Path(settings.MEDIA_ROOT) / 'uploads'
    result = {'found': 0, 'skipped': 0, 'created': 0, 'errors': []}

    if not uploads_dir.exists():
        logger.info("Uploads directory not found: %s", uploads_dir)
        return result

    # existing file paths stored in DB (file.name is relative path like 'uploads/xxx.pdf')
    existing_files = set(UploadedPDF.objects.values_list('file', flat=True))
    existing_basenames = {Path(f).name for f in existing_files if f}

    for path in uploads_dir.iterdir():
        if not path.is_file():
            continue
        fname = path.name
        result['found'] += 1

        if not _is_valid_pdf_filename(fname):
            result['skipped'] += 1
            continue

        if fname in existing_basenames:
            result['skipped'] += 1
            continue

        try:
            size = path.stat().st_size
            if dry_run:
                logger.info("DRY RUN: would create record for %s (%d bytes)", fname, size)
            else:
                with transaction.atomic():
                    inst = UploadedPDF(
                        original_name=fname,
                        size=size,
                        status=UploadedPDF.STATUS_UPLOADED,
                    )
                    # set FileField name relative to MEDIA_ROOT so Django can serve it
                    inst.file.name = f"uploads/{fname}"
                    inst.save()
                    logger.info("Created UploadedPDF id=%s for %s", inst.id, fname)
            result['created'] += 1
            existing_basenames.add(fname)
        except Exception as e:
            logger.exception("Error creating UploadedPDF for %s", fname)
            result['errors'].append({'file': fname, 'error': str(e)})

    return result
