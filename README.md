# Chatbot GenAI com NVIDIA NIM

Aplicacao Streamlit publicada para a atividade pratica da disciplina de Produtos de GenAI.

- Repositorio: <https://github.com/PedroRomeroM/chatbot-genai-pedro>
- Aplicacao publica: pendente de deploy na VM
- Modelo: `meta/llama-3.3-70b-instruct`
- Stack: Python, Streamlit, OpenAI SDK e NVIDIA API Catalog / NIM

## Como executar localmente

1. Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Configure a chave da NVIDIA:

```bash
cp .env.example .env
```

Edite `.env` e preencha:

```bash
NVIDIA_API_KEY=sua_chave
NVIDIA_MODEL=meta/llama-3.3-70b-instruct
```

4. Inicie a aplicacao:

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

5. Acesse:

```text
http://localhost:8501
```

## Relatorio da atividade

### Introducao

O objetivo desta atividade foi desenvolver e publicar um chatbot baseado em Inteligencia Artificial Generativa usando um modelo open source disponibilizado pela NVIDIA. A solucao foi criada em Python com Streamlit, para oferecer uma interface web simples, direta e acessivel pelo navegador.

A aplicacao implementada e um assistente de engenharia de prompt e GenAI. O usuario digita perguntas em linguagem natural, o historico da conversa e mantido durante a sessao e as respostas sao geradas por um modelo Llama servido pela infraestrutura NVIDIA NIM.

### Infraestrutura

A publicacao foi planejada para uma maquina virtual Oracle Cloud Infrastructure.

Configuracao usada para deploy:

- Provedor: Oracle Cloud Infrastructure.
- Sistema operacional: Ubuntu 24.04.
- Tipo de aplicacao: servico Python/Streamlit executado atras de Nginx.
- Porta interna do Streamlit: `8501`.
- Porta publica: `80`, via proxy reverso Nginx.
- Processo em producao: recomendado via `systemd`, para reiniciar automaticamente em caso de falha.

O projeto nao exige GPU na VM porque a inferencia do modelo acontece na API da NVIDIA. A VM precisa apenas executar a interface web, gerenciar conexoes HTTP e chamar o endpoint remoto.

### Modelo escolhido

O modelo escolhido foi `meta/llama-3.3-70b-instruct`, disponibilizado no NVIDIA API Catalog / NIM.

Justificativa:

- e um modelo open weight da familia Llama 3.3;
- tem 70 bilhoes de parametros;
- e ajustado para instrucao e dialogo;
- suporta uso multilingue, incluindo portugues;
- pode ser acessado pela API da NVIDIA usando cliente OpenAI-compatible;
- evita a necessidade de provisionar GPU propria na VM da atividade.

Segundo a documentacao da NVIDIA, o Llama 3.3 70B Instruct e um modelo texto-para-texto pre-treinado e ajustado para instrucao, otimizado para casos de conversa multilingue. O exemplo oficial da NVIDIA tambem mostra o uso do endpoint `https://integrate.api.nvidia.com/v1` com o SDK da OpenAI.

Referencias:

- <https://build.nvidia.com/meta/llama-3_3-70b-instruct>
- <https://docs.api.nvidia.com/nim/reference/meta-llama-3_3-70b-instruct>

### Desenvolvimento

A arquitetura da aplicacao e propositalmente simples:

```text
Usuario no navegador
  -> Streamlit
  -> OpenAI SDK
  -> NVIDIA API Catalog / NIM
  -> Modelo meta/llama-3.3-70b-instruct
```

Bibliotecas utilizadas:

- `streamlit`: interface web e componentes de chat;
- `openai`: cliente HTTP OpenAI-compatible para chamar o endpoint da NVIDIA;
- `python-dotenv`: carregamento de variaveis de ambiente no ambiente local.

O historico da conversa e armazenado em `st.session_state`, ou seja, fica disponivel durante a sessao do navegador. Isso mantem a aplicacao simples e evita criar banco de dados apenas para a atividade.

### Gerenciamento de credenciais

A chave da NVIDIA nao fica no codigo-fonte e nao deve ser enviada ao GitHub. O projeto usa a variavel de ambiente `NVIDIA_API_KEY`.

Em desenvolvimento local, a variavel pode ser carregada por um arquivo `.env`, que esta listado no `.gitignore`. Em producao, a recomendacao e configurar a chave diretamente no ambiente do servico `systemd`, por exemplo em um arquivo protegido em `/etc/chatbot-genai-pedro.env`.

### Implantacao

Processo recomendado para publicacao na VM:

1. Instalar Python, venv, pip, Git e Nginx.
2. Clonar o repositorio.
3. Criar ambiente virtual Python.
4. Instalar dependencias com `pip install -r requirements.txt`.
5. Configurar `NVIDIA_API_KEY` no ambiente da VM.
6. Criar um servico `systemd` executando:

```bash
streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

7. Configurar Nginx como proxy reverso da porta publica `80` para `127.0.0.1:8501`.
8. Reiniciar Nginx e validar o acesso pelo IP publico.

Exemplo de bloco Nginx:

```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

### Principais desafios

O principal ponto de atencao foi separar a execucao do modelo da execucao da interface. Rodar um modelo de 70B parametros diretamente em uma VM comum exigiria GPU e memoria muito superiores ao necessario para a atividade. A solucao foi usar a VM apenas como camada web e consumir a API da NVIDIA para inferencia.

Outro cuidado importante foi o gerenciamento da chave de API. A chave precisa existir na VM para a aplicacao funcionar, mas nao pode entrar no repositorio.

### Discussao

Licoes aprendidas:

- Streamlit e uma alternativa eficiente para publicar prototipos de GenAI rapidamente.
- A compatibilidade OpenAI do endpoint da NVIDIA simplifica bastante a integracao.
- Separar interface e inferencia reduz custo e complexidade de infraestrutura.
- Mesmo em atividades pequenas, credenciais devem ser tratadas como segredo operacional.

Possiveis melhorias futuras:

- adicionar selecao de temperatura e tamanho de resposta na interface;
- registrar metricas simples de uso;
- incluir guardrails de seguranca e moderacao;
- adicionar RAG com documentos da disciplina;
- publicar com HTTPS e dominio proprio;
- criar pipeline automatizado de deploy.

## Licenca

Projeto criado para fins educacionais.
