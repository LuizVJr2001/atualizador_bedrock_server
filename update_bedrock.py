import warnings
# O silenciador DEVE vir antes de qualquer outra importação!
warnings.filterwarnings("ignore")

import os
import stat
import zipfile
import requests
import paramiko
import tarfile
import shutil
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv
from tqdm import tqdm  # A nossa nova biblioteca mágica para a barra de progresso

# Carrega as variáveis do arquivo .env
load_dotenv()

# --- CONFIGURAÇÕES DO SERVIDOR (Puxadas do .env e limpas) ---
SFTP_HOST = os.getenv('SFTP_HOST', '').strip()
SFTP_PORT = int(os.getenv('SFTP_PORT', 2077))
SFTP_USER = os.getenv('SFTP_USER', '').strip()
SFTP_PASS = os.getenv('SFTP_PASS', '').strip()
REMOTE_DIR = os.getenv('REMOTE_DIR', '/').strip()

# Arquivos/pastas que NUNCA devem ser sobrescritos
IGNORE_LIST = ['server.properties', 'permissions.json', 'allowlist.json', 'worlds', 'valid_known_packs.json']

def get_latest_bedrock_url():
    print("Consultando a API oficial da Microsoft...")
    url = "https://net-secondary.web.minecraft-services.net/api/v1.0/download/links"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        dados = response.json()
        for item in dados.get('result', {}).get('links', []):
            if item.get('downloadType') == 'serverBedrockLinux':
                return item.get('downloadUrl')
                
    raise Exception(f"Falha ao ler a API da Microsoft. O servidor retornou o status: {response.status_code}")

def create_sftp_connection():
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.chdir(REMOTE_DIR)
    return sftp, transport

def download_dir_sftp(sftp, remote_dir, local_dir):
    os.makedirs(local_dir, exist_ok=True)
    for item in sftp.listdir_attr(remote_dir):
        if remote_dir == '/':
            r_path = f"/{item.filename}"
        else:
            r_path = f"{remote_dir.rstrip('/')}/{item.filename}"
            
        l_path = os.path.join(local_dir, item.filename)
        
        if stat.S_ISDIR(item.st_mode):
            download_dir_sftp(sftp, r_path, l_path)
        else:
            sftp.get(r_path, l_path)

def backup_via_sftp(sftp):
    print("\n--- INICIANDO BACKUP COMPLETO DO SERVIDOR ---")
    print("Atenção: Baixar todos os arquivos via SFTP pode levar alguns minutos...")
    
    data_atual = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    pasta_backups = './backups'
    nome_arquivo_tar = f'backup_server_{data_atual}.tar.gz'
    caminho_tar = os.path.join(pasta_backups, nome_arquivo_tar)
    pasta_temp = './temp_backup_raw'
    
    if not os.path.exists(pasta_backups):
        os.makedirs(pasta_backups)
        
    download_dir_sftp(sftp, REMOTE_DIR, pasta_temp)
    
    print(f"Compactando arquivos em {nome_arquivo_tar}...")
    with tarfile.open(caminho_tar, "w:gz") as tar:
        tar.add(pasta_temp, arcname=f"backup_bedrock_{data_atual}")
        
    shutil.rmtree(pasta_temp)
    print(f"Backup completo salvo com sucesso em: {caminho_tar}\n")

def upload_via_sftp(sftp, local_extract_path):
    print("\n--- INICIANDO UPLOAD DA ATUALIZAÇÃO ---")
    
    arquivos_para_enviar = []
    pastas_para_criar = []
    
    # 1. Mapeia toda a estrutura local antes de enviar
    for root, dirs, files in os.walk(local_extract_path):
        for d in dirs:
            if d in IGNORE_LIST:
                continue
            remote_path = os.path.join(root.replace(local_extract_path, ''), d).replace('\\', '/').lstrip('/')
            if remote_path:
                pastas_para_criar.append(remote_path)

        for f in files:
            if f in IGNORE_LIST and root == local_extract_path:
                continue
            local_file = os.path.join(root, f)
            remote_path = os.path.join(root.replace(local_extract_path, ''), f).replace('\\', '/').lstrip('/')
            arquivos_para_enviar.append((local_file, remote_path))

    # 2. Cria as pastas necessárias no servidor
    print("Sincronizando estrutura de pastas no servidor...")
    for p in pastas_para_criar:
        try:
            sftp.stat(p)
        except IOError:
            sftp.mkdir(p)

    # 3. Faz o upload dos arquivos exibindo a barra de progresso
    print(f"Preparando envio de {len(arquivos_para_enviar)} arquivos...")
    
    # A mágica acontece aqui: o tqdm abraça a nossa lista e cria a animação
    for local_file, remote_path in tqdm(arquivos_para_enviar, desc="Progresso", unit="arq", dynamic_ncols=True, leave=True):
        sftp.put(local_file, remote_path)

    print("\nUpload concluído com sucesso!")

def main():
    sftp = None
    transport = None
    try:
        url = get_latest_bedrock_url()
        print(f"Link de download encontrado: {url}")
        
        print("Baixando os arquivos do servidor (isso pode levar alguns segundos)...")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers)
        
        print("Extraindo arquivos temporariamente...")
        zip_ref = zipfile.ZipFile(BytesIO(response.content))
        extract_path = './temp_bedrock'
        zip_ref.extractall(extract_path)
        
        print("Conectando ao SFTP...")
        sftp, transport = create_sftp_connection()
        
        # --- Backup desativado conforme solicitado ---
        # backup_via_sftp(sftp)
        
        # Faz o upload da atualização do Minecraft com a barra visual
        upload_via_sftp(sftp, extract_path)
        
        # Limpeza local
        print("\nLimpando arquivos temporários locais...")
        for root, dirs, files in os.walk(extract_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(extract_path)
        
        print("=======================================")
        print("Atualização do Bedrock finalizada!")
        print("Lembre-se de ligar o servidor no painel.")
        print("=======================================")
        
    except Exception as e:
        print(f"\n[ERRO] Ocorreu um problema: {e}")
    finally:
        if sftp: sftp.close()
        if transport: transport.close()

if __name__ == "__main__":
    main()