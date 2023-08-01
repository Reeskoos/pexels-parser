import sys
import httpx


from colorama import Fore


class EmptyInputException(Exception):
    """Query string can not be empty."""
    pass


class SpecialCharInputException(Exception):
    """Query string must escape special characters"""
    pass

class NoImagesFoundException(Exception):
    """Response got no images"""
    pass


def error_handler_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except EmptyInputException:
            print(Fore.RED + '[ERROR]', 'Input value can not be empty.')
            sys.exit(1)
        except SpecialCharInputException:
            print(Fore.LIGHTRED_EX + '[ERROR]', Fore.RED + 'Input can not contain special characters.')
            sys.exit(1)
        except httpx.ConnectError:
            print(Fore.LIGHTRED_EX + '[ERROR]',
                  Fore.RED + 'Failed to connect to server. Check your internet connection and try again.')
            sys.exit(1)
        except httpx.ProxyError:
            print(Fore.LIGHTRED_EX + '[ERROR]',
                  Fore.RED + 'Failed to connect to server. Check your proxies and try again.')
            sys.exit(1)
        except NoImagesFoundException:
            print(Fore.LIGHTRED_EX + '[ERROR]', Fore.RED + 'No images found.')
            sys.exit(1)
    return wrapper
