import sys
import math
import time
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QGridLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsEllipseItem, QGraphicsPixmapItem, QPushButton
from PyQt6.QtGui import QBrush, QPen, QPixmap
from inputs import get_gamepad

class MovableCircle(QGraphicsEllipseItem):
    def __init__(self, diameter, parent_ellipse):
        super().__init__(0, 0, diameter, diameter)
        self.default_brush = QBrush(Qt.GlobalColor.white)
        self.active_brush = QBrush(Qt.GlobalColor.black)

        self.setBrush(self.default_brush)
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(4)
        self.setPen(pen)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)

        ellipse_rect = parent_ellipse.sceneBoundingRect()
        self.big_circle_center = ellipse_rect.center()

        self.big_circle_radius = ellipse_rect.width() / 2
        self.small_circle_radius = diameter / 2
        self.max_movement_radius = self.big_circle_radius - self.small_circle_radius

        self.setPos(self.big_circle_center.x() - self.small_circle_radius, 
                    self.big_circle_center.y() - self.small_circle_radius)
    


    def mousePressEvent(self, event):
        """Change color to black when clicked."""
        self.setBrush(self.active_brush)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        new_pos = self.mapToScene(event.pos())

        vector = new_pos - self.big_circle_center
        distance = math.sqrt(vector.x() ** 2 + vector.y() ** 2)

        if distance > self.max_movement_radius:
            vector *= self.max_movement_radius / distance 

        new_position = self.big_circle_center + vector

        self.setPos(new_position.x() - self.small_circle_radius, new_position.y() - self.small_circle_radius)

    def mouseReleaseEvent(self, event):
        """Reset the small circle to the center and turn it back to white."""
        self.setPos(self.big_circle_center.x() - self.small_circle_radius, 
                    self.big_circle_center.y() - self.small_circle_radius)
        self.setBrush(self.default_brush)
        super().mouseReleaseEvent(event)

#This class controlls the movement
class gamePadMovement(QRunnable):
    def __init__(self, movableCircle):
        super().__init__()
        self.args = movableCircle
    
    @pyqtSlot()
    def run(self):
        print("Gamepad functionality active")
        circle = self.args
        abs_y = 0
        abs_x = 0
        while 1:
            events = get_gamepad()
            for event in events:
                if(event.code == "ABS_Y"):
                    print("y = ",abs_y)
                    abs_y = event.state/372767
                    circle.setPos(circle.big_circle_center.x() + abs_x*circle.max_movement_radius, circle.big_circle_center.y() + abs_y*circle.max_movement_radius)
                elif(event.code == "ABS_X"):
                    print("x = ",abs_x)
                    abs_x = event.state/372767
                    circle.setPos(circle.big_circle_center.x() + abs_x*circle.max_movement_radius, circle.big_circle_center.y() + abs_y*circle.max_movement_radius)
                else:
                    print("other event detected")
                    circle.setPos(circle.big_circle_center.x() - circle.small_circle_radius, 
                    circle.big_circle_center.y() - circle.small_circle_radius)
                
class MainWindow(QMainWindow):
    
    circle = MovableCircle

    def activate_controller(self):
        #create a thread and put the circle into the worker
        worker = gamePadMovement(self.circle)
        self.threadpool.start(worker)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        layout.addWidget(slider, 0, 2)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        scene = QGraphicsScene(0, 0, 400, 300)

        controller_image = QPixmap("controller.png")
        controller_image = controller_image.scaled(400, 275, Qt.AspectRatioMode.KeepAspectRatio)

        controller_pixmap_item = QGraphicsPixmapItem(controller_image)
        controller_pixmap_item.setPos(0, 0)
        scene.addItem(controller_pixmap_item)

        ellipse = QGraphicsEllipseItem(85, 45, 70, 70)
        brush = QBrush(Qt.GlobalColor.white)
        ellipse.setBrush(brush)
        pen = QPen(Qt.GlobalColor.black)
        pen.setWidth(4)
        ellipse.setPen(pen)
        scene.addItem(ellipse)

        self.circle = MovableCircle(20, ellipse)
        scene.addItem(self.circle)

        #create a thread pool
        self.threadpool = QThreadPool()

        #button to start thread: (idk if there is some better way to do this)
        button = QPushButton("detect controller")
        button.pressed.connect(self.activate_controller)
        layout.addWidget(button, 0, 3)

        view = QGraphicsView(scene)
        layout.addWidget(view, 1, 0, 1, 3)

        self.setFixedSize(1000, 500)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
