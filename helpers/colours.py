from colorama import Fore, Style

# Terminal output styles
INFO = Fore.BLUE
SUCCESS = Fore.GREEN
FAILED = Fore.RED
ERROR = Fore.YELLOW
TEXT = Fore.MAGENTA
RESET = Style.RESET_ALL

def print_banner():
    print(f"{Fore.MAGENTA}{Style.BRIGHT}                   __\n"
          f"               .-/  \\__\n"
          f"              /       @{Fore.CYAN}`---.{Fore.MAGENTA}\n"
          f"             |   (*)      .'{Fore.CYAN}\n"
          f"              \\__/`--'---'{Fore.BLUE}     .---.  .----.  .-.   .-..----. .---.\n"
          f"                /  /       {Fore.CYAN}___| {{_}} |/  {{}}  \\ |  `-'  || {{}}  }}| {{_}}\n"
          f"               /_.'       /__/|____/ \\______/ |__/|__/|___.' |_|  \n"
          f"\n{Fore.CYAN}     AI-Powered JS Vulnerability Scanner {Fore.MAGENTA}•{Fore.BLUE} Red Team CLI Interface{Style.RESET_ALL}\n")