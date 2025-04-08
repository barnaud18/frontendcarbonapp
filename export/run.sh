#!/bin/bash

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Ambiente virtual não encontrado. Executando setup.py primeiro..."
    python setup.py
    source venv/bin/activate
fi

# Run the application
python main.py