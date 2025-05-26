from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtCore import Qt
from utils.enums import State

class InfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background: transparent")
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo = QSvgWidget()
        self.logo.setFixedSize(50, 50)
        self.layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.layout.insertSpacing(self.layout.count(), 5) 

        self.title = QLabel()
        self.title.setStyleSheet("font-family: 'DM Sans'; font-weight: bold; font-size: 30px;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title)
        
        self.subtitle = QLabel()
        self.subtitle.setStyleSheet("font-family: 'DM Sans'; font-size: 20px;")
        self.subtitle.setWordWrap(True)
        self.subtitle.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.subtitle)
        self.layout.insertSpacing(self.layout.count(), -40) 

        self.image = QSvgWidget() 
        self.image.setFixedSize(200, 200) 
        self.layout.addWidget(self.image, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        init_config = {"state": "error"}
        self.update_state(init_config)
    

    def paintEvent(self, a0):
        return super().paintEvent(a0)
        

    def update_state(self, config):

        state = config.get("state")

        match State(state):
            case State.ERROR | State.STOPPED:
                self.logo.load("assets/info_error.svg")
                self.image.load("assets/info_speed_stopped.svg")
                self.title.setText("Stop Zone")
                self.subtitle.setText("You are impacting the\nproductivity of the robot")
            case State.WARNING | State.REDUCED_SPEED:
                self.logo.load("assets/info_warning.svg")
                self.image.load("assets/info_speed_reduced.svg")
                self.title.setText("Too close")
                self.subtitle.setText("You are impacting the\nproductivity of the robot")
            case State.TASK_FINISHED:
                self.logo.load("assets/info_done.svg")
                self.image.load("assets/info_replace_pallet.svg")
                self.title.setText("Task finished")
                self.subtitle.setText("Please, replace pallet")
            case _:
                self.logo = QSvgWidget() 
                self.image = QSvgWidget() 
                self.title.setText("")
                self.subtitle.setText("")
            
        if (title := config.get("screen2Text0")) is not None:
            self.title.setText(title)
        if (subtitle := config.get("screen2Text1")) is not None:
            self.subtitle.setText(subtitle)
            self.subtitle.setWordWrap(True)

        self.logo.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.image.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
