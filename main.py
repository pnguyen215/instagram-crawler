import instaloader
import logging
import logging.config
import yaml
import os
import shutil
import sys


class Configs:
    def __init__(self, filename):
        self.filename = {}
        self._load_config(filename)

    def _load_config(self, filename):
        with open(filename, "r") as f:
            self.filename = yaml.safe_load(f)

    def get(self, path: str, default=None, cast_type=None):
        keys = path.split(".")
        current_level = self.filename
        for key in keys:
            if key in current_level:
                current_level = current_level[key]
            else:
                return self._cast_default(default, cast_type)
        return self._cast_value(current_level, cast_type)

    def _cast_default(self, default, cast_type):
        if default is None:
            return default
        return self._cast_value(default, cast_type)

    def _cast_value(self, value, cast_type):
        if cast_type is None or value is None:
            return value
        try:
            return cast_type(value)
        except ValueError:
            return value

    def __repr__(self):
        return str(self.filename)


class Logger:
    def __init__(self, filename_logger):
        with open(filename_logger, "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
        self.logger = logging.getLogger(__name__)


class InstagramCrawler:
    def __init__(self, username: str, logger: Logger, config: Configs):
        self.username = username
        self.logger: Logger = logger
        self.config: Configs = config
        self.ins = instaloader.Instaloader()
        self.root_dir = self.config.get(
            "directories.root", default="assets", cast_type=str
        )
        self.image_dir = os.path.join(
            self.root_dir,
            username,
            self.config.get(
                "directories.types.picture", default="images", cast_type=str
            ),
        )
        self.video_dir = os.path.join(
            self.root_dir,
            username,
            self.config.get("directories.types.video", default="videos", cast_type=str),
        )
        self.caption_dir = os.path.join(
            self.root_dir,
            username,
            self.config.get(
                "directories.types.caption", default="captions", cast_type=str
            ),
        )
        self.profile_dir = os.path.join(
            self.root_dir,
            username,
            self.config.get(
                "directories.types.profile", default="profiles", cast_type=str
            ),
        )

    def create_directories(self):
        os.makedirs(self.image_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)
        os.makedirs(self.caption_dir, exist_ok=True)
        os.makedirs(self.profile_dir, exist_ok=True)

    def move_files(self, file_extension, target_dir):
        files = [f for f in os.listdir(self.username) if f.endswith(file_extension)]
        for file in files:
            try:
                src = os.path.join(self.username, file)
                dst = os.path.join(target_dir, file)
                if not os.path.exists(dst):
                    shutil.move(src, dst)
            except FileNotFoundError:
                self.logger.logger.error("File %s not found, skipping.", file)
            except Exception as e:
                self.logger.logger.error("Error moving file %s: %s", file, e)

    def download_posts_by_username_context(self):
        ctx = self.access_by_username_context()
        if not ctx:
            return
        self.download_posts(ctx)

    def download_posts_by_credentials_context(self, username, password):
        ctx = self.access_by_credentials_context(username, password)
        if not ctx:
            return
        self.download_posts(ctx)

    def download_posts(self, ctx: instaloader.Profile):
        try:
            for post in ctx.get_posts():
                if post.is_video:
                    self.ins.download_post(post, target=self.username)
                    self.move_files(".mp4", self.video_dir)
                else:
                    self.ins.download_post(post, target=self.username)
                    self.move_files(".jpg", self.image_dir)
                    self.move_files(".txt", self.caption_dir)
                    self.move_files(".json.xz", self.profile_dir)
        except Exception as e:
            self.logger.logger.error("Error downloading posts: %s", e)

    def execute(self):
        enabled: bool = self.config.get(
            "instagram.enabled", default=False, cast_type=bool
        )
        if enabled:
            username: str = self.config.get("instagram.username", cast_type=str)
            password: str = self.config.get("instagram.password", cast_type=str)
            self.download_posts_by_credentials_context(username, password)
        else:
            self.download_posts_by_username_context()

    def access_by_username_context(self):
        try:
            return instaloader.Profile.from_username(self.ins.context, self.username)
        except Exception as e:
            self.logger.logger.error(
                "Error fetching by username: %s, %s",
                self.username,
                e,
            )
            return None

    def access_by_credentials_context(self, username, password):
        try:
            self.ins.login(username, password)
            return instaloader.Profile.from_username(self.ins.context, self.username)
        except Exception as e:
            self.logger.logger.error("Error logging by username: %s, %s", username, e)
            return None

    def clean_up(self):
        if os.path.exists(self.username):
            shutil.rmtree(self.username)
        else:
            self.logger.logger.warning(
                "Directory %s does not exist, nothing to remove.", self.username
            )


def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


def main(username, filename_logger, filename_config):
    scraper = InstagramCrawler(
        username, Logger(filename_logger), Configs(filename_config)
    )
    scraper.create_directories()
    scraper.execute()
    scraper.clean_up()


def execute():
    if is_docker():
        username = os.getenv("INSTAGRAM_USERNAME")
    else:
        username = input("Enter Instagram's username: ")
    filename_logger = "./config/logger.yaml"
    filename_config = "./config/application.yaml"
    main(username, filename_logger, filename_config)


def execute_with_args():
    if len(sys.argv) != 4:
        print("Usage: python3 main.py <filename_logger> <filename_config> <username>")
        sys.exit(1)
    filename_logger = sys.argv[1]
    filename_config = sys.argv[2]
    username = sys.argv[3]
    main(username, filename_logger, filename_config)


if __name__ == "__main__":
    execute_with_args()
