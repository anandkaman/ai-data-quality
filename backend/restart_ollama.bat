@echo off
:loop
timeout /t 1800
taskkill /F /IM ollama.exe
timeout /t 3
start "" "C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe" serve
goto loop
