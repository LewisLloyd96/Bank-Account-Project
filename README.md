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
