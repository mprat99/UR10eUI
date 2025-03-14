# UR10e UI

A PyQt6-based user interface for the UR10e robot control system. This application provides a modern, animated interface with real-time feedback and control capabilities through TCP communication.

## Project Structure

```
my_project/
├── main.py                   # Application entry point
├── README.md                 # Project documentation
├── requirements.txt          # List of Python package dependencies
├── config/
│   └── settings.py          # Configuration settings
├── ui/
│   ├── main_window.py       # Main window implementation
│   ├── ring_widget.py       # Background animation widget
│   └── section_widget.py    # Section widgets implementation
├── network/
│   └── tcp_client.py        # TCP client implementation
└── utils/
    └── helpers.py           # Helper functions
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv ur10e_ui_venv
   ```

2. Activate the virtual environment:
   - Windows: `.\ur10e_ui_venv\Scripts\activate`
   - Linux/Mac: `source ur10e_ui_venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the application, run:
```bash
python main.py
```

## Features

- Modern animated background with expanding rings
- Three main sections for robot control and monitoring
- Real-time TCP communication with the robot controller
- Responsive UI design 