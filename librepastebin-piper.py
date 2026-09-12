#!/usr/bin/env python3

import argparse
import os
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://pastebin.com/api/api_post.php"

VISIBILITY = {
    "public": "0",
    "unlisted": "1",
    "private": "2",
}

EXPIRATION = {
    "N",
    "10M",
    "1H",
    "1D",
    "1W",
    "2W",
    "1M",
}


@dataclass(frozen=True)
class Config:
    api_key: str
    user_key: str | None
    title: str
    language: str
    expiration: str
    visibility: str
    api_url: str


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pastebin",
        description="Create a Pastebin.com paste from stdin.",
        epilog=(
            "Examples:\n"
            "  echo 'hello' | pastebin\n"
            "  cat script.py | pastebin -l python -t 'My Script'\n"
            "  cat file.txt | pastebin -v private -e 1H\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-k",
        "--api-key",
        default=os.getenv("PASTEBIN_API_KEY"),
        help="Pastebin API key or PASTEBIN_API_KEY.",
    )

    parser.add_argument(
        "-u",
        "--user-key",
        default=os.getenv("PASTEBIN_USER_KEY"),
        help="Pastebin user key or PASTEBIN_USER_KEY.",
    )

    parser.add_argument(
        "-t",
        "--title",
        "--topic",
        default="Paste",
        help="Paste title. Default: Paste.",
    )

    parser.add_argument(
        "-l",
        "--language",
        "--lang",
        default="text",
        help="Syntax highlighting language. Default: text.",
    )

    parser.add_argument(
        "-e",
        "--expire",
        default="1D",
        choices=sorted(EXPIRATION),
        help="Expiration: N, 10M, 1H, 1D, 1W, 2W or 1M.",
    )

    parser.add_argument(
        "-v",
        "--visibility",
        default="private",
        choices=sorted(VISIBILITY),
        help="Visibility: public, unlisted or private.",
    )

    parser.add_argument(
        "--api-url",
        default=API_URL,
        help="Pastebin API endpoint.",
    )

    return parser


def read_config(arguments: argparse.Namespace) -> Config:
    if not arguments.api_key:
        raise ValueError(
            "Missing API key. Use --api-key or set PASTEBIN_API_KEY."
        )

    return Config(
        api_key=arguments.api_key,
        user_key=arguments.user_key,
        title=arguments.title,
        language=arguments.language,
        expiration=arguments.expire,
        visibility=arguments.visibility,
        api_url=arguments.api_url,
    )


def read_stdin() -> str:
    content = sys.stdin.read()

    if not content.strip():
        raise ValueError(
            "No input received. Example: echo 'hello' | pastebin"
        )

    return content


def create_form(config: Config, content: str) -> bytes:
    form = {
        "api_dev_key": config.api_key,
        "api_option": "paste",
        "api_paste_code": content,
        "api_paste_name": config.title,
        "api_paste_format": config.language,
        "api_paste_expire_date": config.expiration,
        "api_paste_private": VISIBILITY[config.visibility],
    }

    if config.user_key:
        form["api_user_key"] = config.user_key

    return urlencode(form).encode("utf-8")


def create_request(config: Config, content: str) -> Request:
    return Request(
        config.api_url,
        data=create_form(config, content),
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "pastebin-wrapper/1.0",
        },
    )


def parse_response(response: str) -> str:
    result = response.strip()

    if not result:
        raise RuntimeError("Pastebin returned an empty response.")

    if result.lower().startswith("bad api request"):
        raise RuntimeError(result)

    if result.lower().startswith("error"):
        raise RuntimeError(result)

    return result


def send_request(request: Request) -> str:
    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return parse_response(body)

    except HTTPError as error:
        details = error.read().decode("utf-8", errors="replace").strip()
        details = details or str(error.reason)

        raise RuntimeError(
            f"Pastebin returned HTTP {error.code}: {details}"
        ) from error

    except URLError as error:
        raise RuntimeError(
            f"Could not connect to Pastebin: {error.reason}"
        ) from error

    except TimeoutError as error:
        raise RuntimeError("The Pastebin request timed out.") from error


def create_paste(config: Config, content: str) -> str:
    request = create_request(config, content)
    return send_request(request)


def main(arguments=None) -> int:
    try:
        parser = create_parser()
        parsed_arguments = parser.parse_args(arguments)
        config = read_config(parsed_arguments)
        content = read_stdin()
        paste_url = create_paste(config, content)

        print()
        print("Paste created successfully.")
        print(f"Title:      {config.title}")
        print(f"Language:   {config.language}")
        print(f"Visibility: {config.visibility}")
        print(f"Expires:    {config.expiration}")
        print(f"Link:       {paste_url}")

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled.", file=sys.stderr)
        return 130

    except (ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
