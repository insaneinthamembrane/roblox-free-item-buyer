import pathlib
import time

import requests
from rich.console import Console

cookie = pathlib.Path("cookie.txt").read_text()

session = requests.Session()
session.cookies.update({".ROBLOSECURITY": cookie})

console = Console(highlight=False)


def cprint(color: str, content: str) -> None:
    console.print(f"[ [bold {color}]>[/] ] {content}")


def fetch_items() -> None:
    result = {}
    cursor = ""

    while cursor is not None:
        req = session.get(
            f"https://catalog.roblox.com/v1/search/items/details?creatorTargetId=1&limit=30&maxPrice=0&cursor={cursor}"
        )
        res = req.json()

        if req.status_code == 429:
            cprint("red", "Rate limited. Waiting 20 seconds")
            time.sleep(20)
            continue

        for item in res.get("data", []):
            item_name = item.get("name")
            result[item_name] = item.get("productId")
            cprint("blue", f"Found {item_name}")

        cursor = res.get("nextPageCursor")

    return result


def purchase(name: str, product_id: int) -> None:
    req = session.post("https://auth.roblox.com/v2/login")
    csrf_token = req.headers["x-csrf-token"]

    while True:
        req = session.post(
            f"https://economy.roblox.com/v1/purchases/products/{product_id}",
            json={"expectedCurrency": 1, "expectedPrice": 0, "expectedSellerId": 1},
            headers={"X-CSRF-TOKEN": csrf_token},
        )

        if req.status_code == 429:
            cprint("red", "Rate limited. Waiting 60 seconds")
            time.sleep(60)
            continue

        res = req.json()
        if "reason" in res and res.get("reason") == "AlreadyOwned":
            cprint("yellow", f"{name} is already owned")
            return

        cprint("green", f"Successfully purchased {name}")
        return


def main() -> None:
    free_items = fetch_items()
    for name, product_id in free_items.items():
        purchase(name, product_id)


main()
