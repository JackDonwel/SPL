#!/usr/bin/env python3
import argparse
import sys
import traceback
from pathlib import Path
from termcolor import cprint
from .interpreter import execute_file, start_repl
from .compiler import Compiler
from .version import __version__

LOGO_FILE_PATH = Path(__file__).parent.parent / "docs" / "logo.txt"

def print_banner():
    """Display the SPL ASCII logo and version information"""
    try:
        logo = LOGO_FILE_PATH.read_text()
        cprint(logo, "cyan", attrs=["bold"])
    except FileNotFoundError:
        pass
    
    cprint(f"\nSwahili Programming Language v{__version__}\n", "yellow")

def validate_file(file_path):
    """Validate SPL file existence and extension"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File '{file_path}' not found")
    if path.suffix != ".spl":
        raise ValueError(f"Invalid extension '{path.suffix}', expected .spl")
    return path.resolve()

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="SPL (Swahili Programming Language) CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "command", 
        choices=["run", "repl", "compile"],
        help="Available commands:\n  run     Execute SPL file\n  repl    Interactive session\n  compile Compile code"
    )
    
    parser.add_argument(
        "file", 
        nargs="?", 
        help="SPL source file (required for run/compile)"
    )
    
    parser.add_argument(
        "--target", 
        choices=["python", "llvm", "wasm"],
        default="python",
        help="Compilation target (default: python)"
    )
    
    parser.add_argument(
        "--output",
        help="Output file path (for compile command)"
    )
    
    parser.add_argument(
        "--sandbox", 
        action="store_true",
        help="Enable restricted execution"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"SPL v{__version__}"
    )
    
    return parser.parse_args()

def handle_compile(args):
    """Handle compilation process"""
    if not args.file or not args.target:
        raise ValueError("Missing file or target for compilation")
    
    source_path = validate_file(args.file)
    output_path = Path(args.output) if args.output else source_path.with_suffix(f".{args.target}")
    
    try:
        compiler = Compiler(source_path.read_text())
        output = compiler.compile(target=args.target)
        output_path.write_text(output)
        cprint(f"\n✅ Successfully compiled to: {output_path}", "green")
        
    except Exception as e:
        raise RuntimeError(f"Compilation failed: {str(e)}") from e

def main():
    args = parse_arguments()
    
    try:
        if args.command == "run":
            if not args.file:
                raise ValueError("Missing SPL file for execution")
            execute_file(validate_file(args.file), sandbox=args.sandbox)
            
        elif args.command == "repl":
            print_banner()
            start_repl()
            
        elif args.command == "compile":
            handle_compile(args)
            
    except Exception as e:
        cprint(f"\n⛔ Error: {str(e)}", "red", attrs=["bold"])
        sys.exit(1)

if __name__ == "__main__":
    main()