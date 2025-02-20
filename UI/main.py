import sys
import math
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtWidgets import QApplication, QMainWindow, QSlider, QWidget, QGridLayout, QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsEllipseItem, QGraphicsPixmapItem
from PyQt6.QtGui import QBrush, QPen, QPixmap

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

class MainWindow(QMainWindow):
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

        circle = MovableCircle(20, ellipse)
        scene.addItem(circle)

        view = QGraphicsView(scene)
        layout.addWidget(view, 1, 0, 1, 3)

        self.setFixedSize(1000, 500)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
