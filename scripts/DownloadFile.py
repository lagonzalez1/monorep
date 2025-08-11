import os
import subprocess
from pathlib import Path


class DownloadFile:
    """
    Downloads a ZIP file from a URL or directly downloads a CSV file, extracts or renames it,
    and saves the result in a specified static_data directory.

    Attributes:
        url (str): The download URL.
        type (str): The type of download: 'csv' for direct CSV or 'txt' for zipped ZIP-to-CSV.
        SCRIPT_DIR (Path): Directory where this script resides.
    """

    # Define constants at class level if desired
    SCRIPT_DIR = Path(__file__).resolve().parent

    def __init__(self, url: str, download_type: str) -> None:
        """
        Initialize the downloader with a URL and download type.

        Args:
            url (str): The URL to download; either points to a .csv or a .zip.
            download_type (str): 'csv' to download directly, 'txt' to unzip and rename.
        """
        self.url = url
        self.type = download_type

    def download_file(self) -> bool:
        """
        Executes the bash helper to perform the download and conversion.
        Returns:
            bool: True if the operation succeeded, False otherwise.
        """
        try:
            # Construct path to the shell script helper
            script = self.SCRIPT_DIR / "download_static_data.sh"
            if not script.exists() or not os.access(script, os.X_OK):
                raise FileNotFoundError(f"Script not found or not executable: {script}")

            # Call the helper script with type and URL
            subprocess.run([str(script), self.type, self.url], check=True)
            return True

        except subprocess.CalledProcessError as e:
            # Log non-zero exit codes
            print(f"Download script failed with exit code {e.returncode}")
            return False

        except FileNotFoundError as e:
            # Handle missing or non-executable script
            print(f"Error locating download script: {e}")
            return False

        except Exception as e:
            # Catch-all for unexpected errors
            print(f"Unexpected error in download_file: {e}")
            return False
