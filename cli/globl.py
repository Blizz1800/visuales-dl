from configparser import ConfigParser
from .database import DB


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
        self.download_id = None
        self.db = DB(self.config.get('database', 'filename'))


globl = Globals()
config = globl.config
