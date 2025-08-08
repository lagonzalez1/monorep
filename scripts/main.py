from DownloadFile import DownloadFile
from DependencyManager import DependencyManager
import logging
##from lib.verse import common

ENRON_EMAIL_URL = "https://raw.githubusercontent.com/adriancampos1/Enron_Email_Analysis/master/data/enron_emails_1702.csv"
ELECTRICITY_LOAD_DIAGRAM_URL = "https://archive.ics.uci.edu/static/public/321/electricityloaddiagrams20112014.zip"

def download_and_extract():
    """
        Run download file using Download class
        Return: None
    """
    ENRON_STATUS = DownloadFile(ENRON_EMAIL_URL, 'csv')
    print("Enron download", ENRON_STATUS.download_file())
    ELECTRICITY_DIAGRAM = DownloadFile(ELECTRICITY_LOAD_DIAGRAM_URL, 'zip')
    print("Electricity download", ELECTRICITY_DIAGRAM.download_file())


def align_python_deps():
    """
        Run update dependencies using DependencyManager class.
        Returns: None
    """
    al = DependencyManager()
    if al.alignment_available():
        possible_updates = al.update_pyproject()
        if not possible_updates:        
            print("No alignment available")
        update_project = al.test_pyproject()
        if update_project:
            print(" ".join([f'{update} ' for update in possible_updates]))
    
    print("No alignment available")
            

def main():
    download_and_extract()
    align_python_deps()

if __name__ == "__main__":
    main()
