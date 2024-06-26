# Instagram Crawler

Instagram Crawler is a Python script that uses the `instaloader` module to download posts from a specified Instagram account.

## Features

- Downloads all posts from a specified Instagram account.
- Separates downloaded content into images, videos, captions, and profile data.
- Uses a logger to keep track of the download process.

## Installation

1. Clone this repository:

```bash
git clone https://github.com/pnguyen215/instagram-crawler.git
```

2. Install the required Python modules:

```bash
pip3 install -r requirements.txt
```

3. Upgrade the required Python modules:

```bash
pip3 install --upgrade -r requirements.txt
```

## Usage

1. Run the script with the Instagram username as an argument:

```bash
python3 main.py
```

2. When prompted, enter the Instagram username you want to download posts from.

## Docker

1. Build the Docker image

```bash
docker-compose build
```

2. Run the Docker container:

```bash
docker-compose up
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT
