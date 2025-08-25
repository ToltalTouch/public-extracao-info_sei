@echo off
pyinstaller --noconsole --ico="C:\python\extracao_itens-sei\icon\download_sei.ico" --noconfirm --onedir ^
--add-data "C:\python\extracao_itens-sei\excel\;excel" ^
--add-data "C:\python\extracao_itens-sei\edgedriver_win64\*;edgedriver_win64" ^
--add-data "C:\python\extracao_itens-sei\login_sei.py;." ^
--add-data "C:\python\extracao_itens-sei\config.py;." ^
--add-data "C:\python\extracao_itens-sei\buscas.py;." ^
--add-data "C:\python\extracao_itens-sei\main.py;." ^
--add-data "C:\python\extracao_itens-sei\README.pdf;." ^
extracao_itens_sei.py
pause
