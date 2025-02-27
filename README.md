# Project Title

**Develop an Utility to Explore Running Processes and Registry Information from the Host Machine**

## Description

This utility provides real-time visibility into the running processes and registry information of a host machine. It captures live process details and organizes registry data into categories such as device details, installed software, browser history, and more. This tool is intended for system administrators, cybersecurity professionals, and anyone interested in monitoring system activities.

### Features

- **Live Process Monitoring**: Displays running processes in real time, showing CPU and memory usage.
- **Registry Information Capture**: Captures details from the Windows registry, including recently used files, installed software, browser history, and more.
- **Browser History**: Extracts history from Internet Explorer, Google Chrome, Microsoft Edge, and Firefox.
- **Removable Devices**: Detects devices like USB drives and printers connected to the system.
- **Startup Programs and Services**: Lists software that runs at startup and their respective services.
- **Network Configuration**: Displays installed network cards and their status.

---

## Installation

To run the utility on your system, follow these steps:

### Prerequisites
1. **Python**: You need Python 3.x installed.
2. **Required Libraries**: 
   - psutil
   - tkinter
   - SQLite3 (for browser history handling)
   
   Install them using pip:
   ```bash
   pip install psutil tkinter sqlite3
   ```

## Setup

1. Clone the repository or download the project files.
2. Ensure Python is installed and libraries are set up.
3. Run the script as follows:
   ```bash
   python display_scrapper.py
   ```

# Usage

## 1. Live Process Monitoring
Upon running the script, you will see a graphical user interface (GUI) displaying live processes, similar to the Task Manager. It provides details such as:

- **Process ID (PID)**
- **Memory usage**
- **CPU usage**
- **Process name**

## 2. Registry Information Capture
A PowerShell script captures registry details related to:

- Installed software
- Recent documents
- Devices connected to the machine

The data is saved as a JSON file, which is later parsed by a Python script and displayed in a human-readable format.

## 3. Browser History Capture
The utility automatically fetches browser history data from:

- **Chrome**
- **Edge**
- **Firefox**

It saves this data in SQLite3 database format. The Internet Explorer history is captured from the registry.


# Example Output
The output will display information such as:

- **System Information**: Computer name, OS version, timezone.
- **Recent Files**: Recently accessed EXE, PPTX, ZIP, XLSX files.
- **Installed Software**: A list of installed software and versions.
- **Removable Devices**: Information about USB drives, printers, and other removable devices.
- **Browser History**: Lists of URLs visited in browsers.

## Contributions
Contributions are welcome! If you'd like to contribute to this project, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- **psutil**: Used for gathering process information.
- **SQLite3**: Used for storing browser history data in a structured format.
- **tkinter**: Used for creating the graphical user interface (GUI).

