import logging
from datetime import datetime
import os


class Logger:
    """
        A logging utility class that writes both to a standard log file and a Markdown file.

        This class manages:
        - Automatic creation of timestamped log directories and files.
        - Writing logs to a standard .log file in a structured text format.
        - Writing logs to a parallel .md file for more user-friendly, readable documentation.
        - Separation of logs into expandable Markdown sections.

        Attributes:
            log_dir (str): The directory where logs are saved. By default, 'logs'.
            logger (logging.Logger): The Python Logger instance for standard logging.
            markdown_log (file object): A file object for the Markdown log file.
        """

    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.__initialize()
        return cls._instance

    def __initialize(self, log_dir="logs"):
        """
            Initializes the Logger by creating a timestamped log directory and configuring both the standard log file and the Markdown log file.

            Args:
                log_dir (str): The directory in which all logs will be saved. Defaults to 'logs'.
        """
        if not hasattr(self, "_initialized"):
            self._initialized = True

        # Ensure the base directory for logs exists
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        # Create a unique subdirectory for this run, based on timestamp
        run_timestamp = datetime.now().strftime("app_%Y-%m-%d_%H-%M-%S")
        self.log_dir = os.path.join(self.log_dir, run_timestamp)
        os.makedirs(self.log_dir, exist_ok=True)

        # Generate filenames for the standard log and markdown log
        log_filename = datetime.now().strftime(f"{run_timestamp}.log")
        log_path = os.path.join(self.log_dir, log_filename)

        log_md_filename = datetime.now().strftime(f"{run_timestamp}.md")
        markdown_log_path = os.path.join(self.log_dir, log_md_filename)

        # Configure the standard logger
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger()

        # Open the markdown log file
        self.markdown_log = open(markdown_log_path, "w", encoding="utf-8")

    def _write_markdown(self, text):
        """
            Writes text to the markdown log file and flushes immediately.

            Args:
                text (str): The text to be written to the Markdown file.
        """
        self.markdown_log.write(text + "\n")
        self.markdown_log.flush()

    def info(self, message):
        self.logger.info(message)
        self._write_markdown(f"- **INFO**: {message}")

    def info_new_section(self, message):
        self.logger.info(message)
        self.__add_markdown_section(f"{message}")


    def info_end_section(self, message):
        self.logger.info(message)
        self._write_markdown(f"- **INFO**: {message}")
        self.__end_markdown_section()

    def warning(self, message):
        """
            Logs a warning-level message to both the standard log file and the Markdown file.

           Args:
               message (str): The message to log.
        """
        self.logger.warning(message)
        self._write_markdown(f"- **WARNING**: {message}")

    def error(self, message):
        """
            Logs an error-level message to both the standard log file and the Markdown file.

            Args:
                message (str): The message to log.
        """
        self.logger.error(message)
        self._write_markdown(f"- **ERROR**: {message}")

    def newline(self):
        """
        Inserts a newline in both the standard log stream and the Markdown file, helping visually separate log segments.
        """
        # Ensure the handler has a stream before writing
        for handler in self.logger.handlers:
            if isinstance(handler, logging.StreamHandler):  # Check if it's a StreamHandler
                handler.stream.write("\n")
                break  # We only need to write once

        # Write a newline to the markdown file
        self._write_markdown("\n")

    def array(self, array, array_title="No data"):
        """
            Logs an array of data to both the standard logger and the Markdown file within a collapsible section.

            Args:
                array (list): The data array to log.
                array_title (str): A title for this section of the log. Default: "No data".
        """
        self.logger.info(f"{array_title}")
        self.logger.info(f"Count: {len(array)}")

        self.__add_markdown_section(f"{array_title} (Count: {len(array)})")
        # Put the array in a fenced code block for Markdown
        self._write_markdown("\n```text\n" + "\n".join(map(str, array)) + "\n```\n")
        self.__end_markdown_section()

        # Log each item in the standard logger
        for item in array:
            self.logger.info(item)
        self.newline()

    def __add_markdown_section(self, title):
        """
            Starts a collapsible Markdown section with a given title.

            Args:
                title (str): The title for the collapsible section.
        """
        self._write_markdown(f"<details><summary><b>{title}</b></summary>\n")

    def __end_markdown_section(self):
        """
            Closes a collapsible Markdown section.
        """
        self._write_markdown("</details>\n")

    def dictionary(self, dict_data, dict_title="No data"):
        """
            Logs a dictionary to both the standard logger and the Markdown file within a collapsible section.

           Args:
               dict_data (dict): The dictionary to log.
               dict_title (str): A title for this section of the log. Default: "No data".
        """
        self.logger.info(f"{dict_title}")
        self.logger.info(f"Count: {len(dict_data.items())}")

        # Start a collapsible section in Markdown
        self._write_markdown(f"<details><summary><b>{dict_title} (Count: {len(dict_data)})</b></summary>\n")
        # Format the dictionary into a JSON-like fenced code block
        self._write_markdown(
            "\n```json\n" + "\n".join(f'"{k}": "{v}"' for k, v in dict_data.items()) + "\n```\n</details>\n")

        # Log each key-value pair in the standard logger
        for key, value in dict_data.items():
            self.logger.info(f"{key}: {value}")
        self.newline()

    def close(self):
        """
            Closes the Markdown log file gracefully, indicating that the import (or run) is complete.
        """
        end_message = "Import successful!"

        self.info(end_message)

        self.markdown_log.close()