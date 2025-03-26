from PyQt5.QtGui import QPen, QPolygon
from PyQt5.QtCore import QPoint
from shared_imports import *


def create_resources_directory():
    resources_dir = Path("resources")
    resources_dir.mkdir(exist_ok=True)
    return resources_dir


def create_icon(name, color_hex="#2196F3"):
    """Create a simple icon with the given name and color"""
    resources_dir = create_resources_directory()
    icon_path = resources_dir / f"{name}.png"

    # Skip if icon already exists
    if icon_path.exists():
        print(f"Icon already exists: {icon_path}")
        return

    # Create a transparent pixmap
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)

    # Set up painter
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Set pen for drawing
    pen = QPen(QColor(color_hex))
    pen.setWidth(3)
    painter.setPen(pen)

    # Draw based on icon name
    if name == "add_icon":
        # Plus sign
        painter.drawLine(16, 32, 48, 32)  # Horizontal
        painter.drawLine(32, 16, 32, 48)  # Vertical
    elif name == "select_icon":
        # Checkmark
        points = [QPoint(16, 32), QPoint(28, 44), QPoint(48, 20)]
        painter.drawPolyline(QPolygon(points))
    elif name == "delete_icon":
        # X mark
        painter.drawLine(16, 16, 48, 48)  # \
        painter.drawLine(48, 16, 16, 48)  # /
    elif name == "filter_icon":
        # Filter funnel
        points = [
            QPoint(12, 16),
            QPoint(52, 16),
            QPoint(36, 36),
            QPoint(36, 48),
            QPoint(28, 48),
            QPoint(28, 36),
            QPoint(12, 16)
        ]
        painter.drawPolygon(QPolygon(points))
    elif name == "export_icon":
        # Export arrow
        painter.drawLine(16, 32, 48, 32)  # Horizontal
        painter.drawLine(36, 20, 48, 32)  # Upper diagonal
        painter.drawLine(36, 44, 48, 32)  # Lower diagonal
        painter.drawLine(16, 20, 16, 44)  # Vertical line
    elif name == "refresh_icon":
        # Refresh circular arrow
        painter.drawArc(16, 16, 32, 32, 30 * 16, 300 * 16)
        # Arrow head
        painter.drawLine(40, 20, 48, 16)
        painter.drawLine(40, 20, 44, 28)
    elif name == "info_icon":
        # Info circle with i
        painter.drawEllipse(16, 16, 32, 32)
        painter.drawLine(32, 28, 32, 40)  # Vertical line
        painter.drawPoint(32, 24)  # Dot
    elif name == "success_icon":
        # Checkmark in circle
        painter.drawEllipse(16, 16, 32, 32)
        points = [QPoint(22, 32), QPoint(30, 40), QPoint(42, 24)]
        painter.drawPolyline(QPolygon(points))
    elif name == "error_icon":
        # X in circle
        painter.drawEllipse(16, 16, 32, 32)
        painter.drawLine(24, 24, 40, 40)  # \
        painter.drawLine(40, 24, 24, 40)  # /
    elif name == "warning_icon":
        # Exclamation in triangle
        points = [QPoint(32, 14), QPoint(50, 48), QPoint(14, 48)]
        painter.drawPolygon(QPolygon(points))
        painter.drawLine(32, 28, 32, 38)  # Vertical line
        painter.drawPoint(32, 42)  # Dot
    elif name == "close_icon":
        # Simple X
        painter.drawLine(16, 16, 48, 48)  # \
        painter.drawLine(48, 16, 16, 48)  # /

    # End painting
    painter.end()

    # Save the pixmap
    pixmap.save(str(icon_path))
    print(f"Created icon: {icon_path}")


def create_all_icons():
    """Create all required icons with appropriate colors"""
    icons_to_create = [
        ("add_icon", "#4CAF50"),  # Green
        ("select_icon", "#2196F3"),  # Blue
        ("delete_icon", "#F44336"),  # Red
        ("filter_icon", "#FF9800"),  # Orange
        ("export_icon", "#673AB7"),  # Purple
        ("refresh_icon", "#2196F3"),  # Blue
        ("info_icon", "#2196F3"),  # Blue
        ("success_icon", "#4CAF50"),  # Green
        ("error_icon", "#F44336"),  # Red
        ("warning_icon", "#FF9800"),  # Orange
        ("close_icon", "#757575"),  # Gray
    ]

    for name, color in icons_to_create:
        create_icon(name, color)


if __name__ == "__main__":
    create_all_icons()
    print("Icon creation complete!")