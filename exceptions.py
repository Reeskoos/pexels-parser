import sys
from colorama import Fore
from httpx import ConnectError, ProxyError


class EmptyInputError(Exception):
    """Query string can not be empty."""
    pass


class SpecialCharInputError(Exception):
    """Query string must escape special characters"""
    pass

class NoImagesFoundError(Exception):
    """Response got no images"""
    pass


def error_handler_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EmptyInputError:
            print(Fore.RED + '[ERROR]', 'Input value can not be empty.')
            sys.exit(1)
        except SpecialCharInputError:
            print(Fore.LIGHTRED_EX + '[ERROR]', Fore.RED + 'Input can not contain special characters.')
            sys.exit(1)
        except ConnectError:
            print(Fore.LIGHTRED_EX + '[CONNECTION ERROR]',
                  Fore.RED + 'Failed to connect to server. Check your internet connection and try again.')
            sys.exit(1)
        except ProxyError:
            print(Fore.LIGHTRED_EX + '[PROXIES ERROR]',
                  Fore.RED + 'Failed to connect to server. Check your proxies and try again.')
            sys.exit(1)
        except NoImagesFoundError:
            print(Fore.LIGHTRED_EX + '[ERROR]', Fore.RED + 'No images found.')
            sys.exit(1)
    return wrapper
