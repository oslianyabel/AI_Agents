@echo off
echo ==============================
echo Creando entorno virtual...
echo ==============================

REM Crea el entorno virtual solo si no existe
if not exist venv (
    python -m venv venv
)

echo ==============================
echo Activando entorno virtual...
echo ==============================

call venv\Scripts\activate

echo ==============================
echo Instalando dependencias...
echo ==============================

pip install --upgrade pip
pip install -r requirements.txt

echo ==============================
echo Entorno listo.
echo ==============================
pause
