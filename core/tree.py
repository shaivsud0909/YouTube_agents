import os
from pathlib import Path

from fastapi import HTTPException

from core.logs import logger
from core.config import PROJECT_ROOT as BASE_DIR


def folder_tree(folder_name: str) -> dict:
    """
    Fetch the tree structure of a folder and its subfolders and files.
    """

    logger.info("Request received: folder-tree")

    try:
  
        folder_path = (BASE_DIR / folder_name).resolve()

        # Validate that the path stays inside BASE_DIR
        if not folder_path.is_relative_to(BASE_DIR.resolve()):
            raise HTTPException(
                status_code=400,
                detail="Invalid path",
            )

        if not folder_path.is_dir():
            raise HTTPException(
                status_code=404,
                detail="Folder not found",
            )

        tree_lines = []

        exclude = {".git", "__pycache__", ".venv", ".vscode"}

        def build_tree(path: Path, prefix: str = ""):
            items = sorted(
                item
                for item in os.listdir(path)
                if not item.startswith("~$") and item not in exclude
            )

            for index, item in enumerate(items):
                full_path = path / item

                is_last = index == len(items) - 1
                connector = "└── " if is_last else "├── "

                tree_lines.append(prefix + connector + item)

                if full_path.is_dir():
                    extension = "    " if is_last else "│   "
                    build_tree(full_path, prefix + extension)

        tree_lines.append(f"{folder_name}/")
        build_tree(folder_path)

        return {
            "folder": folder_name,
            "tree": tree_lines,
        }

    except HTTPException:
        raise

    except OSError:
        logger.exception("Filesystem error while generating folder tree")
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve folder tree",
        )

    except Exception:
        logger.exception("Unexpected error while generating folder tree")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )