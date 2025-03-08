#!/usr/bin/env python3
"""
SPL Runtime Module - Enhanced
"""
import gc
import ast
import sys
import signal
import logging
from types import ModuleType
from typing import Any, Dict, Optional, Set
from copy import deepcopy
from hashlib import sha256

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityViolation(Exception):
    """Exception raised for security policy violations"""
    pass

class ImmutabilityError(RuntimeError):
    """Exception raised for immutability violations"""
    pass

class ResourceLimitExceeded(Exception):
    """Exception raised when resource limits are exceeded"""
    pass

class RuntimeEnvironment:
    def __init__(self, security_policy: Optional[Dict[str, Any]] = None):
        self.immutable_store: Dict[str, bytes] = {}  # name: hash
        self.security_policy = security_policy or self.default_security_policy()
        self.original_modules = set(sys.modules.keys())
        
        # Resource limits
        self.timeout = 5  # seconds
        self.max_memory = 128 * 1024 * 1024  # 128MB

    def default_security_policy(self) -> Dict[str, Any]:
        """Return a strict default security policy"""
        return {
            'allowed_builtins': {
                'print', 'range', 'len', 'min', 'max', 'sum',
                'int', 'float', 'str', 'bool', 'list', 'dict'
            },
            'allowed_modules': set(),
            'enable_network': False,
            'enable_filesystem': False,
            'enable_subprocess': False
        }

    def register_immutable(self, name: str, obj: Any) -> None:
        """Register an immutable object with hash verification"""
        if name in self.immutable_store:
            raise ImmutabilityError(f"{name} is already registered as immutable")
            
        self.immutable_store[name] = self._hash_object(obj)
        logger.info(f"Registered immutable variable '{name}'")

    def verify_immutability(self, name: str, current_obj: Any) -> bool:
        """Verify if a registered object remains immutable"""
        if name not in self.immutable_store:
            raise ImmutabilityError(f"No immutability registered for '{name}'")
            
        current_hash = self._hash_object(current_obj)
        if self.immutable_store[name] != current_hash:
            raise ImmutabilityError(f"Immutable variable '{name}' has been modified")
            
        return True

    def _hash_object(self, obj: Any) -> bytes:
        """Generate a secure hash of an object's state"""
        return sha256(str(obj).encode()).digest()

    def manual_gc(self, generation: int = 2) -> Dict[str, int]:
        """Perform manual garbage collection with detailed reporting"""
        collected = {0: gc.collect(generation)}
        stats = {
            'collected': collected[0],
            'uncollectable': len(gc.garbage),
            'generation': gc.get_count()
        }
        logger.info(f"GC Collected {stats['collected']} objects")
        return stats

    def run_sandboxed(self, code: str, locals_dict: Optional[Dict] = None) -> Dict[str, Any]:
        """Execute code in a secure sandboxed environment"""
        self._validate_code_security(code)
        self._clean_environment()
        
        # Prepare restricted environment
        safe_globals = self._create_safe_globals()
        locals_dict = locals_dict or {}
        
        try:
            # Set up resource limits
            signal.signal(signal.SIGALRM, self._handle_timeout)
            signal.alarm(self.timeout)
            
            # Execute with resource constraints
            exec(code, safe_globals, locals_dict)
        except TimeoutError:
            raise ResourceLimitExceeded("Execution time limit exceeded")
        finally:
            signal.alarm(0)  # Disable alarm
            self._clean_environment()
            
        return locals_dict

    def _validate_code_security(self, code: str) -> None:
        """Perform AST-based security validation"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise SecurityViolation(f"Invalid syntax: {str(e)}") from None
            
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                raise SecurityViolation("Imports are not allowed")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ['eval', 'exec', 'open']:
                    raise SecurityViolation(f"Dangerous function call: {node.func.id}")
            if isinstance(node, ast.Attribute) and node.attr.startswith('_'):
                raise SecurityViolation("Access to private attributes is forbidden")

    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a restricted global namespace"""
        allowed_builtins = {
            name: __builtins__[name]
            for name in self.security_policy['allowed_builtins']
            if name in __builtins__
        }
        
        return {
            '__builtins__': allowed_builtins,
            '__sandboxed__': True,
            '__file__': '<sandbox>',
            '__name__': '__spl_sandbox__'
        }

    def _clean_environment(self) -> None:
        """Clean up module imports and leaked references"""
        new_modules = set(sys.modules.keys()) - self.original_modules
        for module in new_modules:
            del sys.modules[module]
            
        gc.collect()

    def _handle_timeout(self, signum, frame) -> None:
        """Handle execution timeout"""
        raise TimeoutError("Execution timed out")

    def apply_resource_limits(self) -> None:
        """Apply system-level resource limits (Unix only)"""
        try:
            import resource
            resource.setrlimit(resource.RLIMIT_AS, 
                (self.max_memory, self.max_memory))
            resource.setrlimit(resource.RLIMIT_CPU, 
                (self.timeout, self.timeout + 5))
        except ImportError:
            logger.warning("Resource limits not supported on this platform")
        except Exception as e:
            logger.error(f"Failed to set resource limits: {str(e)}")
            
class Sandbox:
    """Restricted execution environment"""
    def __init__(self):
        self.allowed_builtins = {
            'chapisha': print,
            'soma': input,
            'nambari': float
        }
        
    def __enter__(self):
        self.original_builtins = globals().copy()
        globals().clear()
        globals().update(self.allowed_builtins)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        globals().clear()
        globals().update(self.original_builtins)


class SandboxErrorHandler:
    """Decorator for safe execution of untrusted code"""
    def __init__(self, runtime: RuntimeEnvironment):
        self.runtime = runtime
        
    def __call__(self, func):
        def wrapped(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.runtime.manual_gc()
                logger.error(f"Sandbox error: {type(e).__name__}: {str(e)}")
                raise
        return wrapped

if __name__ == '__main__':
    # Example usage with enhanced security
    runtime = RuntimeEnvironment()
    runtime.security_policy.update({
        'allowed_builtins': {'print', 'range', 'sum', 'int'}
    })
    
    # Test immutability
    runtime.register_immutable("PI", 3.14159)
    try:
        runtime.verify_immutability("PI", 3.14)  # Should fail
    except ImmutabilityError as e:
        logger.error(str(e))
    
    # Test sandboxed execution
    safe_code = """
total = sum(range(10))
print(f"Safe calculation result: {total}")
"""
    try:
        result = runtime.run_sandboxed(safe_code)
        logger.info(f"Execution result: {result}")
    except SecurityViolation as e:
        logger.error(f"Security violation: {str(e)}")
    except ResourceLimitExceeded as e:
        logger.error(f"Resource limit: {str(e)}")
    
    # Test malicious code detection
    malicious_code = "import os; os.system('rm -rf /')"
    try:
        runtime.run_sandboxed(malicious_code)
    except SecurityViolation as e:
        logger.error(f"Blocked malicious code: {str(e)}")