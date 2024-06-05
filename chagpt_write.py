import os

def capture_code_files_content(directory):
    """
    Captura o conteúdo de todos os arquivos de código no diretório fornecido e em seus subdiretórios,
    excluindo o próprio script.

    Args:
        directory (str): O diretório raiz para pesquisar arquivos de código.

    Returns:
        dict: Um dicionário com o nome do arquivo como chave e o conteúdo do arquivo como valor.
    """
    files_content = {}
    script_path = os.path.abspath(__file__)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js')):
                file_path = os.path.join(root, file)
                # Ignora o próprio script
                if file_path != script_path:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files_content[file_path] = content
                    except Exception as e:
                        print(f"Erro ao ler o arquivo {file_path}: {e}")
    return files_content

def format_files_content(files_content):
    """Formata o conteúdo do arquivo para exibição."""
    formatted_content = []
    for filename, content in files_content.items():
        formatted_content.append(f'Filename: {filename}\nContent:\n{content}\n{"-" * 80}')
    return "\n\n".join(formatted_content)

def main():
    # Diretório raiz para pesquisar arquivos de código
    root_directory = os.path.dirname(os.path.abspath(__file__))

    # Captura e formata o conteúdo dos arquivos de código
    code_files_content = capture_code_files_content(root_directory)
    formatted_content = format_files_content(code_files_content)

    # Salva o conteúdo formatado em um arquivo .txt
    with open('code_files_content.txt', 'w', encoding='utf-8') as f:
        f.write(formatted_content)

    # Exibe o conteúdo formatado no console (opcional)
    print(formatted_content)

if __name__ == "__main__":
    main()
