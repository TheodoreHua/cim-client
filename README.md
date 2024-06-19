# CIM Client
The client component of the CIM (Command [Line] Instant Messenger) project, counterpart to the [CIM Server](https://github.com/TheodoreHua/cim-server).

## Screenshot
![](https://s3.theodorehua.dev/33a85cf7-3ac0-468a-8a90-d971b5cc4c42.png)

## Installation
### Installer
Installers are not currently available.

### Compiled Executable
There are precompiled executables in a portable format for Windows and Linux. 

> [!CAUTION]
> 
> These precompiled executables are **not currently stable and may cause errors**. It is recommended to use the source code.

1. Go to the [releases page](https://github.com/TheodoreHua/cim-server/releases)
2. Go to the "Assets" section of the latest release
3. Download the appropriate compressed file for your operating system
    - Windows: `cim-client-windows-portable.zip`
    - Linux: `cim-client-linux-portable.tar.gz`
4. Extract the compressed file to a directory of your choice
5. You can now use the program through `cim-server.exe` (Windows) or `cim-server.bin` (Linux)

### From Source
1. Have a Python 3 environment set up (recommended to use a version >= 3.8)
2. Go to the [releases page](https://github.com/TheodoreHua/cim-server/releases)
3. Download the source code compressed file
4. Extract the compressed file to a directory of your choice
5. Create a virtual environment (optional, but recommended)
    - Run `python -m venv venv` (or `python3 -m venv venv`) in the directory
    - Activate the virtual environment with `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux)
6. Install the required packages with `pip install -r requirements.txt`
7. You can now use the program through `python sim-client.py` (or `python3 sim-client.py`)

## Usage
> [!IMPORTANT]
> 
> As this client makes use of a TUI (Text User Interface), it is recommended to run the program in a modern terminal emulator.
> 
> For Windows specifically, it is recommended to use Windows Terminal instead of the default Command Prompt. For Linux, almost all terminal emulators should work fine.

The client is a command-line interface (CLI) program. Run the program with `python sim-client.py` (or `python3 sim-client.py`) to view the help message.
