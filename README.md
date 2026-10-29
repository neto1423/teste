# BaixaReel

Aplicativo local para baixar vídeos públicos a partir de links HTTP ou HTTPS em sites compatíveis com yt-dlp.

## Como iniciar no Windows

1. Instale o Python 3.10 ou superior.
2. Abra o PowerShell nesta pasta.
3. Instale a dependência: `py -m pip install -r requirements.txt`
4. Inicie o aplicativo: `py app.py`
5. Abra `http://127.0.0.1:8000` no navegador.

Os vídeos baixados ficam na pasta `downloads`. Para encerrar o aplicativo, pressione `Ctrl+C` no terminal.

O yt-dlp oferece suporte a vários sites, mas nem todo link ou plataforma funciona. Conteúdo privado, protegido por autenticação ou DRM pode não estar disponível. Use apenas conteúdo que você tenha autorização para salvar.

## Publicar gratuitamente no Render

O GitHub Pages não executa o servidor Python. Para publicar o aplicativo completo,
conecte este repositório ao Render como um **Web Service** e use:

- Build command: `pip install -r requirements.txt`
- Start command: `python app.py`
- Plano: Free

O servidor escuta a porta indicada pelo Render. O plano gratuito pode suspender o
serviço após inatividade, e os vídeos salvos no disco do serviço são temporários.
