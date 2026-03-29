Aqui está um **README.md** completo, organizado e com aquele toque profissional para o seu repositório. Ele foi escrito pensando tanto em você (que vai manter o código) quanto no seu amigo (que só quer que o servidor funcione).

---

# ⛏️ Bedrock Server Auto-Updater (Razehost Edition)

Este projeto é uma ferramenta de automação "Plug & Play" desenvolvida em Python para simplificar a atualização de servidores de **Minecraft Bedrock** hospedados em serviços que utilizam painéis Pterodactyl (como a Razehost) via protocolo SFTP.

O grande diferencial deste script é a facilidade de uso: ele é capaz de preparar todo o ambiente (incluindo a instalação do próprio Python) de forma automática.

## ✨ Funcionalidades

* **Busca Inteligente:** Consulta a API oficial da Microsoft para encontrar sempre a versão estável mais recente do Bedrock Server (Linux).
* **Instalação Automática:** O arquivo `.bat` detecta se o Python está instalado; caso não esteja, ele baixa e instala a versão 3.12 silenciosamente para o usuário.
* **Proteção de Dados:** Garante que arquivos vitais (`worlds`, `server.properties`, `allowlist.json`, etc.) nunca sejam sobrescritos durante a atualização.
* **Barra de Progresso:** Feedback visual em tempo real do upload dos arquivos.
* **Ambiente Isolado:** Utiliza `venv` (Virtual Environment) para manter as bibliotecas do projeto organizadas sem afetar o sistema.

---

## 📁 Estrutura do Projeto

```text
├── backups/             # (Gerado automaticamente) Backups em .tar.gz
├── venv/                # (Gerado automaticamente) Ambiente virtual Python
├── update_bedrock.py    # O cérebro do projeto (Script Python)
├── atualizar.bat        # O executor mágico para Windows
├── .env                 # Suas credenciais reais (NÃO enviar ao GitHub)
├── .env.example         # Modelo para configuração das credenciais
├── requirements.txt     # Lista de bibliotecas necessárias
└── .gitignore           # Filtro para não subir arquivos sensíveis ao Git
```

---

## 🛠️ Como Usar (Passo a Passo)

### 1. Preparação
Clone este repositório na sua máquina:
```bash
git clone https://github.com/seu-usuario/seu-repo.git
cd seu-repo
```

### 2. Configuração das Credenciais
1. Na pasta do projeto, encontre o arquivo `.env.example`.
2. Renomeie-o para apenas `.env`.
3. Abra-o com o Bloco de Notas e preencha com os dados do seu painel Razehost (encontrados na aba **Settings > SFTP Details**):
   * `SFTP_HOST`: O endereço do host (Ex: `node1.razehost.com`)
   * `SFTP_USER`: Seu usuário completo (Ex: `usuario.a1b2c3d4`)
   * `SFTP_PASS`: A mesma senha que você usa para logar no painel.

### 3. Execução
Basta dar **dois cliques no arquivo `atualizar.bat`**. 

> **O que vai acontecer?**
> * Se você não tiver Python, ele será instalado automaticamente.
> * As bibliotecas necessárias serão baixadas.
> * A versão mais nova do Minecraft será baixada da Microsoft.
> * O upload começará com uma barra de progresso no terminal.

---

## ⚠️ Avisos Importantes

* **Desligue o Servidor:** Antes de rodar o script, desligue o servidor de Minecraft no painel da Razehost. Arquivos como o `bedrock_server` ficam travados pelo sistema enquanto o servidor está online, o que impedirá a atualização.
* **Segurança:** Nunca compartilhe ou faça commit do seu arquivo `.env`. Ele contém a senha de acesso ao seu servidor.
* **Backup:** Embora o script ignore a pasta de mundos, é sempre recomendável fazer um backup manual ocasional via painel da hospedagem.

---

## 🚀 Tecnologias Utilizadas

* [Python 3.12](https://www.python.org/)
* [Paramiko](http://www.paramiko.org/) (Conexão SFTP)
* [tqdm](https://github.com/tqdm/tqdm) (Barra de progresso)
* [python-dotenv](https://github.com/theskumar/python-dotenv) (Gestão de variáveis de ambiente)