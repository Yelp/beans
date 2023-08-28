import gzip
import json
import os
import subprocess
from argparse import ArgumentParser
from base64 import b64decode
from base64 import b64encode
from pathlib import Path

CONFIG_FILES = (
    "api/client_secrets.json",
    "api/config.yaml",
    "frontend/lib/config.json",
)
BEANS_CONFIG_ENV = "YELP_BEANS_CONFIG"


def create_parser() -> ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument("action", choices=("print", "load_from_env"))
    return parser


def get_git_root() -> Path:
    try:
        res = subprocess.run(
            ("git", "rev-parse", "--show-toplevel"),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"{e.stdout=}\n{e.stderr=}")
        raise
    return Path(res.stdout.strip())


def print_config_as_str() -> None:
    git_root = get_git_root()
    configs = {}
    for config_filepath in CONFIG_FILES:
        config_file = git_root / config_filepath
        configs[config_filepath] = config_file.read_text()

    configs_as_str = json.dumps(configs)
    print(b64encode(gzip.compress(configs_as_str.encode())).decode())


def load_config_from_env() -> None:
    if BEANS_CONFIG_ENV not in os.environ:
        print(f"{BEANS_CONFIG_ENV} not in the environment. Not writing configs")
        return

    git_root = get_git_root()
    configs_as_str = gzip.decompress(b64decode(os.environ[BEANS_CONFIG_ENV]))
    configs = json.loads(configs_as_str)

    for config_filepath, config in configs.items():
        config_file = git_root / config_filepath
        config_file.write_text(config)


def main():
    args = create_parser().parse_args()
    if args.action == "print":
        print_config_as_str()
    elif args.action == "load_from_env":
        load_config_from_env()
    else:
        raise ValueError("Unsupported action")


if __name__ == "__main__":
    main()
