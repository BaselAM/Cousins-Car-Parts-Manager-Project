# ------------------------------------------------------------
# db_transaction.py - Transaction management module
# ------------------------------------------------------------
from contextlib import contextmanager
import threading
import logging


class TransactionManager:
    """Manages database transactions"""

    def __init__(self, connection_manager, logger=None):
        """Initialize with a connection manager"""
        self.connection_manager = connection_manager
        self.logger = logger or logging.getLogger('database.transaction')
        self.lock = threading.RLock()

    @contextmanager
    def transaction(self):
        """Context manager for handling transactions safely"""
        conn = self.connection_manager.connection
        local = self.connection_manager.local

        # Track whether we started a transaction
        transaction_started = False

        with self.lock:
            try:
                # Start a transaction if one is not already in progress
                if not hasattr(local, 'in_transaction') or not local.in_transaction:
                    conn.start_transaction()
                    local.in_transaction = True
                    transaction_started = True
                    thread_id = threading.get_ident()
                    self.logger.debug(f"Thread {thread_id}: Transaction started")

                # Yield control to the caller
                yield

                # Only commit if we started this transaction
                if transaction_started:
                    conn.commit()
                    local.in_transaction = False
                    thread_id = threading.get_ident()
                    self.logger.debug(f"Thread {thread_id}: Transaction committed")

            except Exception as e:
                # Roll back on any exception, but only if we started this transaction
                if transaction_started and hasattr(local, 'in_transaction') and local.in_transaction:
                    try:
                        conn.rollback()
                        local.in_transaction = False
                        thread_id = threading.get_ident()
                        self.logger.debug(f"Thread {thread_id}: Transaction rolled back due to: {e}")
                    except Exception as rollback_error:
                        self.logger.error(f"Error during rollback: {rollback_error}")

                # Re-raise the original exception
                raise

    def begin_transaction(self):
        """Begin a transaction manually"""
        conn = self.connection_manager.connection
        local = self.connection_manager.local

        with self.lock:
            # If already in a transaction, just return
            if hasattr(local, 'in_transaction') and local.in_transaction:
                return True

            try:
                # Start a new transaction
                conn.start_transaction()
                local.in_transaction = True
                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction manually started")
                return True
            except Exception as e:
                self.logger.error(f"Error starting transaction: {e}")
                return False

    def commit_transaction(self):
        """Commit the current transaction manually"""
        conn = self.connection_manager.connection
        local = self.connection_manager.local

        with self.lock:
            # Only commit if we're in a transaction
            if not hasattr(local, 'in_transaction') or not local.in_transaction:
                return True  # Nothing to commit

            try:
                conn.commit()
                local.in_transaction = False
                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction manually committed")
                return True
            except Exception as e:
                self.logger.error(f"Error committing transaction: {e}")
                return False

    def rollback_transaction(self):
        """Roll back the current transaction manually"""
        conn = self.connection_manager.connection
        local = self.connection_manager.local

        with self.lock:
            # Only roll back if we're in a transaction
            if not hasattr(local, 'in_transaction') or not local.in_transaction:
                return True  # Nothing to roll back

            try:
                conn.rollback()
                local.in_transaction = False
                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction manually rolled back")
                return True
            except Exception as e:
                self.logger.error(f"Error rolling back transaction: {e}")
                return False

    def ensure_transaction_state(self, desired_state='ready'):
        """
        Ensure the connection is in the desired transaction state

        Args:
            desired_state: Either 'ready' (no transaction) or 'active' (transaction started)
        """
        local = self.connection_manager.local

        with self.lock:
            current_state = hasattr(local, 'in_transaction') and local.in_transaction

            # If we want 'ready' state (no transaction) but one is active
            if desired_state == 'ready' and current_state:
                return self.commit_transaction()

            # If we want 'active' state (transaction started) but none is active
            elif desired_state == 'active' and not current_state:
                return self.begin_transaction()

            return True  # Already in the desired state