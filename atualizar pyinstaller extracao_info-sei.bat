@echo off
pyinstaller --noconsole --ico="C:\2python\public-extracao-info_sei\icon\download_sei.ico" --noconfirm --onedir ^
--add-data "C:\2python\public-extracao-info_sei\excel\*;excel" ^
--add-data "C:\2python\public-extracao-info_sei\edgedriver_win64\*;edgedriver_win64" ^
--add-data "C:\2python\public-extracao-info_sei\login_sei.py;." ^
--add-data "C:\2python\public-extracao-info_sei\config.py;." ^
--add-data "C:\2python\public-extracao-info_sei\buscas.py;." ^
--add-data "C:\2python\public-extracao-info_sei\main.py;." ^
--add-data "C:\2python\public-extracao-info_sei\README.pdf;." ^
extracao_info_sei.py
pause
