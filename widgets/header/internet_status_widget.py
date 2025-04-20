from PyQt5.QtCore import (Qt, QTimer, QPropertyAnimation, QEasingCurve, QEvent,
                          QPoint, QRectF, QSize, pyqtSignal, QTime)
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLabel, QToolTip,
                             QVBoxLayout, QFrame, QApplication, QGraphicsOpacityEffect,
                             QGridLayout, QGraphicsDropShadowEffect, QSizePolicy, QDialog)
from PyQt5.QtGui import (QPixmap, QColor, QPainter, QPen, QFont, QCursor, QPainterPath,
                         QLinearGradient, QRadialGradient)
import socket
import platform
import subprocess
import re
import threading
import time
from themes import get_color


class InfoRow(QFrame):
    """Modern row for network information display"""

    def __init__(self, label, value="", parent=None):
        super().__init__(parent)
        self.setObjectName("infoRow")

        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 6, 0, 6)
        layout.setSpacing(6)

        # Label
        self.label = QLabel(label)
        self.label.setObjectName("infoLabel")

        # Value
        self.value = QLabel(value)
        self.value.setObjectName("infoValue")
        self.value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Add to layout
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.value)

    def update_value(self, new_value):
        """Update the value text"""
        self.value.setText(new_value)


class NetworkInfoDialog(QDialog):
    """
    Dialog that shows detailed network information.
    Using a dialog instead of a popup widget for better stability.
    """

    # COMPLETE __init__ METHOD FOR NetworkInfoDialog:
    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self.translator = translator  # Store translator reference
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Configure dialog behavior - this is key to stability
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Don't delete on close, just hide

        # Network data with defaults
        self.ip_address = "Checking..."
        self.ping_latency = "Checking..."
        self.connection_type = "Checking..."
        self.network_name = "Checking..."
        self.is_connected = False

        # Cached data to avoid repeated system calls
        self.last_check_time = 0
        self.cache_duration = 5  # Cache network data for 5 seconds

        # Setup UI
        self._setup_ui()

        # Initial check
        self._check_connection_async()

    # COMPLETE update_ui METHOD FOR NetworkInfoDialog:
    def update_ui(self):
        """Update UI with current network status"""
        # Update status indicator and row
        if self.is_connected:
            self.status_indicator.setStyleSheet("#statusIndicator { background-color: #2ecc71; border-radius: 6px; }")
            if self.translator:
                self.status_row.update_value(self.translator.t("Connected"))
            else:
                self.status_row.update_value("Connected")
        else:
            self.status_indicator.setStyleSheet("#statusIndicator { background-color: #e74c3c; border-radius: 6px; }")
            if self.translator:
                self.status_row.update_value(self.translator.t("Disconnected"))
            else:
                self.status_row.update_value("Disconnected")

        # Update IP address
        self.ip_row.update_value(self.ip_address)

        # Update network name
        self.network_row.update_value(self.network_name)

        # Update connection type
        self.connection_row.update_value(self.connection_type)

        # Update ping latency with color coding
        if self.ping_latency.isdigit():
            ping_value = int(self.ping_latency)

            # Determine quality text and color
            if ping_value < 30:
                quality = "Excellent"
                color = "#2ecc71"  # Green
            elif ping_value < 70:
                quality = "Good"
                color = "#27ae60"  # Darker green
            elif ping_value < 120:
                quality = "Fair"
                color = "#f39c12"  # Yellow/orange
            else:
                quality = "Poor"
                color = "#e74c3c"  # Red

            ping_text = f"{ping_value} ms"

            # Update with HTML for color
            self.ping_row.update_value(f"<span style='color:{color};'>{ping_text}</span>")
        else:
            self.ping_row.update_value(self.ping_latency)

    # NEW update_translations METHOD FOR NetworkInfoDialog:
    def update_translations(self):
        """Update all translations in the dialog"""
        if not self.translator:
            return

        # Update title
        if hasattr(self, 'title'):
            self.title.setText(self.translator.t("Network Status"))

        # Update all info rows
        if hasattr(self, 'status_row'):
            self.status_row.label.setText(self.translator.t("Status"))
            # Also update value based on connection state
            if self.is_connected:
                self.status_row.update_value(self.translator.t("Connected"))
            else:
                self.status_row.update_value(self.translator.t("Disconnected"))

        if hasattr(self, 'ip_row'):
            self.ip_row.label.setText(self.translator.t("IP Address"))

        if hasattr(self, 'network_row'):
            self.network_row.label.setText(self.translator.t("Network"))

        if hasattr(self, 'connection_row'):
            self.connection_row.label.setText(self.translator.t("Connection"))

        if hasattr(self, 'ping_row'):
            self.ping_row.label.setText(self.translator.t("Latency"))

        # Force UI update
        self.update_ui()


    def _setup_ui(self):
        """Set up the panel UI"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Main container
        self.container = QFrame()
        self.container.setObjectName("networkInfoContainer")

        # Apply shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.shadow.setOffset(0, 3)
        self.container.setGraphicsEffect(self.shadow)

        # Container layout
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(15, 15, 15, 15)
        container_layout.setSpacing(5)

        # Header with status indicator
        header_layout = QHBoxLayout()

        # Title
        self.title = QLabel("Network Status")
        self.title.setObjectName("networkTitle")

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setFixedSize(12, 12)
        self.status_indicator.setObjectName("statusIndicator")

        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)

        container_layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        container_layout.addWidget(separator)

        # Info rows container
        self.info_container = QFrame()
        info_layout = QVBoxLayout(self.info_container)
        info_layout.setContentsMargins(0, 10, 0, 5)
        info_layout.setSpacing(0)

        # Create info rows
        self.status_row = InfoRow("Status")
        self.ip_row = InfoRow("IP Address")
        self.network_row = InfoRow("Network")
        self.connection_row = InfoRow("Connection")
        self.ping_row = InfoRow("Latency")

        # Add rows to container
        info_layout.addWidget(self.status_row)
        info_layout.addWidget(self.ip_row)
        info_layout.addWidget(self.network_row)
        info_layout.addWidget(self.connection_row)
        info_layout.addWidget(self.ping_row)

        # Add all to container
        container_layout.addWidget(self.info_container)

        # Add container to main layout
        layout.addWidget(self.container)

        # Ensure the panel has a reasonable size
        self.setFixedWidth(260)

    def _check_connection_async(self):
        """Start a new thread to check connection without blocking UI"""
        # Check if we have recent cached data
        current_time = time.time()
        if current_time - self.last_check_time < self.cache_duration:
            # Use cached data and just update UI
            QTimer.singleShot(0, self.update_ui)
            return

        # Create a new thread for the check
        threading.Thread(target=self._check_connection_thread, daemon=True).start()

    def _check_connection_thread(self):
        """Run connection checks in a separate thread"""
        try:
            # Run all network checks
            self._check_connection()
            self.last_check_time = time.time()

            # Update UI in the main thread
            QTimer.singleShot(0, self.update_ui)
        except Exception as e:
            print(f"Error checking connection: {e}")

    def _check_connection(self):
        """Check internet connection and network details"""
        # Check basic connectivity
        try:
            # Connect to Google's DNS server
            socket.create_connection(("8.8.8.8", 53), timeout=1)
            self.is_connected = True
        except OSError:
            self.is_connected = False

        # Update IP address if connected
        if self.is_connected:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                self.ip_address = s.getsockname()[0]
                s.close()
            except:
                self.ip_address = "Unknown"
        else:
            self.ip_address = "Not available"

        # Check connection type and network name
        self._check_network_details()

        # Check ping latency if connected
        if self.is_connected:
            try:
                param = '-n' if platform.system().lower() == 'windows' else '-c'
                command = ['ping', param, '1', '8.8.8.8']

                result = subprocess.run(command, capture_output=True, text=True)

                if platform.system().lower() == 'windows':
                    match = re.search(r'time[=<](\d+)ms', result.stdout)
                else:
                    match = re.search(r'time=(\d+\.\d+) ms', result.stdout)

                if match:
                    ping_time = match.group(1)
                    try:
                        ping_time = str(int(float(ping_time)))
                    except ValueError:
                        pass

                    self.ping_latency = ping_time
                else:
                    self.ping_latency = "Unknown"
            except:
                self.ping_latency = "Error"
        else:
            self.ping_latency = "No connection"

    def _check_network_details(self):
        """Get network connection details based on platform"""
        if not self.is_connected:
            self.connection_type = "None"
            self.network_name = "Not connected"
            return

        try:
            system = platform.system().lower()

            if system == 'windows':
                # Get network connection details on Windows
                self._check_windows_network()
            elif system == 'darwin':  # macOS
                self._check_macos_network()
            else:  # Linux and others
                self._check_linux_network()
        except Exception as e:
            print(f"Error checking network details: {e}")
            self.connection_type = "Unknown"
            self.network_name = "Unknown"

    def _check_windows_network(self):
        """Check network details on Windows"""
        # Check for active WiFi connection
        try:
            wifi_result = subprocess.run(
                ['netsh', 'wlan', 'show', 'interfaces'],
                capture_output=True, text=True, timeout=1
            )

            # Look for connected WiFi
            if "State                 : connected" in wifi_result.stdout:
                self.connection_type = "WiFi"

                # Extract SSID (network name)
                ssid_match = re.search(r'SSID\s+:\s+(.+)', wifi_result.stdout)
                if ssid_match:
                    self.network_name = ssid_match.group(1).strip()
                else:
                    self.network_name = "Unknown WiFi"
                return
        except:
            pass  # Fall back to checking Ethernet

        # If we get here, either WiFi check failed or WiFi is not connected
        # Check Ethernet connections
        try:
            # Use ipconfig to get network adapter info
            ip_result = subprocess.run(
                ['ipconfig'],
                capture_output=True, text=True, timeout=1
            )

            # Look for Ethernet adapter with IP address
            ethernet_sections = re.finditer(
                r'Ethernet adapter ([^:]+):[.\s\S]+?IPv4 Address[^:]*:\s+(\d+\.\d+\.\d+\.\d+)',
                ip_result.stdout
            )

            for match in ethernet_sections:
                adapter_name = match.group(1).strip()
                # Found an active Ethernet connection
                self.connection_type = "Ethernet"
                self.network_name = adapter_name
                return

            # If we got here but have an IP, we're connected somehow
            if self.is_connected:
                self.connection_type = "Network"
                self.network_name = "Unknown connection"
            else:
                self.connection_type = "None"
                self.network_name = "Not connected"
        except:
            self.connection_type = "Unknown"
            self.network_name = "Unknown"

    def _check_macos_network(self):
        """Check network details on macOS"""
        try:
            # Use networksetup to get active network service
            result = subprocess.run(
                ['networksetup', '-listallhardwareports'],
                capture_output=True, text=True, timeout=1
            )

            # Look for Wi-Fi
            wifi_section = re.search(r'Hardware Port: Wi-Fi\nDevice: (en\d+)', result.stdout)
            if wifi_section:
                wifi_device = wifi_section.group(1)

                # Check if this interface has an IP
                ip_result = subprocess.run(
                    ['ipconfig', 'getifaddr', wifi_device],
                    capture_output=True, text=True, timeout=1
                )

                if ip_result.stdout.strip():
                    # WiFi is active with IP
                    self.connection_type = "WiFi"

                    # Get SSID
                    airport_result = subprocess.run(
                        ['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport',
                         '-I'],
                        capture_output=True, text=True, timeout=1
                    )

                    ssid_match = re.search(r' SSID: (.+)', airport_result.stdout)
                    if ssid_match:
                        self.network_name = ssid_match.group(1).strip()
                    else:
                        self.network_name = "Unknown WiFi"
                    return

            # Check for Ethernet
            ethernet_section = re.search(r'Hardware Port: Ethernet\nDevice: (en\d+)', result.stdout)
            if ethernet_section:
                eth_device = ethernet_section.group(1)

                # Check if this interface has an IP
                ip_result = subprocess.run(
                    ['ipconfig', 'getifaddr', eth_device],
                    capture_output=True, text=True, timeout=1
                )

                if ip_result.stdout.strip():
                    # Ethernet is active
                    self.connection_type = "Ethernet"
                    self.network_name = "Wired Connection"
                    return

            # If we got here but have an IP, we're connected somehow
            if self.is_connected:
                self.connection_type = "Network"
                self.network_name = "Unknown connection"
            else:
                self.connection_type = "None"
                self.network_name = "Not connected"
        except:
            self.connection_type = "Unknown"
            self.network_name = "Unknown"

    def _check_linux_network(self):
        """Check network details on Linux"""
        try:
            # Use iwconfig to detect wireless
            iwconfig_result = subprocess.run(
                ['iwconfig'],
                capture_output=True, text=True, timeout=1
            )

            # Look for connected wireless
            wifi_match = re.search(r'(\w+).*ESSID:"([^"]+)"', iwconfig_result.stdout)
            if wifi_match and "Not-Associated" not in iwconfig_result.stdout:
                self.connection_type = "WiFi"
                self.network_name = wifi_match.group(2).strip()
                return

            # If no WiFi, check for Ethernet using ifconfig
            ifconfig_result = subprocess.run(
                ['ifconfig'],
                capture_output=True, text=True, timeout=1
            )

            # Look for an Ethernet interface with IP
            eth_match = re.search(r'(eth\d|en\w+).*inet (\d+\.\d+\.\d+\.\d+)', ifconfig_result.stdout, re.DOTALL)
            if eth_match:
                self.connection_type = "Ethernet"
                self.network_name = eth_match.group(1).strip()
                return

            # If we got here but have an IP, we're connected somehow
            if self.is_connected:
                self.connection_type = "Network"
                self.network_name = "Unknown connection"
            else:
                self.connection_type = "None"
                self.network_name = "Not connected"
        except:
            self.connection_type = "Unknown"
            self.network_name = "Unknown"

    def apply_theme(self):
        """Apply current theme styling"""
        bg_color = get_color('background')
        text_color = get_color('text')
        border_color = get_color('border')

        self.setStyleSheet(f"""
            #networkInfoContainer {{
                background-color: {bg_color};
                border-radius: 10px;
                border: 1px solid {border_color};
            }}

            #networkTitle {{
                color: {text_color};
                font-size: 15px;
                font-weight: bold;
            }}

            #separator {{
                background-color: {border_color};
            }}

            #infoRow {{
                border: none;
                background: transparent;
            }}

            #infoLabel {{
                color: {text_color};
                opacity: 0.8;
                font-size: 13px;
            }}

            #infoValue {{
                color: {text_color};
                font-size: 13px;
                font-weight: bold;
            }}
        """)

    def position_relative_to(self, widget):
        """
        Improved method to position the panel relative to the widget
        that avoids constant repositioning during window resizing.
        """
        if not widget:
            return

        # Don't reposition if parent window is being resized
        parent_window = widget.window()
        if hasattr(parent_window, '_in_resize') and parent_window._in_resize:
            return

        # Don't reposition if we're already visible and the user
        # might be in the middle of interacting with the dialog
        if self.isVisible() and hasattr(self, '_shown_time'):
            # Only reposition if it's been less than 500ms since first shown
            # This prevents repositioning during resize when the dialog is already visible
            if QTime.currentTime().msecsTo(self._shown_time) > 500:
                return

        # Get global position with minimal calculations
        global_pos = widget.mapToGlobal(QPoint(0, 0))
        widget_center = global_pos.x() + widget.width() // 2

        # Position panel below the widget
        x = widget_center - (self.width() // 2)
        y = global_pos.y() + widget.height() + 5

        # Simple screen boundary check
        screen = QApplication.desktop().screenGeometry()
        if x + self.width() > screen.width():
            x = screen.width() - self.width() - 10
        if x < 0:
            x = 10

        # Move to the calculated position
        self.move(x, y)

    def showEvent(self, event):
        """Enhanced show event handler that tracks show time"""
        super().showEvent(event)

        # Store the time when dialog was shown
        self._shown_time = QTime.currentTime()

        # Use cached data first for immediate display
        self.update_ui()

        # Then request fresh data asynchronously
        QTimer.singleShot(10, self._check_connection_async)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        # Prevent dialog from closing when clicked inside it
        event.accept()


class OptimizedInternetStatusWidget(QWidget):
    """
    Optimized internet status widget with click to show details.
    Properly handles window closing and uses async operations for better performance.
    """
    clicked = pyqtSignal()

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.is_connected = False
        self.info_dialog = None  # Changed to dialog

        # Cache check results
        self.last_check_time = 0
        self.check_in_progress = False

        # Setup UI
        self.setup_ui()

        # Set up timer for periodic checks
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_connection_async)
        self.check_timer.start(10000)  # Check every 10 seconds

        # Initial connection check (async)
        self.check_connection_async()

        # Enable mouse tracking and set cursor
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    # For backward compatibility
    def check_connection(self):
        """Backward compatibility method that calls check_connection_async"""
        self.check_connection_async()

    def setup_ui(self):
        """Initialize the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(0)

        # Create icon label
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(32, 32)

        # Create icon
        self.create_network_icon()

        # Add to layout
        layout.addWidget(self.status_icon)

        # Set fixed width
        self.setFixedWidth(42)

    def create_network_icon(self):
        """Create a network icon"""
        size = 32
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw circular background
        painter.setBrush(QColor(70, 130, 180, 50))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, size - 2, size - 2)

        # Draw network icon
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.NoBrush)

        # Center of icon
        center_x = size / 2
        center_y = size / 2

        # Draw globe
        globe_radius = size * 0.35
        painter.drawEllipse(QRectF(center_x - globe_radius, center_y - globe_radius,
                                   globe_radius * 2, globe_radius * 2))

        # Draw network arcs
        painter.drawArc(QRectF(center_x - size * 0.5, center_y - size * 0.5,
                               size, size), 40 * 16, 100 * 16)
        painter.drawArc(QRectF(center_x - size * 0.6, center_y - size * 0.6,
                               size * 1.2, size * 1.2), 40 * 16, 100 * 16)

        # Add status indicator
        indicator_size = 10

        if self.is_connected:
            indicator_color = QColor(40, 200, 40)  # Green
        else:
            indicator_color = QColor(200, 40, 40)  # Red

        # Draw indicator with glow
        painter.setBrush(QColor(indicator_color.red(), indicator_color.green(),
                                indicator_color.blue(), 80))
        painter.drawEllipse(QRectF(size - indicator_size - 2,
                                   size - indicator_size - 2,
                                   indicator_size + 4,
                                   indicator_size + 4))

        painter.setBrush(indicator_color)
        painter.drawEllipse(QRectF(size - indicator_size - 2,
                                   size - indicator_size - 2,
                                   indicator_size,
                                   indicator_size))

        painter.end()

        self.status_icon.setPixmap(pixmap)

    def check_connection_async(self):
        """Start an async check of the connection status"""
        # Don't start another check if one is already in progress
        if self.check_in_progress:
            return

        # Check if we have recent data (within 5 seconds)
        current_time = time.time()
        if current_time - self.last_check_time < 5:
            return

        self.check_in_progress = True
        threading.Thread(target=self._check_connection_thread, daemon=True).start()

    def _check_connection_thread(self):
        """Run the connection check in a background thread"""
        try:
            # Simple check - just test connectivity
            previous_state = self.is_connected

            try:
                socket.create_connection(("8.8.8.8", 53), timeout=1)
                self.is_connected = True
            except OSError:
                self.is_connected = False

            # Update timestamp
            self.last_check_time = time.time()

            # Only update UI if state changed
            if previous_state != self.is_connected:
                # Update UI in the main thread
                QTimer.singleShot(0, self.update_display)

                # Update info dialog if visible
                try:
                    if self.info_dialog and self.info_dialog.isVisible():
                        QTimer.singleShot(10, self.info_dialog._check_connection_async)
                except:
                    # Just ignore errors here, the dialog will update when shown next time
                    pass
        finally:
            self.check_in_progress = False

    def update_display(self):
        """Update the icon display"""
        self.create_network_icon()  # Recreate icon with current status
        self._update_tooltip()

    def _update_tooltip(self):
        """Update tooltip text"""
        if self.is_connected:
            status = self.translator.t("Internet: Connected")  # Correct method
        else:
            status = self.translator.t("Internet: Disconnected")  # Correct method

        click_text = self.translator.t("Click for details")  # Correct method
        self.setToolTip(f"{status}\n{click_text}")


    def apply_theme(self):
        """Apply theme styling"""
        if self.info_dialog:
            try:
                self.info_dialog.apply_theme()
            except:
                # If dialog is invalid, just create a new one next time
                self.info_dialog = None

        # The icon is drawn directly
        self.setStyleSheet("background-color: transparent;")

        # Update icon
        self.create_network_icon()

    # CORRECTED version of the InternetStatusWidget update_translations method:
    def update_translations(self):
        """Update all translations in the widget and dialog"""
        # Update tooltip using the correct t() method, not tr()
        if self.is_connected:
            status = self.translator.t("Internet: Connected")
        else:
            status = self.translator.t("Internet: Disconnected")

        click_text = self.translator.t("Click for details")
        self.setToolTip(f"{status}\n{click_text}")

        # Update the dialog if it exists
        if hasattr(self, 'info_dialog') and self.info_dialog:
            # Pass translator to dialog if needed
            if hasattr(self.info_dialog, 'translator') and self.info_dialog.translator is None:
                self.info_dialog.translator = self.translator

            # Call dialog's update_translations if available
            if hasattr(self.info_dialog, 'update_translations'):
                self.info_dialog.update_translations()

        # Force recreation of the network icon with new translations
        self.create_network_icon()

    # CORRECTED version of the enterEvent method (if present):
    def enterEvent(self, event):
        """Handle mouse enter for tooltip"""
        if self.is_connected:
            tooltip_text = f"{self.translator.t('Internet: Connected')}\n{self.translator.t('Click for details')}"
        else:
            tooltip_text = f"{self.translator.t('Internet: Disconnected')}\n{self.translator.t('Click for details')}"

        QToolTip.showText(event.globalPos(), tooltip_text)
        super().enterEvent(event)

    # CORRECTED version of the toggle_info_dialog method:
    def toggle_info_dialog(self):
        """Show or hide the network info dialog - completely redesigned for reliability"""
        print("Toggle info dialog called")

        # Create dialog if needed
        if not self.info_dialog:
            print("Creating new dialog")
            # Create dialog without parent to avoid deletion when parent state changes
            self.info_dialog = NetworkInfoDialog(self.translator)  # FIXED: Pass translator here!
            self.info_dialog.apply_theme()

        # Simple toggle visibility
        if self.info_dialog.isVisible():
            print("Dialog is visible, hiding it")
            self.info_dialog.hide()
        else:
            print("Dialog is hidden, showing it")
            # Position and show
            self.info_dialog.position_relative_to(self)
            self.info_dialog.show()

            # Make sure dialog gets updated data
            QTimer.singleShot(10, self.info_dialog._check_connection_async)


    def mousePressEvent(self, event):
        """Handle mouse press to toggle dialog"""
        if event.button() == Qt.LeftButton:
            self.toggle_info_dialog()
            self.clicked.emit()
        super().mousePressEvent(event)


    def hideEvent(self, event):
        """Hide dialog when widget is hidden"""
        if self.info_dialog and self.info_dialog.isVisible():
            self.info_dialog.hide()
        super().hideEvent(event)

    def closeEvent(self, event):
        """Handle close event - properly clean up resources"""
        # Stop timer
        if hasattr(self, 'check_timer') and self.check_timer.isActive():
            self.check_timer.stop()

        # Close and delete dialog
        if self.info_dialog:
            if self.info_dialog.isVisible():
                self.info_dialog.hide()
            self.info_dialog.deleteLater()
            self.info_dialog = None

        super().closeEvent(event)








# For backward compatibility
InternetStatusWidget = OptimizedInternetStatusWidget