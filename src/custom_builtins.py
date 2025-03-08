#!/usr/bin/env python3
"""
Custom Built-ins for SPL (Swahili Programming Language)
Provides core built-in functions with Swahili names.
"""

import sys
import requests
import readline
import math
import json
from typing import Any, Iterable, Callable, List, Dict

# Constants
KWELI = True
SIKWELI = False
HAKUNA = None

# Core I/O Functions
def chapisha(*args: Any, **kwargs: Any) -> None:
    """Chapisha - Print output"""
    print(*args, **kwargs)

def soma(prompt: str = "") -> str:
    """Soma - Read input from user"""
    return input(prompt)

# Data Operations
def orodha(iterable: Iterable = ()) -> list:
    """Orodha - Create list from iterable"""
    return list(iterable)

def kamusi(**kwargs: Any) -> dict:
    """Kamusi - Create dictionary"""
    return kwargs

def urefu(iterable: Iterable) -> int:
    """Urefu - Get length of collection"""
    return len(iterable)

# Mathematical Functions
def jumlisha(namba: Iterable[float]) -> float:
    """Jumlisha - Sum numbers"""
    return sum(namba)

def kiasi(namba: Iterable[float]) -> float:
    """Kiasi - Product of numbers"""
    return math.prod(namba)

def kipeo(x: float, y: float) -> float:
    """Kipeo - Exponentiation (x^y)"""
    return x ** y

def mzizi(x: float, n: float = 2) -> float:
    """Mzizi - Nth root of number"""
    return x ** (1/n)

# String Operations
def gawa(mshono: str, kigawanyiko: str = " ") -> list:
    """Gawa - Split string"""
    return mshono.split(kigawanyiko)

def unganisha(vipande: Iterable, kiunganishi: str = "") -> str:
    """Unganisha - Join elements"""
    return kiunganishi.join(map(str, vipande))

def herufi_kubwa(mshono: str) -> str:
    """Herufi Kubwa - Uppercase"""
    return mshono.upper()

def herufi_ndogo(mshono: str) -> str:
    """Herufi Ndogo - Lowercase"""
    return mshono.lower()

# File Operations
def fungua(jina: str, hali: str = "r") -> Any:
    """Fungua - Open file"""
    return open(jina, hali)

def andika(jina: str, yaliyomo: str) -> None:
    """Andika - Write to file"""
    with open(jina, "w") as faili:
        faili.write(yaliyomo)

# Network Operations
def pakua(url: str, njia: str = "GET", **mazingira: Any) -> Any:
    """Pakua - Make HTTP request"""
    try:
        majibu = requests.request(njia, url, **mazingira)
        majibu.raise_for_status()
        return majibu.json() if 'application/json' in majibu.headers.get('content-type', '') else majibu.text
    except Exception as kosa:
        chapisha(f"Kosa la mtandao: {kosa}")
        return HAKUNA

# Functional Programming
def panga(kitendo: Callable, iterable: Iterable) -> List[Any]:
    """Panga - Apply function to items"""
    return list(map(kitendo, iterable))

def chuja(kitendo: Callable, iterable: Iterable) -> List[Any]:
    """Chuja - Filter items"""
    return list(filter(kitendo, iterable))

def punguza(kitendo: Callable, iterable: Iterable, thamani_awali: Any = None) -> Any:
    """Punguza - Reduce collection"""
    from functools import reduce
    return reduce(kitendo, iterable, thamani_awali) if thamani_awali else reduce(kitendo, iterable)

# Type Conversion
def kamili(thamani: Any) -> int:
    """Kamili - Convert to integer"""
    return int(thamani)

def desimali(thamani: Any) -> float:
    """Desimali - Convert to float"""
    return float(thamani)

def mshono(thamani: Any) -> str:
    """Mshono - Convert to string"""
    return str(thamani)

# System Operations
def tazama(jina: str) -> None:
    """Tazama - List directory contents"""
    from os import listdir
    chapisha("\n".join(listdir(jina)))

def simamisha(muda: float) -> None:
    """Simamisha - Sleep for seconds"""
    from time import sleep
    sleep(muda)

# REPL Functions
def msaada(kipengele: Any = HAKUNA) -> None:
    """Msaada - Show help information"""
    if kipengele is HAKUNA:
        chapisha("Vifaa vya SPL:")
        chapisha(", ".join(sorted(CUSTOM_BUILTINS.keys())))
    else:
        help(kipengele)

def repl(mazingira_ya_globals: Dict[str, Any] = None) -> None:
    """REPL - Kuingilia kwa Mstari wa Amri"""
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    
    mazingira = mazingira_ya_globals or CUSTOM_BUILTINS.copy()
    mazingira['msaada'] = msaada
    
    chapisha("SPL REPL. Andika 'msaada()' kwa usaidizi. 'ondoka()' kuacha.")
    while KWELI:
        try:
            mstari = soma(">>> ")
            if mstari.strip() == "ondoka()":
                break
            try:
                matokeo = eval(mstari, mazingira)
                if matokeo is not HAKUNA:
                    chapisha(matokeo)
            except SyntaxError:
                exec(mstari, mazingira)
        except (EOFError, KeyboardInterrupt):
            chapisha("\nKuacha SPL...")
            break
        except Exception as kosa:
            chapisha(f"Kosa: {kosa}")

# Dictionary of all built-in functions
CUSTOM_BUILTINS = {
    # Core I/O
    'chapisha': chapisha,
    'soma': soma,
    
    # Data Structures
    'orodha': orodha,
    'kamusi': kamusi,
    'urefu': urefu,
    
    # Math
    'jumlisha': jumlisha,
    'kiasi': kiasi,
    'kipeo': kipeo,
    'mzizi': mzizi,
    
    # Strings
    'gawa': gawa,
    'unganisha': unganisha,
    'herufi_kubwa': herufi_kubwa,
    'herufi_ndogo': herufi_ndogo,
    
    # Files
    'fungua': fungua,
    'andika': andika,
    
    # Network
    'pakua': pakua,
    
    # Functional
    'panga': panga,
    'chuja': chuja,
    'punguza': punguza,
    
    # Type Conversion
    'kamili': kamili,
    'desimali': desimali,
    'mshono': mshono,
    
    # System
    'tazama': tazama,
    'simamisha': simamisha,
    
    # Constants
    'kweli': KWELI,
    'sikweli': SIKWELI,
    'hakuna': HAKUNA
}

if __name__ == '__main__':
    repl()