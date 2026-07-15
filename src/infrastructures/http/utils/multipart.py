import asyncio
from typing import List

from fastapi import UploadFile

from core.dtos.file_meta import DFileMeta


def map_file_meta_to_httpx_request_file(
    multipart_key: str,
    file_meta: DFileMeta,
) -> tuple[str, tuple[str, bytes, str]]:
    """
    Maps a DFileMeta object to a format suitable for httpx multipart file uploads.
    The tuple format is (key, (filename, content, content_type)).

    Reference: https://www.python-httpx.org/quickstart/#sending-multipart-file-uploads

    Args:
        multipart_key: The key to be used in the multipart form data.
        file_meta: DFileMeta object containing the file metadata and content.

    Returns:
        A tuple containing the multipart key and a tuple with the filename, content, and content type.
    """

    return (
        multipart_key,
        (
            file_meta.filename or "unknown_filename",
            file_meta.content,
            file_meta.content_type or "application/octet-stream",
        ),
    )


async def map_upload_file_to_file_meta(upload_file: UploadFile) -> DFileMeta:
    """
    Maps an UploadFile object to a DFileMeta object.

    Args:
        upload_file: An instance of UploadFile from FastAPI.

    Returns:
        A DFileMeta object containing the file metadata and content.
    """
    return DFileMeta(
        filename=upload_file.filename,
        content=await upload_file.read(),
        content_type=upload_file.content_type,
    )


async def map_upload_files_to_file_metas(
    upload_files: List[UploadFile] | None,
) -> List[DFileMeta] | None:
    """
    Maps a list of UploadFile objects to a list of DFileMeta objects.

    Args:
        upload_files: A list of UploadFile instances from FastAPI or None if no files were uploaded.

    Returns:
        A list of DFileMeta objects containing the file metadata and content, or None if no files were uploaded.
    """

    if not upload_files:
        return None

    tasks = []
    for upload_file in upload_files:
        tasks.append(map_upload_file_to_file_meta(upload_file))
    return await asyncio.gather(*tasks)
