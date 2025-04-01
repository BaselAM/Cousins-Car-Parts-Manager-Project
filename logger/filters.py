"""
Custom filters for the logging system.
"""
import logging


class ModuleFilter(logging.Filter):
    """Filter logs based on module name."""

    def __init__(self, module_name):
        super().__init__()
        self.module_name = module_name

    def filter(self, record):
        return record.name.startswith(self.module_name)


class ExcludeFilter(logging.Filter):
    """Filter out logs matching the specified criteria."""

    def __init__(self, exclude_pattern):
        super().__init__()
        self.exclude_pattern = exclude_pattern

    def filter(self, record):
        # Return False if the message matches the exclusion pattern
        return self.exclude_pattern not in record.getMessage()


class SensitiveDataFilter(logging.Filter):
    """Filter sensitive data from log records."""

    SENSITIVE_FIELDS = ['password', 'credit_card', 'token', 'secret']

    def filter(self, record):
        if not isinstance(record.msg, str):
            return True

        # Replace sensitive data with asterisks
        msg = record.msg
        for field in self.SENSITIVE_FIELDS:
            if field in msg.lower():
                # Use regular expression to replace the sensitive data
                import re
                pattern = f"({field}=)'[^']*'"
                msg = re.sub(pattern, r"\1'*****'", msg, flags=re.IGNORECASE)
                pattern = f'({field}=)"[^"]*"'
                msg = re.sub(pattern, r'\1"*****"', msg, flags=re.IGNORECASE)

        record.msg = msg
        return True