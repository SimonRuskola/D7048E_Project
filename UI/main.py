import sys
import math
import time
from PyQt6.QtCore import Qt, QRunnable, QThreadPool, pyqtSlot, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QGridLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsEllipseItem, QGraphicsPixmapItem, QPushButton
from PyQt6.QtGui import QBrush, QPen, QPixmap
from inputs import get_gamepad
import AccelerometerGamepad 

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
class GamePadWorker(QRunnable):
    def __init__(self, fn, **kwargs):
        super().__init__()
        self.fn = fn
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        #Keyword argument used for coordinates
        self.kwargs["coordinate_callback"] = self.signals.coordinates
        
    @pyqtSlot()
    def run(self):
        result = self.fn(**self.kwargs)

class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    result
        object data returned from processing

    '''
    coordinates = pyqtSignal(object)
    
                
class MainWindow(QMainWindow):
    
    circle = MovableCircle

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")

        layout = QGridLayout()
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.sliderReleased.connect() # here connect to another function
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

    #it works! I ust need to make sure that the center point is actually the center point. 
    def gamepad_worker(self, coordinate_callback):
        abs_y = 0
        abs_x = 0
        center_x = (self.circle.big_circle_center.x() - self.circle.small_circle_radius)
        center_y = (self.circle.big_circle_center.y() - self.circle.small_circle_radius)
        maxMove = self.circle.max_movement_radius
        while 1:
            events = get_gamepad()
            for event in events:
                if(event.code == "ABS_Y"):
                    abs_y = event.state/32767
                    coordinate_callback.emit((center_x + maxMove*abs_x, center_y - maxMove*abs_y))
                elif(event.code == "ABS_X"):
                    abs_x = event.state/32767
                    coordinate_callback.emit((center_x + maxMove*abs_x, center_y - maxMove*abs_y))
                elif(event.code == "BTN_SOUTH"):
                    coordinate_callback.emit((85, 45))

    def accelerometer_worker(slef) :
        gamepad = AccelerometerGamepad()
        gamepad.loopData()

    def activate_controller(self):
        #create a thread and put the circle into the worker
        worker = GamePadWorker(self.gamepad_worker)
        worker.signals.coordinates.connect(self.move_circle)
        self.threadpool.start(worker)

        accelerometer_worker = GamePadWorker(self.accelerometer_worker)
        self.threadpool.start(accelerometer_worker)
    
    def move_circle(self, tuple):
        self.circle.setPos(tuple[0], tuple[1])


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
