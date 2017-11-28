pip install pyinstaller==3.3
pip install -r requirements.txt
python -m PyInstaller --clean --hidden-import=requests -F main.py
