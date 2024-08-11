import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QSize
from PyQt5.QtOpenGL import QGLWidget
import math
import random  # For simulating temperature data

class OpenGLWidget(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)
        self.elapsed = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # 16ms = 60fps
        self.angle = 0
        self.move_angle = 0

    def animate(self):
        self.elapsed = (self.elapsed + self.timer.interval()) % 1000
        self.angle = (self.angle + 1) % 360
        self.move_angle = (self.move_angle + 1) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.drawOpenGLContent(painter, event, self.elapsed)

    def drawOpenGLContent(self, painter, event, elapsed):
        painter.setBrush(QColor(40, 40, 40))  # Dark gray background
        painter.drawRect(0, 0, self.width(), self.height())

        painter.setPen(QPen(Qt.white, 2))
        painter.drawRect(20, 20, self.width() - 40, self.height() - 40)

        painter.setPen(QPen(Qt.white, 1))
        center_x = int(self.width() / 2)
        center_y = int(self.height() / 2)
        radius = 100
        for i in range(36):
            angle = i * 10
            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            painter.drawLine(int(center_x), int(center_y), int(x), int(y))

        painter.setPen(QPen(Qt.red, 3))
        x1 = center_x + radius * math.cos(math.radians(self.angle))
        y1 = center_y + radius * math.sin(math.radians(self.angle))
        x2 = center_x + (radius + 20) * math.cos(math.radians(self.angle))
        y2 = center_y + (radius + 20) * math.sin(math.radians(self.angle))
        painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        painter.setBrush(QColor(0, 255, 0))
        painter.drawEllipse(50, 50, 20, 20)
        painter.setBrush(QColor(255, 0, 0))
        painter.drawEllipse(self.width() - 70, 50, 20, 20)

class AnimatedBox(QLabel):
    def __init__(self, parent=None):
        super(AnimatedBox, self).__init__(parent)
        self.setGeometry(QRect(0, 0, 50, 50))  
        self.setStyleSheet("background-color: green;")  
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.moveBox)
        self.timer.start(16)  
        self.x_speed = 5
        self.y_speed = 5  
        self.is_moving = False

    def startAnimation(self, start_pos, end_pos):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = QPoint(start_pos)
        self.is_moving = True

    def moveBox(self):
        if not self.is_moving:
            return

        direction = self.end_pos - self.start_pos
        distance = direction.manhattanLength()
        if distance > 0:
            norm = direction / distance
            movement = QPoint(int(self.x_speed * norm.x()), int(self.y_speed * norm.y()))
            self.current_pos += movement
            
            if (self.current_pos - self.start_pos).manhattanLength() >= distance:
                self.current_pos = self.end_pos
                self.is_moving = False
            
            self.move(self.current_pos)

            
            if self.geometry().intersects(self.parent().opengl_widget.geometry()):
                self.hide()

class ServerWidget(QWidget):
    def __init__(self, parent=None):
        super(ServerWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Server")
        
        # Initialize label before setting alignment
        label = QLabel("Server", self)
        label.setAlignment(Qt.AlignCenter)
        
        self.setStyleSheet("background-color: #87CEEB; border: 1px solid #c0c0c0;")
        vbox_layout_server = QVBoxLayout()
        self.setLayout(vbox_layout_server)

        label.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px; color: #008000; background-color: #87CEEB;")
        vbox_layout_server.addWidget(label)

class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Server Screen")

        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        window_width = int(screen_width * 0.7)
        window_height = int(screen_height * 0.8)
        self.setGeometry(50, 50, window_width, window_height)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        hbox_layout = QHBoxLayout()
        main_layout.addLayout(hbox_layout)

        self.opengl_widget = OpenGLWidget(self)
        self.opengl_widget.setFixedWidth(int(window_width * 0.3))
        self.opengl_widget.setFixedHeight(int(window_height * 0.5))
        hbox_layout.addWidget(self.opengl_widget)

        empty_space = QWidget(self)
        empty_space.setFixedWidth(int(window_width * 0.4))
        empty_space.setFixedHeight(window_height)
        hbox_layout.addWidget(empty_space)

        self.server_container = ServerWidget(self)
        self.server_container.setFixedWidth(int(window_width * 0.3))
        self.server_container.setFixedHeight(int(window_height * 0.5))
        hbox_layout.addWidget(self.server_container)

        button_layout = QVBoxLayout()
        fetch_button = QPushButton("Fetch Data", self)
        fetch_button.clicked.connect(self.onFetch)
        button_layout.addWidget(fetch_button)

        store_button = QPushButton("Store Data", self)
        store_button.clicked.connect(self.onStore)
        button_layout.addWidget(store_button)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
        main_layout.addLayout(button_layout)

        self.animated_box = AnimatedBox(self)
        self.animated_box.hide()  

    def onFetch(self):
        server_pos = self.server_container.geometry().topRight()
        opengl_pos = self.opengl_widget.geometry().topLeft()
        
        server_pos = self.mapToGlobal(server_pos)
        opengl_pos = self.mapToGlobal(opengl_pos)
        
        self.animated_box.setGeometry(QRect(server_pos, QSize(50, 50)))  
        self.animated_box.show()
        self.animated_box.startAnimation(server_pos, opengl_pos)

        self.checkTemperature()  # Check temperature on fetch

    def onStore(self):
        print("Store Data button clicked")
        
        try:
            subprocess.run(['python', 'store_data.py'], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running store_data.py: {e}")

    def checkTemperature(self):
        # Simulate fetching temperature data
        temperature = random.uniform(20, 100)  # Simulated temperature

        # Set the threshold
        threshold = 90
        
        if temperature > threshold:
            self.showHighTemperatureAlert(temperature)

    def showHighTemperatureAlert(self, temperature):
        alert = QMessageBox(self)
        alert.setWindowTitle("High Temperature Alert")
        alert.setText(f"Warning: High temperature detected! Current temperature: {temperature:.2f}°C")
        alert.setIcon(QMessageBox.Warning)
        alert.setStandardButtons(QMessageBox.Ok)
        alert.exec_()

if __name__ ==
