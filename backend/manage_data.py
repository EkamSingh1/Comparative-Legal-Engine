from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from dotenv import load_dotenv

try:
    from google import genai
    from google.genai import types
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "google-genai is not installed. Run: pip install -r backend/requirements.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parent
SOURCES_DIR = ROOT / "sources"
DEFAULT_STORE = "Islamic-Law-Sources"


def load_environment() -> None:
    load_dotenv(ROOT / ".env")
    load_dotenv(BACKEND_DIR / ".env")


def get_client():
    load_environment()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def get_store(client, display_name: str, create: bool = False):
    for store in client.file_search_stores.list():
        if getattr(store, "display_name", None) == display_name:
            return store
    if not create:
        return None
    return client.file_search_stores.create(config={"display_name": display_name})


def list_documents(client, store_name: str) -> list:
    store = get_store(client, store_name)
    if not store:
        return []
    return list(client.file_search_stores.documents.list(parent=store.name))


def document_exists(client, store_name: str, display_name: str) -> bool:
    return any(
        getattr(doc, "display_name", None) == display_name
        for doc in list_documents(client, store_name)
    )


def wait_for_operation(client, operation) -> None:
    while not operation.done:
        time.sleep(5)
        operation = client.operations.get(operation)


def upload_pdf(client, store_name: str, path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"File not found: {path}")
    if document_exists(client, store_name, path.name):
        print(f"Skipping existing document: {path.name}")
        return

    store = get_store(client, store_name, create=True)
    print(f"Uploading {path.name} to {store.display_name}...")
    operation = client.file_search_stores.upload_to_file_search_store(
        file=str(path),
        file_search_store_name=store.name,
        config={"display_name": path.name},
    )
    wait_for_operation(client, operation)
    print(f"Indexed {path.name}")


def upload_all(client, store_name: str) -> None:
    for path in sorted(SOURCES_DIR.glob("*.pdf")):
        upload_pdf(client, store_name, path)


def test_query(client, store_name: str, question: str) -> None:
    store = get_store(client, store_name)
    if not store:
        raise SystemExit(f"Store not found: {store_name}")
    response = client.models.generate_content(
        model=os.getenv("GEMINI_FILE_SEARCH_MODEL", "gemini-3.1-flash-lite-preview"),
        contents=question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(file_search_store_names=[store.name])
                )
            ]
        ),
    )
    print(response.text)


def main() -> None:
    load_environment()
    parser = argparse.ArgumentParser(description="Manage Gemini File Search source PDFs.")
    parser.add_argument(
        "--store",
        default=os.getenv("GEMINI_FILE_SEARCH_STORE", DEFAULT_STORE),
        help="File Search store display name.",
    )

    subcommands = parser.add_subparsers(dest="command", required=True)
    subcommands.add_parser("list", help="List indexed documents.")
    subcommands.add_parser("upload-all", help="Upload all PDFs from ./sources.")

    upload_parser = subcommands.add_parser("upload", help="Upload one PDF.")
    upload_parser.add_argument("path", type=Path)

    test_parser = subcommands.add_parser("test", help="Run a test File Search query.")
    test_parser.add_argument(
        "question",
        nargs="?",
        default="Identify the source documents indexed in this store.",
    )

    args = parser.parse_args()
    client = get_client()

    if args.command == "list":
        documents = list_documents(client, args.store)
        if not documents:
            print("No documents found.")
            return
        for doc in documents:
            print(f"{doc.display_name} ({doc.name})")
    elif args.command == "upload-all":
        upload_all(client, args.store)
    elif args.command == "upload":
        upload_pdf(client, args.store, args.path)
    elif args.command == "test":
        test_query(client, args.store, args.question)


if __name__ == "__main__":
    main()
