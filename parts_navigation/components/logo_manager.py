"""
LogoManager component for downloading and caching brand logos.

A premium component that manages the downloading, caching, and display of
brand logos with elegant animation and error handling.
"""
import os
import hashlib
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import (QObject, QUrl, QDir, QStandardPaths,
                          QThreadPool, QRunnable, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

from logger import get_logger

logger = get_logger('parts_navigation.logo_manager')


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
        'alfa romeo': 'https://www.carlogos.org/car-logos/alfa-romeo-logo.png',
        'bentley': 'https://www.carlogos.org/car-logos/bentley-logo.png',
        'bugatti': 'https://www.carlogos.org/car-logos/bugatti-logo.png',
        'cadillac': 'https://www.carlogos.org/car-logos/cadillac-logo.png',
        'chrysler': 'https://www.carlogos.org/car-logos/chrysler-logo.png',
        'citroen': 'https://www.carlogos.org/car-logos/citroen-logo.png',
        'dodge': 'https://www.carlogos.org/car-logos/dodge-logo.png',
        'ferrari': 'https://www.carlogos.org/car-logos/ferrari-logo.png',
        'fiat': 'https://www.carlogos.org/car-logos/fiat-logo.png',
        'jaguar': 'https://www.carlogos.org/car-logos/jaguar-logo.png',
        'jeep': 'https://www.carlogos.org/car-logos/jeep-logo.png',
        'lamborghini': 'https://www.carlogos.org/car-logos/lamborghini-logo.png',
        'land rover': 'https://www.carlogos.org/car-logos/land-rover-logo.png',
        'lexus': 'https://www.carlogos.org/car-logos/lexus-logo.png',
        'mini': 'https://www.carlogos.org/car-logos/mini-logo.png',
        'mitsubishi': 'https://www.carlogos.org/car-logos/mitsubishi-logo.png',
        'opel': 'https://www.carlogos.org/car-logos/opel-logo.png',
        'peugeot': 'https://www.carlogos.org/car-logos/peugeot-logo.png',
        'porsche': 'https://www.carlogos.org/car-logos/porsche-logo.png',
        'renault': 'https://www.carlogos.org/car-logos/renault-logo.png',
        'rolls royce': 'https://www.carlogos.org/car-logos/rolls-royce-logo.png',
        'saab': 'https://www.carlogos.org/car-logos/saab-logo.png',
        'seat': 'https://www.carlogos.org/car-logos/seat-logo.png',
        'skoda': 'https://www.carlogos.org/car-logos/skoda-logo.png',
        'suzuki': 'https://www.carlogos.org/car-logos/suzuki-logo.png',
    }

    # Fallback URL if brand-specific URL is not found
    DEFAULT_LOGO_URL = 'https://www.carlogos.org/logo/car-logos.svg'

    def __init__(self, brand_name):
        """
        Initialize the logo downloader.

        Args:
            brand_name: Name of the car brand to download logo for
        """
        super().__init__()
        self.brand_name = brand_name.lower()
        self.signals = LogoSignals()

        # Remove network manager creation from constructor
        # Network operations must happen in the worker thread
        self.current_reply = None

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
        filename = f"{self.brand_name.lower().replace(' ', '_')}.png"
        return os.path.join(self.cache_dir, filename)

    def _get_logo_url(self):
        """Get the URL for this brand's logo."""
        # Try to find a specific URL for this brand
        normalized_name = self.brand_name.lower().replace(' ', '')

        # Check for exact matches
        if self.brand_name in self.LOGO_URLS:
            return self.LOGO_URLS[self.brand_name]

        # Check normalized name
        if normalized_name in self.LOGO_URLS:
            return self.LOGO_URLS[normalized_name]

        # Check for partial matches
        for key, url in self.LOGO_URLS.items():
            key_normalized = key.lower().replace(' ', '')
            if key_normalized in normalized_name or normalized_name in key_normalized:
                return url

        # Use default/generic car logo if no match found
        return self.DEFAULT_LOGO_URL

    def _download_logo(self):
        """Download the logo from the internet."""
        url = QUrl(self._get_logo_url())
        request = QNetworkRequest(url)

        # Create a new network manager in the worker thread
        self.manager = QNetworkAccessManager()

        # Store the reply as instance variable
        self.current_reply = self.manager.get(request)

        # Connect signals for handling the response - use direct connections, not lambdas
        self.current_reply.finished.connect(self._handle_download_finished)
        self.current_reply.error.connect(self._handle_download_error)

    def _handle_download_finished(self):
        """Handle successful download completion."""
        # Use the stored reply
        reply = self.current_reply

        if reply and reply.error() == QNetworkReply.NoError:
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
        if reply:
            reply.deleteLater()
            self.current_reply = None  # Clear the reference

        # Also clean up the manager
        if hasattr(self, 'manager'):
            self.manager.deleteLater()

    def _handle_download_error(self, error_code):
        """Handle download errors."""
        reply = self.current_reply
        if reply:
            error_msg = reply.errorString()
            logger.error(f"Error downloading logo for {self.brand_name}: {error_msg}")
            self.signals.error.emit(self.brand_name, error_msg)

            # Clean up
            reply.deleteLater()
            self.current_reply = None  # Clear the reference

        # Also clean up the manager
        if hasattr(self, 'manager'):
            self.manager.deleteLater()


class LogoManager(QObject):
    """
    Manages downloading and caching of brand logos.
    Provides a simple interface for UI components.
    """
    # Signal emitted when logo is ready
    logo_ready = pyqtSignal(str, QPixmap)  # brand_name, pixmap

    def __init__(self, parent=None):
        """Initialize the logo manager."""
        super().__init__(parent)
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(4)  # Limit concurrent downloads

        # In-memory cache for already loaded logos
        self.pixmap_cache = {}

        # Set up cache directory
        cache_location = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        self.cache_dir = os.path.join(cache_location, 'brand_logos')
        os.makedirs(self.cache_dir, exist_ok=True)

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

        # Check disk cache
        cached_path = self._get_cached_path(brand_name)
        if os.path.exists(cached_path):
            pixmap = QPixmap(cached_path)
            if not pixmap.isNull():
                # Store in memory cache
                self.pixmap_cache[brand_key] = pixmap
                return pixmap

        # Start download if not cached
        downloader = LogoDownloader(brand_name)
        downloader.signals.finished.connect(self._on_logo_downloaded)
        downloader.signals.error.connect(self._on_logo_error)

        self.thread_pool.start(downloader)
        return None

    def _get_cached_path(self, brand_name):
        """
        Get the cached file path for a brand.

        Args:
            brand_name: Name of the brand

        Returns:
            str: Full path to the cached file
        """
        # Use the same filename format as LogoDownloader
        filename = f"{brand_name.lower().replace(' ', '_')}.png"
        return os.path.join(self.cache_dir, filename)

    def _on_logo_downloaded(self, brand_name, pixmap):
        """Handle downloaded logo."""
        brand_key = brand_name.lower()
        self.pixmap_cache[brand_key] = pixmap
        self.logo_ready.emit(brand_name, pixmap)

    def _on_logo_error(self, brand_name, error_msg):
        """Handle logo download error."""
        logger.error(f"Logo download error for {brand_name}: {error_msg}")
        # Could emit a different signal for errors if needed

    def preload_logos(self, brand_names):
        """
        Preload logos for a list of brands in the background.

        Args:
            brand_names: List of brand names to preload
        """
        logger.info(f"Preloading logos for {len(brand_names)} brands")

        # Set maximum thread count based on available cores
        import multiprocessing
        max_threads = min(8, max(2, multiprocessing.cpu_count() - 1))
        self.thread_pool.setMaxThreadCount(max_threads)

        # Throttling for batch operations
        batch_size = 5
        preloaded_count = 0

        for i in range(0, len(brand_names), batch_size):
            batch = brand_names[i:i + batch_size]
            for brand_name in batch:
                if brand_name and brand_name.lower() not in self.pixmap_cache:
                    # Check if already in disk cache
                    cached_path = self._get_cached_path(brand_name)
                    if os.path.exists(cached_path):
                        pixmap = QPixmap(cached_path)
                        if not pixmap.isNull():
                            self.pixmap_cache[brand_name.lower()] = pixmap
                            preloaded_count += 1
                            continue

                    # Start download for non-cached logos
                    downloader = LogoDownloader(brand_name)
                    downloader.signals.finished.connect(self._on_logo_downloaded)
                    downloader.signals.error.connect(self._on_logo_error)
                    self.thread_pool.start(downloader)

            # Allow UI updates between batches
            QApplication.processEvents()

        logger.info(f"Found {preloaded_count} already cached logos out of {len(brand_names)}")
    def get_logo_sync(self, brand_name):
        """
        Get a logo synchronously from cache only.

        Args:
            brand_name: Name of the brand

        Returns:
            QPixmap: Cached logo if available, otherwise None
        """
        if not brand_name:
            return None

        brand_key = brand_name.lower()

        # Check in-memory cache
        if brand_key in self.pixmap_cache:
            return self.pixmap_cache[brand_key]

        # Check disk cache
        cached_path = self._get_cached_path(brand_name)
        if os.path.exists(cached_path):
            pixmap = QPixmap(cached_path)
            if not pixmap.isNull():
                # Store in memory cache
                self.pixmap_cache[brand_key] = pixmap
                return pixmap

        return None