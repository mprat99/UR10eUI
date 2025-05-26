# SSM UI

A **PyQt6-based user interface** for monitoring and interacting with a UR10e robotic system. This application provides a real-time, animated graphical interface for visualizing Safety State Monitoring (SSM) states using TCP communication and optional IMU input.

---

## 🚀 Features

- Real-time **TCP communication** with the UR10e controller  
- Optional **IMU-based rotation tracking**  
- Dynamic **UI with expanding rings**, bar charts, and live stats  
- **Multi-display support** with customizable screen layouts  
- Developer-friendly **debug settings**

---

## 🗂 Project Structure

```
SSM_UI/
├── dev.py
├── main.py
├── README.md
├── requirements.txt
│
├── assets/                 
│
├── config/
│   └── settings.py          
│
├── network/
│   ├── serial_reader.py
│   └── tcp_client.py
│
├── ui/
│   ├── ring_manager.py
│   ├── screen_window.py
│   ├── ui_controller.py
│   ├── ui_setup.py
│   │
│   ├── screens/
│   │
│   └── widgets/
├── utils/
│   ├── enums.py
│   └── utils.py
```


## ⚙️ Setup Instructions

1. **Create a Python virtual environment**:
   ```bash
   python -m venv ssm_ui_venv
   ```

2. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     .\ssm_ui_venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source ssm_ui_venv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Running the Application

To launch the UI in normal mode:
```bash
python main.py
```

To run in **development mode** with auto-reload on save:
```bash
python dev.py
```

This will automatically restart the application whenever you save a Python file—useful during development.

---

## 🧪 Development Tips

- Enable `DEBUG_MODE = True` in `settings.py` to:
  - Work with a **single monitor**
  - Use **smaller, resizable windows** instead of fullscreen
  - Simplify layout debugging and testing without multi-screen setup

---

## 🔧 Configuration – `config/settings.py`

Customize the application's behavior using the `settings.py` file:

### **Network Settings**
| Setting               | Description                            |
|-----------------------|----------------------------------------|
| `TCP_ENABLED`         | Enable TCP communication               |
| `TCP_HOST`            | IP of the UR10e controller             |
| `TCP_PORT`            | Port number for TCP                    |
| `TCP_MESSAGE_DELIMITER` | End-of-message byte delimiter        |

### **IMU Settings**
| Setting               | Description                            |
|-----------------------|----------------------------------------|
| `ROTATION_FROM_IMU`   | Enable IMU-based orientation tracking  |
| `IMU_SERIAL_PORT`     | Serial port of the IMU device          |
| `IMU_SERIAL_BAUDRATE` | Baud rate for serial communication     |
| `ROTATION_OFFSET`     | Offset correction for IMU rotation     |
| `ROTATION_THRESHOLD`  | Rotation detection threshold           |

### **UI Settings**
| Setting           | Description            |
|-------------------|------------------------|
| `GREEN_COLOR`     | Hex color for "safe"   |
| `YELLOW_COLOR`    | Hex color for "warning"|
| `RED_COLOR`       | Hex color for "stop"   |
| `BLUE_COLOR`      | Hex color (general)    |

### **Debug Settings**
| Setting                  | Description                                |
|--------------------------|--------------------------------------------|
| `DEBUG_MODE`             | Enable dev/debug display mode              |
| `DEBUG_DISPLAY_INDEX`    | Which display index to use (0 = primary)   |
| `DEBUG_NUM_SCREENS`      | Simulated number of screens                |
| `DEBUG_FRAMELESS_WINDOW` | Show the window without title bar         |
| `HIDE_WINDOW_FROM_TASKBAR` | Hide app from taskbar in debug mode     |

### **Layout Configuration**
| Setting                   | Description                                          |
|---------------------------|------------------------------------------------------|
| `UI_SCREEN_INDICES`       | Which displays the UI should use                     |
| `LIVE_STATS_AVAILABLE`    | Enable/disable the live stats section                |
| `SWITCH_SCREEN_INTERVAL`  | Auto-switch interval (ms) between stacked widgets    |
| `SCREEN_CLASSES_BY_INDEX` | Maps screen count to which widgets to show          |

---

## 🛠 Recommendations

- Use a **virtual environment** to isolate dependencies.
- Adjust `settings.py` before deployment or during development to match your hardware configuration.
- Use `dev.py` + `DEBUG_MODE = True` for a smoother development experience.
