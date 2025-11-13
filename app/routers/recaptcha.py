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
    html = f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <script>
          function onSuccess(token) {{
            // Post token back to the WebView
            try {{ window.ReactNativeWebView.postMessage(token); }} catch (e) {{ /* ignore */ }}
            // Also render token on the page for manual debugging
            var el = document.getElementById('token'); if (el) el.textContent = token;
          }}

          function onLoadCallback() {{
            try {{
              var widgetId = grecaptcha.render('recaptcha', {{ 'sitekey': '{site_key}', 'size': 'invisible', 'callback': onSuccess }});
              grecaptcha.execute(widgetId);
            }} catch (e) {{
              try {{ grecaptcha.execute(); }} catch (ee) {{ document.body.innerText = 'reCAPTCHA error: ' + ee.message; }}
            }}
          }}
        </script>
      </head>
      <body>
        <div id="recaptcha"></div>
        <div style="position:fixed; bottom:8px; left:8px; right:8px; background: #fff; padding:8px; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.2)">
          <small>Se você vir um token aqui, a verificação foi executada:</small>
          <pre id="token" style="word-break:break-all;">(aguardando token)</pre>
        </div>
        <script src="https://www.google.com/recaptcha/api.js?onload=onLoadCallback&render=explicit" async defer></script>
      </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=200)
