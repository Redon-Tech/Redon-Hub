"""
    File: /cli.py
    Usage: The CLI.
"""

import argparse
import os
import sys
import asyncio
import subprocess
import json
import shutil
from . import __version__ as version
from .utils.logging import cli_logger
from logging import getLogger

fullInstallDir = [
    "example.config.json",
    "example.env",
    "launcher.py",
    "redonhub",
    "LICENSE.md",
]


_log = getLogger("CLI")


def printHeader():
    print(
        """\x1b[95m
 ███████                ██                     ██      ██         ██     
░██░░░░██              ░██                    ░██     ░██        ░██     
░██   ░██   █████      ░██  ██████  ███████   ░██     ░██ ██   ██░██     
░███████   ██░░░██  ██████ ██░░░░██░░██░░░██  ░██████████░██  ░██░██████ 
░██░░░██  ░███████ ██░░░██░██   ░██ ░██  ░██  ░██░░░░░░██░██  ░██░██░░░██
░██  ░░██ ░██░░░░ ░██  ░██░██   ░██ ░██  ░██  ░██     ░██░██  ░██░██  ░██
░██   ░░██░░██████░░██████░░██████  ███  ░██  ░██     ░██░░██████░██████ 
░░     ░░  ░░░░░░  ░░░░░░  ░░░░░░  ░░░   ░░   ░░      ░░  ░░░░░░ ░░░░░"""
    )


def updatePort(file: str, port: int):
    _log.info(f"Updating port in {file} to {port}")
    if os.path.exists(file):
        with open(file, "r") as f:
            data = f.read()
            data = json.loads(data)
            data["API"]["Port"] = port
            data = json.dumps(data, indent=4)

        with open(file, "w") as f:
            f.write(data)
    else:
        raise FileNotFoundError(f"No {file} found in current directory.")


def main():
    with cli_logger():
        base_parser = argparse.ArgumentParser(
            description="Redon Hub setup and run script."
        )

        base_parser.add_argument(
            "-s",
            "--setup",
            help="Setup the bot in the current directory.",
            action="store_true",
            default=False,
        )
        base_parser.add_argument(
            "-r",
            "--run",
            help="Run the bot in the current directory.",
            action="store_true",
            default=False,
        )
        base_parser.add_argument(
            "-f",
            "--full",
            help="""Install all files, and launch the bot from this directory instead of from the package.
            Usefull if you need to edit the bots code.""",
            action="store_true",
            default=False,
        )
        base_parser.add_argument(
            "-p", "--port", help="Set the port in the config file", type=int
        )

        base_args = base_parser.parse_args()

        cwd = os.getcwd()
        parent = os.path.dirname(os.path.abspath(__file__))

        printHeader()
        _log.info(f"Redon Hub CLI v{version}")

        if base_args.run and base_args.setup:
            sys.exit("Can not run and setup at the same time")

        if base_args.setup == False and base_args.run == False:
            _log.error("No arguments provided. Exiting.")

        if base_args.setup:
            if len(os.listdir(cwd)) > 0:
                sys.exit(
                    "Directory is not empty. Can not setup bot in a non-empty directory."
                )

            if base_args.full:
                # Copy all files to current directory
                _log.info("Copying all files to current directory")
                for dir in fullInstallDir:
                    if os.path.isdir(parent + "/" + dir):
                        _log.info("Copying directory:", dir)
                        shutil.copytree(parent + "/" + dir, cwd + "/" + dir)
                    else:
                        _log.info("Copying file:", dir)
                        if dir.startswith("example."):
                            if dir == "example.env":
                                shutil.copy(parent + "/" + dir, cwd + "/.env")
                            else:
                                shutil.copy(
                                    parent + "/" + dir,
                                    cwd + "/" + dir.replace("example.", ""),
                                )
                            shutil.copy(parent + "/" + dir, cwd + "/")
                        else:
                            shutil.copy(parent + "/" + dir, cwd + "/")

                _log.info(
                    "Installation complete. Please ensure to update .env and config.json with the correct values!"
                )
            else:
                # Copy example.config.json to config.json
                _log.info("Copying example.config.json to config.json")
                shutil.copy(parent + "/example.config.json", cwd + "/config.json")

                # Copy example.env to .env
                _log.info("Copying example.env to .env")
                shutil.copy(parent + "/example.env", cwd + "/.env")

                _log.info(
                    "Installation complete. Please ensure to update .env and config.json with the correct values!"
                )

            if base_args.port:
                try:
                    updatePort(cwd + "/config.json", base_args.port)
                except FileNotFoundError as e:
                    sys.exit(str(e))

            sys.exit(0)

        if base_args.run:
            if not os.path.exists(cwd + "/config.json"):
                _log.error("No config.json found in current directory.")
                sys.exit(
                    "Bot not found error. Please ensure to run --setup before attempting to run the bot."
                )

            if not os.path.exists(cwd + "/.env"):
                _log.error("No .env found in current directory.")
                sys.exit(
                    "Bot not found error. Please ensure to run --setup before attempting to run the bot."
                )

            if base_args.port:
                try:
                    updatePort(cwd + "/config.json", base_args.port)
                except FileNotFoundError as e:
                    sys.exit(str(e))

            if os.path.exists(cwd + "/launcher.py"):
                _log.info(
                    "Found launcher.py in current directory, running that instead."
                )
                subprocess.run(["python", "launcher.py"])
            else:
                from .launcher import run

                asyncio.run(run())

        sys.exit(0)


if __name__ == "__main__":
    main()
