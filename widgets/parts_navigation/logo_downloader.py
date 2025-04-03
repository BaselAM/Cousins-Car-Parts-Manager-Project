"""
Utility for downloading and caching car brand logos from the internet.
"""
import os
import hashlib
from PyQt5.QtCore import QObject, QUrl, QDir, QStandardPaths, QThreadPool, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from logger import get_logger

logger = get_logger('logo_downloader')


class LogoSignals(QObject):
    """Signals for the logo downloader."""
    finished = pyqtSignal(str, QPixmap)  # brand_name, pixmap
    error = pyqtSignal(str, str)  # brand_name, error_message


class LogoDownloader(QRunnable):
    """
    Downloads car brand logos from the internet and caches them locally.
    Runs in a separate thread to avoid blocking the UI.
    """

    # Dictionary of major car brand logo URLs
    LOGO_URLS = {
        'audi': 'https://www.carlogos.org/car-logos/audi-logo.png',
        'bmw': 'https://www.carlogos.org/car-logos/bmw-logo.png',
        'chevrolet': 'https://www.carlogos.org/car-logos/chevrolet-logo.png',
        'ford': 'https://www.carlogos.org/car-logos/ford-logo.png',
        'honda': 'https://www.carlogos.org/car-logos/honda-logo.png',
        'hyundai': 'https://www.carlogos.org/car-logos/hyundai-logo.png',
        'kia': 'https://www.carlogos.org/car-logos/kia-logo.png',
        'mazda': 'https://www.carlogos.org/car-logos/mazda-logo.png',
        'mercedes': 'https://www.carlogos.org/car-logos/mercedes-benz-logo.png',
        'nissan': 'https://www.carlogos.org/car-logos/nissan-logo.png',
        'subaru': 'https://www.carlogos.org/car-logos/subaru-logo.png',
        'tesla': 'https://www.carlogos.org/car-logos/tesla-logo.png',
        'toyota': 'https://www.carlogos.org/car-logos/toyota-logo.png',
        'volkswagen': 'https://www.carlogos.org/car-logos/volkswagen-logo.png',
        'volvo': 'https://www.carlogos.org/car-logos/volvo-logo.png',
        # Add more as needed
    }

    # Fallback URL if brand-specific URL is not found
    DEFAULT_LOGO_URL = 'https://www.carlogos.org/logo/car-logos.svg'

    def __init__(self, brand_name):
        super().__init__()
        self.brand_name = brand_name.lower()
        self.signals = LogoSignals()
        self.manager = QNetworkAccessManager()

        # Set up cache directory
        cache_location = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        self.cache_dir = os.path.join(cache_location, 'brand_logos')
        os.makedirs(self.cache_dir, exist_ok=True)

    @pyqtSlot()
    def run(self):
        """Run the logo download task."""
        # First check if the logo is already in cache
        cached_path = self._get_cached_path()
        if os.path.exists(cached_path):
            pixmap = QPixmap(cached_path)
            if not pixmap.isNull():
                logger.debug(f"Using cached logo for {self.brand_name}")
                self.signals.finished.emit(self.brand_name, pixmap)
                return

        # If not in cache, download it
        self._download_logo()

    def _get_cached_path(self):
        """Get the cached file path for this brand."""
        # Use a hash of the brand name for the filename
        filename = f"{self.brand_name.lower()}.png"
        return os.path.join(self.cache_dir, filename)

    def _get_logo_url(self):
        """Get the URL for this brand's logo."""
        # Try to find a specific URL for this brand
        normalized_name = self.brand_name.lower().replace(' ', '')

        # Check for exact matches
        if normalized_name in self.LOGO_URLS:
            return self.LOGO_URLS[normalized_name]

        # Check for partial matches
        for key, url in self.LOGO_URLS.items():
            if key in normalized_name or normalized_name in key:
                return url

        # Use default/generic car logo if no match found
        return self.DEFAULT_LOGO_URL

    def _download_logo(self):
        """Download the logo from the internet."""
        url = QUrl(self._get_logo_url())
        request = QNetworkRequest(url)

        # Create a new network manager for this request
        self.manager = QNetworkAccessManager()
        reply = self.manager.get(request)

        # Connect signals for handling the response
        reply.finished.connect(lambda: self._handle_download_finished(reply))
        reply.error.connect(lambda error_code: self._handle_download_error(reply, error_code))

    def _handle_download_finished(self, reply):
        """Handle successful download completion."""
        if reply.error() == QNetworkReply.NoError:
            # Read the image data
            img_data = reply.readAll()
            pixmap = QPixmap()
            if pixmap.loadFromData(img_data):
                # Save to cache
                cached_path = self._get_cached_path()
                pixmap.save(cached_path)
                logger.debug(f"Downloaded and cached logo for {self.brand_name}")

                # Emit the pixmap
                self.signals.finished.emit(self.brand_name, pixmap)
            else:
                logger.error(f"Failed to create pixmap from downloaded data for {self.brand_name}")
                self.signals.error.emit(self.brand_name, "Invalid image data")

        # Clean up
        reply.deleteLater()

    def _handle_download_error(self, reply, error_code):
        """Handle download errors."""
        error_msg = reply.errorString()
        logger.error(f"Error downloading logo for {self.brand_name}: {error_msg}")
        self.signals.error.emit(self.brand_name, error_msg)

        # Clean up
        reply.deleteLater()


class LogoManager(QObject):
    """
    Manages downloading and caching of brand logos.
    Provides a simple interface for the UI components.
    """

    # Signal emitted when logo is ready
    logo_ready = pyqtSignal(str, QPixmap)  # brand_name, pixmap

    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(4)  # Limit concurrent downloads

        # In-memory cache for already loaded logos
        self.pixmap_cache = {}

    def get_logo(self, brand_name):
        """
        Get a logo for the specified brand.
        Returns immediately if cached, otherwise downloads asynchronously.

        Args:
            brand_name: Name of the brand

        Returns:
            QPixmap: Cached logo if available, otherwise None
        """
        if not brand_name:
            return None

        brand_key = brand_name.lower()

        # Check in-memory cache first
        if brand_key in self.pixmap_cache:
            return self.pixmap_cache[brand_key]

        # Start download if not cached
        downloader = LogoDownloader(brand_name)
        downloader.signals.finished.connect(self._on_logo_downloaded)
        downloader.signals.error.connect(self._on_logo_error)

        self.thread_pool.start(downloader)
        return None

    def _on_logo_downloaded(self, brand_name, pixmap):
        """Handle downloaded logo."""
        brand_key = brand_name.lower()
        self.pixmap_cache[brand_key] = pixmap
        self.logo_ready.emit(brand_name, pixmap)

    def _on_logo_error(self, brand_name, error_msg):
        """Handle logo download error."""
        logger.error(f"Logo download error for {brand_name}: {error_msg}")
        # Could emit a different signal for errors if needed