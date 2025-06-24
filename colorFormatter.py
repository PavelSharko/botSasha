import logging

class ColorFormatter(logging.Formatter):
    RESET = "\x1b[0m"
    YELLOW = "\x1b[33m"
    GREEN = "\x1b[32m"
    ORANGE = "\x1b[38;5;208m"

    def format(self, record):
        msg = super().format(record)
        levelname = record.levelname
        if levelname == "DEBUG":
            prefix = f"{self.YELLOW}[{record.asctime}] DEBUG:{self.RESET} "
            return prefix + record.getMessage()
        elif levelname == "INFO":
            prefix = f"{self.GREEN}[{record.asctime}] INFO:{self.RESET} "
            return prefix + record.getMessage()
        elif levelname == "WARNING":
            return f"{self.ORANGE}{msg}{self.RESET}"
        elif levelname in ("ERROR", "CRITICAL"):
            return f"{self.RED}{msg}{self.RESET}"
        else:
            return msg
