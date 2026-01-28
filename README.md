# spot-downloader

GUI em Python para baixar playlists do Spotify em MP3 usando o spotdl, com organização por gênero e otimização opcional via OpenAI.

## Funcionalidades
- Baixa músicas a partir de um link do Spotify
- Gera `tracklist.txt` com as faixas
- Deduplicação por arquivo existente
- Organização por gênero (opcional, usando OpenAI)
- Interface gráfica com customtkinter

## Requisitos
- Python 3.10+
- FFmpeg instalado e disponível no PATH

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração
Crie um `.env` a partir do `.env.example` (não versionado):
```bash
cp .env.example .env
```

Defina as variáveis no `.env`:
- `SPOTIFY_CLIENT_ID` (opcional)
- `SPOTIFY_CLIENT_SECRET` (opcional)
- `OPENAI_API_KEY` (opcional, necessário para Smart Search e organização por gênero)

## Fluxo seguro de chaves
- Nunca versionar chaves; o `.env` fica fora do git.
- Compartilhe variáveis por canal seguro (gerenciador de senhas, secret manager).
- Se uma chave vazar, revogue imediatamente e gere outra.

## Uso
```bash
python main.py
```

Cole a URL da playlist, escolha a pasta de saída e inicie o download.

## Observações
- O uso de OpenAI é opcional; sem chave, o app funciona normalmente.
- O spotdl faz o matching com base nos metadados do Spotify.
