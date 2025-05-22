@echo off
echo Setting up development environment...

:: Upgrade pip
python -m pip install --upgrade pip

:: Install requirements
pip install -r requirements.txt
pip install -r requirements-dev.txt

:: Install pre-commit hooks
pre-commit install

echo Setup complete!
