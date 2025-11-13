from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.config import settings

router = APIRouter()


@router.get("/recaptcha", response_class=HTMLResponse)
def recaptcha_page():
    """Serve a simple HTML page that renders the invisible reCAPTCHA widget.

    The page executes grecaptcha and posts the token back via
    `window.ReactNativeWebView.postMessage(token)` so the Expo WebView can
    receive it. Hosting this page under your backend domain avoids the
    "Invalid domain for site key" error when using WebView.
    """
    site_key = settings.recaptcha_site_key or ""
    # Serve a nicer, mobile-friendly UI: centered card, success indicator and auto-feedback.
    html = f"""
    <!doctype html>
    <html lang="pt-BR">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>reCAPTCHA</title>
        <style>
          :root {{ --bg: #5a341a; --card: #fff; --accent: #E07612; }}
          html,body {{ height:100%; margin:0; font-family: Inter, Roboto, Arial, sans-serif; background: linear-gradient(180deg, #5a341a 0%, #3b2313 100%); display:flex; align-items:center; justify-content:center; }}
          .card {{ width:92%; max-width:420px; background: var(--card); border-radius:12px; padding:20px; box-shadow:0 8px 30px rgba(0,0,0,0.3); text-align:center; color: #111; }}
          .title {{ font-size:18px; margin-bottom:6px; font-weight:600; }}
          .subtitle {{ color:#6b7280; font-size:13px; margin-bottom:16px; }}
          .check {{ width:64px; height:64px; border-radius:50%; background: linear-gradient(180deg, #34D399, #10B981); display:inline-flex; align-items:center; justify-content:center; color:white; font-weight:700; margin-bottom:12px; font-size:28px; }}
          .token {{ display:none }}
          .actions {{ display:flex; gap:8px; justify-content:center; margin-top:12px; }}
          .btn {{ background:var(--accent); color:white; padding:8px 12px; border-radius:8px; border:none; cursor:pointer; font-weight:600; }}
          .btn.secondary {{ background:#efefef; color:#111; }}
        </style>
        <script>
          function sendTokenToApp(token) {{
            try {{ window.ReactNativeWebView.postMessage(token); }} catch (e) {{ /* ignore if not in WebView */ }}
            document.getElementById('status').textContent = 'Verificação concluída';
            document.getElementById('check').style.display = 'inline-flex';
          }}

          function copyToken() {{ /* no-op in production UI */ }}

          function fallbackCopy(text) {{ /* no-op */ }}

          function onSuccess(token) {{
            sendTokenToApp(token);
          }}

          function onLoadCallback() {{
            try {{
              var widgetId = grecaptcha.render('recaptcha', {{ 'sitekey': '{site_key}', 'size': 'invisible', 'callback': onSuccess }});
              grecaptcha.execute(widgetId);
            }} catch (e) {{
              try {{ grecaptcha.execute(); }} catch (ee) {{ document.getElementById('status').textContent = 'Erro reCAPTCHA: ' + ee.message; }}
            }}
          }}
        </script>
      </head>
      <body>
        <div class="card" role="main">
          <div id="check" class="check" style="display:none">✓</div>
          <div id="status" class="title">Aguardando verificação...</div>
          <div class="subtitle">O reCAPTCHA será executado automaticamente. Aguarde.</div>
          <div id="recaptcha"></div>
          <div id="token" class="token">(token oculto)</div>
          <div class="actions">
            <button class="btn secondary" onclick="location.reload()">Tentar novamente</button>
          </div>
        </div>
        <script src="https://www.google.com/recaptcha/api.js?onload=onLoadCallback&render=explicit" async defer></script>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
