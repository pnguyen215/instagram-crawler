import instaloader
import logging
import logging.config
import yaml
import os
import shutil


class Logger:
    def __init__(self, filename_logger):
        with open(filename_logger, "r") as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
        self.logger = logging.getLogger(__name__)


class InstagramCrawler:
    def __init__(self, username, logger):
        self.username = username
        self.logger = logger
        self.ins = instaloader.Instaloader()
        self.profile = instaloader.Profile.from_username(self.ins.context, username)
        self.root_dir = "assets"
        self.image_dir = os.path.join(self.root_dir, username, "images")
        self.video_dir = os.path.join(self.root_dir, username, "videos")
        self.caption_dir = os.path.join(self.root_dir, username, "captions")
        self.profile_dir = os.path.join(self.root_dir, username, "profiles")

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
                self.logger.error("File %s not found, skipping.", file)
            except Exception as e:
                self.logger.error("Error moving file %s: %s", file, e)

    def download_posts(self):
        for post in self.profile.get_posts():
            if post.is_video:
                self.ins.download_post(post, target=self.username)
                self.move_files(".mp4", self.video_dir)
            else:
                self.ins.download_post(post, target=self.username)
                self.move_files(".jpg", self.image_dir)
                self.move_files(".txt", self.caption_dir)
                self.move_files(".json.xz", self.profile_dir)

    def clean_up(self):
        shutil.rmtree(self.username)


def is_docker():
    path = "/proc/self/cgroup"
    return (
        os.path.exists("/.dockerenv")
        or os.path.isfile(path)
        and any("docker" in line for line in open(path))
    )


def main(username, filename_logger):
    logger = Logger(filename_logger)
    logger.logger.info("Loading username %s profile...", username)
    scraper = InstagramCrawler(username, logger)
    scraper.create_directories()
    scraper.download_posts()
    scraper.clean_up()


if __name__ == "__main__":
    if is_docker():
        username = os.getenv("INSTAGRAM_USERNAME")
    else:
        username = input("Enter Instagram's username: ")
    filename = "./config/logger.yaml"
    main(username, filename)
