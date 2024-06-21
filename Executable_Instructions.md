Step-by-Step Instructions for Creating an Executable (.exe) File

Install PyInstaller:
First, ensure you have PyInstaller installed. You can install it using pip:

    pip install pyinstaller


Prepare Your Script:
Make sure your script (FastDirectorySearch.py) is ready and working properly. Ensure that all required packages are installed and imported correctly in your script.


    FastDirectorySearch/
    ├── FastDirectorySearch.py
    └── Icon.ico


Create the Executable:
Open a terminal or command prompt, navigate to the FastDirectorySearch directory, and run the following command to create the executable:



    pyinstaller --name=FastDirectorySearch --onefile --windowed --icon=Icon.ico FastDirectorySearch.py


This command will instruct PyInstaller to generate a single executable file (--onefile), without a console window (--windowed), and include the specified icon (--icon=Icon.ico).

Locate the Executable:
After the build process completes, you will find the executable in the dist directory within your project folder. The structure should look like this:


    FastDirectorySearch/
    ├── dist/
    │   └── FastDirectorySearch.exe
    ├── build/
    ├── __pycache__/
    ├── FastDirectorySearch.spec
    ├── FastDirectorySearch.py
    └── Icon.ico

Test the Executable:
Run the generated .exe file (FastDirectorySearch.exe) from the dist directory to ensure it works correctly. Make sure all functionalities are operational.
