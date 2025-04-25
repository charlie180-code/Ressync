import os
import ctypes

def load_dlls():
    """
    Load required DLLs from the specified 'libs' directory and add it to the PATH.
    """
    dll_path = os.path.abspath("libs")
    os.environ["PATH"] = f"{dll_path};" + os.environ["PATH"]
    try:
        ctypes.windll.LoadLibrary(os.path.join(dll_path, "libgobject-2.0-0.dll"))
        ctypes.windll.LoadLibrary(os.path.join(dll_path, "libglib-2.0-0.dll"))
        ctypes.windll.LoadLibrary(os.path.join(dll_path, "libgtk-3-0.dll"))
        print("DLLs loaded successfully.")
    except Exception as e:
        print(f"Failed to load DLL: {e}")

if __name__ == "__main__":
    load_dlls()
