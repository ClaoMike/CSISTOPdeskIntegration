"""
Logger Module
-------------

This module provides a `Logger` class that manages logging both in a standard `.log` file 
and a parallel `.md` (Markdown) file for structured documentation.

The class supports:
- Automatic creation of timestamped log directories and files.
- Writing logs to both a structured `.log` file and a Markdown file for easier readability.
- Collapsible Markdown sections for structured logging.
- Logging lists and dictionaries with improved formatting.

Usage Example:
--------------
    from logger import Logger

    log = Logger()

    log.info("Application started.")
    log.warning("Low disk space.")
    log.error("Critical failure.")

    log.array(["item1", "item2", "item3"], "Sample List")
    log.dictionary({"key1": "value1", "key2": "value2"}, "Configuration Settings")

    log.close()
"""

import logging
from datetime import datetime
import os


class Logger:
    """
    A logging utility class that writes logs both to a `.log` file and a `.md` (Markdown) file.

    Features:
    - Creates a timestamped log directory and files for organization.
    - Logs messages in both structured log format and Markdown.
    - Supports collapsible Markdown sections for better readability.
    - Provides structured logging for lists (`array()`) and dictionaries (`dictionary()`).

    Attributes:
        log_dir (str): Directory where logs are saved. Default is 'logs'.
        logger (logging.Logger): Standard logging instance.
        markdown_log (file object): File object for the Markdown log.
    """

    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):  # Accept additional arguments
        """
                Ensures only one instance of the Logger class exists (Singleton pattern).

                Returns:
                    Logger: The singleton instance of the Logger.
                """
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.__initialize(*args, **kwargs)  # Pass arguments to __initialize
        return cls._instance

    def __initialize(self, log_dir="logs", is_logging=True):
        """
        Initializes the Logger by creating a timestamped log directory and configuring logging.

        Args:
            log_dir (str): Directory where logs will be stored. Default is 'logs'.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

        self.is_logging = is_logging  # ✅ Store logging state

        if not self.is_logging:
            return  # ✅ Skip initialization if logging is disabled

        # Ensure base log directory exists
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        # Create a unique subdirectory for this run, based on timestamp
        run_timestamp = datetime.now().strftime("app_%Y-%m-%d_%H-%M-%S")
        self.log_dir = os.path.join(self.log_dir, run_timestamp)
        os.makedirs(self.log_dir, exist_ok=True)

        # Define log filenames
        log_filename = f"{run_timestamp}.log"
        markdown_filename = f"{run_timestamp}.md"

        log_path = os.path.join(self.log_dir, log_filename)
        markdown_log_path = os.path.join(self.log_dir, markdown_filename)

        # Configure the standard logger
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger()

        # Open the Markdown log file
        self.markdown_log = open(markdown_log_path, "w", encoding="utf-8")

    def info(self, message):
        """Logs an INFO-level message."""
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.info(message)
        self._write_markdown(f"- **INFO**: {message}")

    def info_new_section(self, message):
        """Logs an INFO-level message and starts a new collapsible Markdown section."""
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.info(message)
        self.__add_markdown_section(message)

    def info_end_section(self, message):
        """Logs an INFO-level message and closes the current collapsible Markdown section."""
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.info(message)
        self._write_markdown(f"- **INFO**: {message}")
        self.__end_markdown_section()

    def warning(self, message):
        """
        Logs a WARNING-level message.

        Args:
            message (str): The warning message to log.
        """
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.warning(message)
        self._write_markdown(f"- **WARNING**: {message}")

    def error(self, message):
        """
        Logs an ERROR-level message.

        Args:
            message (str): The error message to log.
        """
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.error(message)
        self._write_markdown(f"- **ERROR**: {message}")

    def newline(self):
        """
        Inserts a newline in both the standard log file and Markdown file for visual separation.
        """
        if not self.is_logging:
            return  # ✅ Skip

        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                handler.stream.write("\n")
                break

        self._write_markdown("\n")

    def array(self, array, array_title="No data"):
        """
        Logs an array of data with a title, using a collapsible Markdown section.

        Args:
            array (list): List of items to log.
            array_title (str): Title for the section. Default: "No data".
        """
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.info(f"{array_title} (Count: {len(array)})")

        self.__add_markdown_section(f"{array_title} (Count: {len(array)})")
        self._write_markdown("\n```text\n" + "\n".join(map(str, array)) + "\n```\n")
        self.__end_markdown_section()

        for item in array:
            self.logger.info(item)

        self.newline()

    def dictionary(self, dict_data, dict_title="No data"):
        """
        Logs a dictionary with a title, using a collapsible Markdown section.

        Args:
            dict_data (dict): Dictionary to log.
            dict_title (str): Title for the section. Default: "No data".
        """
        if not self.is_logging:
            return  # ✅ Skip

        self.logger.info(f"{dict_title} (Count: {len(dict_data)})")

        self._write_markdown(f"<details><summary><b>{dict_title} (Count: {len(dict_data)})</b></summary>\n")
        self._write_markdown(
            "\n```json\n" + "\n".join(f'"{k}": "{v}"' for k, v in dict_data.items()) + "\n```\n</details>\n"
        )

        for key, value in dict_data.items():
            self.logger.info(f"{key}: {value}")

        self.newline()

    def close(self):
        """
        Closes the Markdown log file, indicating that logging has finished.
        """
        if not self.is_logging:
            return  # ✅ Skip

        end_message = "Script's execution ENDED!"
        self.info(end_message)
        self.markdown_log.close()

    def _write_markdown(self, text):
        """
        Writes text to the Markdown log file and flushes immediately.

        Args:
            text (str): The text to be written.
        """
        self.markdown_log.write(text + "\n")
        self.markdown_log.flush()

    def __add_markdown_section(self, title):
        """
        Starts a collapsible Markdown section.

        Args:
            title (str): The title of the collapsible section.
        """
        self._write_markdown(f"<details><summary><b>{title}</b></summary>\n")

    def __end_markdown_section(self):
        """Closes a collapsible Markdown section."""
        self._write_markdown("</details>\n")
