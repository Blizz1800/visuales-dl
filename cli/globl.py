from configparser import ConfigParser


class Globals:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read('config.ini')
        self.args = {}
        self.extensions = ["avi", "srt", "mkv", "mpg", "mp4"]
        self.VISITED = []
        self.fileList = []
        self.base_folder = ""
        self.WEB_SITE = ""
        self.LINKS = []


globl = Globals()
config = globl.config
