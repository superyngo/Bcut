import nodriver as nd
from nodriver import Tab, Browser
from nodriver.cdp import network
from pathlib import Path
import time
from weakref import WeakValueDictionary
from ...utils import composer
from .types import MyDriverConfig

__all__: list[str] = ["init_my_driver", "browser_instances"]

# Create a WeakValueDictionary
response_codes: WeakValueDictionary[str, int] = WeakValueDictionary()


async def get_response(tab: Tab, url: str) -> int:

    await tab.send(network.enable())

    global response_codes
    # Add a handler for ResponseReceived events
    tab.add_handler(
        network.ResponseReceived,
        lambda e: (
            response_codes.update({e.response.url: e.response.status})
            if e.response.url == url
            else None
        ),
    )
    await tab.get(url)

    while response_codes.get(url) is None:
        time.sleep(1)

    await tab.send(network.disable())
    return response_codes[url]


# Multiton state
browser_instances: WeakValueDictionary[Path, Browser] = WeakValueDictionary()


async def init_my_driver(browser_config: MyDriverConfig | None = None) -> Tab:
    """init a driver

    Args:
        browser_config (MyDriverConfig | None, optional): config for driver/browser. Defaults to None.

    Returns:
        uc.Browser: browser
    """
    global browser_instances
    browser_config = browser_config or {}
    browser_id: Path = browser_config.get("user_data_dir", Path())

    if browser_id in browser_instances and not browser_instances[browser_id].stopped:
        browser: Browser = browser_instances[browser_id]
    else:
        browser: Browser = await nd.start(**browser_config)

    tab: Tab = await browser.get("about:blank")

    do_compose: int = composer.compose(tab, {"get_response": get_response})
    browser_instances[browser_id] = browser

    return tab


# Restrart not working yet
# async def _restart(browser: Browser) -> None:
#     await self.stop()
#     browser_config = {
#         k: v
#         for (k, v) in self.config.__dict__.items()
#         if k in ["user_data_dir", "browser_executable_path"]
#     }
#     browser_id: Path = browser_config.get("user_data_dir", Path())
#     browser_instances[browser_id] = await nd.start(**browser_config)
#     self = browser_instances[browser_id]
