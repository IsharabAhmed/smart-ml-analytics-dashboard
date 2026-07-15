@echo off
echo ===================================================
echo   Starting Aura ML Analytics Dashboard
echo ===================================================

echo Activating virtual environment...
call .\venv\Scripts\Activate.bat

echo.
echo Applying any pending database migrations...
python manage.py migrate

echo.
echo Launching the server locally (Celery tasks will run eagerly)...
echo Dashboard will be available at http://127.0.0.1:8000
echo.
python manage.py runserver
