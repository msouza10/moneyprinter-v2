import os
import glob

def capture_python_files_content():
    # Diretório onde o script está localizado
    directory = os.path.dirname(os.path.abspath(__file__))
    
    # Obtenha o nome do arquivo atualmente em execução
    current_file = os.path.abspath(__file__)
    
    # Use glob para encontrar todos os arquivos Python no diretório especificado
    python_files = glob.glob(os.path.join(directory, '*.py'))
    
    files_content = {}
    
    for file in python_files:
        # Ignorar o próprio arquivo
        if os.path.abspath(file) == current_file:
            continue
        
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        files_content[file] = content
    
    return files_content

def format_files_content(files_content):
    formatted_content = []
    for filename, content in files_content.items():
        formatted_content.append(f'Filename: {filename}\nContent:\n{content}\n{"-" * 80}')
    return "\n\n".join(formatted_content)

# Captura e formata o conteúdo dos arquivos Python no diretório do script
python_files_content = capture_python_files_content()
formatted_content = format_files_content(python_files_content)

# Exibir o conteúdo formatado
print(formatted_content)
