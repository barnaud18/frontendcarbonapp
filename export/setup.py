import os
import sys
import subprocess

def main():
    """Setup the Calculadora de Pegada de Carbono application."""
    print("Configurando a Calculadora de Pegada de Carbono Agrícola...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERRO: Python 3.8 ou superior é necessário.")
        sys.exit(1)
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists('venv'):
        print("Criando ambiente virtual...")
        subprocess.call([sys.executable, '-m', 'venv', 'venv'])
    
    # Determine the pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join('venv', 'Scripts', 'pip')
    else:  # Unix/Linux/Mac
        pip_path = os.path.join('venv', 'bin', 'pip')
    
    # Install requirements
    print("Instalando dependências...")
    subprocess.call([pip_path, 'install', '-r', 'requirements.txt'])
    
    print("\nInstalação concluída com sucesso!")
    print("\nPara executar a aplicação:")
    if os.name == 'nt':  # Windows
        print("1. Ative o ambiente virtual: venv\\Scripts\\activate")
        print("2. Execute a aplicação: python main.py")
    else:  # Unix/Linux/Mac
        print("1. Ative o ambiente virtual: source venv/bin/activate")
        print("2. Execute a aplicação: python main.py")
    print("3. Acesse no navegador: http://127.0.0.1:5000/")

if __name__ == "__main__":
    main()