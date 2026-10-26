# project1-BankApp
Build a banking application with a C++ backend and Python/Tkinter frontend, applying OOP, file handling, memory management, input validation, and cross-language integration.

## Build and run on Windows

The Tkinter app loads `bank.dll` from this folder. Build that library before launching the app.

1. Install MSYS2 with the MinGW-w64 UCRT x64 toolchain, including `g++`.
2. Open the MSYS2 UCRT64 terminal and change to this project folder.
3. Build the shared library:

	```sh
	g++ -std=c++17 -shared -static -static-libgcc -static-libstdc++ -o bank.dll bank.cpp bank_wrapper.cpp
	```

4. Launch the GUI from PowerShell or VS Code:

	```powershell
	py -3 bank_app.py
	```

The same build command can be run in PowerShell if the MinGW-w64 `bin` directory is on `PATH`.


## Build on macOS

The Tkinter app loads the `bank` shared library from this folder. Build it before launching the app.

1. Install the compiler (Xcode Command Line Tools):

   ```
   xcode-select --install
   ```

2. Open Terminal and go to the project folder:

   ```
   cd /path/to/project
   ```

3. Build the shared library:

   ```
   clang++ -std=c++17 -shared -fPIC -o libbank.dylib bank.cpp bank_wrapper.cpp
   ```

4. Launch the GUI:

   ```
   python3 bank_app.py
   ```

Notes:
- Make sure `bank_app.py` loads `libbank.dylib` on macOS (instead of `bank.dll`).
- If using Homebrew Python, install Tkinter with `brew install python-tk`.
- Python and the library must match architecture (arm64 vs x86_64).
```
