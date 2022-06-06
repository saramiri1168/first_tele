import traceback
import requests
import logging
import constants


def prepare_url(url):
    if url.startswith("https://"):
        url = url.removeprefix("https://")
    elif url.startswith("http://"):
        url = url.removeprefix("http://")

    if "/" in url:
        url = url[:url.index("/")]

    if len(url.split(".")) >= 3:
        url = url.removeprefix("www.")
    return url


def validation_url(url) -> tuple[bool, str | None]:
    prepared_url = prepare_url(url)
    if "." in prepared_url:
        if 2 <= len(prepared_url.split(".")[-1]) <= 6:
            return True, prepared_url
    return False, None


def request(method: str, url: str, *args, **kwargs) -> requests.Response | None:
    try:
        r = requests.request(method, url, *args, **kwargs)
        r.raise_for_status()

        return r

    except Exception:
        print(traceback.format_exc(), method, url)
        logging.critical("Unknown message when requesting", traceback.format_exc(), method, url)

    return None


def telegram_req(endpoint: str, **data) -> dict | None:
    r = request(
        "post",
        f"https://api.telegram.org/bot{constants.TG_BOT_TOKEN}/{endpoint}",
        json=data
    )

    try:
        return r.json()
    except ValueError:
        # TODO: Add log
        return None



