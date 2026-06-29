from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from database import get_conn

router = APIRouter()

def _get_batch_data(batch_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM batches WHERE batch_id=?", (batch_id,)).fetchone()
        if not row:
            return None, None
        handlers = conn.execute(
            "SELECT handler,location,tamper,timestamp FROM handlers WHERE batch_id=?", (batch_id,)
        ).fetchall()
    return dict(row), [dict(h) for h in handlers]

@router.get("/{batch_id}", response_class=HTMLResponse)
def verify_product(batch_id: str, format: str = "html"):
    b, handlers = _get_batch_data(batch_id)

    if format == "json":
        from fastapi.responses import JSONResponse
        if not b:
            return JSONResponse({"verified": False, "error": "Product not found"})
        return JSONResponse({
            "verified": True,
            "batch_id": batch_id,
            "crop": b["crop_name"],
            "farmer": b["farmer_wallet"],
            "organic": bool(b["is_organic"]),
            "tamper_detected": bool(b["tamper_detected"]),
            "supply_chain": [
                {**h, "tamper": bool(h["tamper"])} for h in handlers
            ],
            "trust_score": "HIGH" if b["is_organic"] and not b["tamper_detected"] else "COMPROMISED"
        })

    if not b:
        return HTMLResponse(_not_found_html(batch_id), status_code=404)

    trust = "HIGH" if b["is_organic"] and not b["tamper_detected"] else "COMPROMISED"
    return HTMLResponse(_product_html(batch_id, b, handlers, trust))


def _not_found_html(batch_id):
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>FarmChain</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{{font-family:system-ui,sans-serif;background:#f5f5f5;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}
  .card{{background:#fff;border-radius:12px;padding:40px;text-align:center;box-shadow:0 2px 16px rgba(0,0,0,.1)}}
  h2{{color:#e53e3e}}
</style></head>
<body><div class="card"><h2>Product Not Found</h2><p>Batch <code>{batch_id}</code> has no record in FarmChain.</p></div></body></html>"""


def _product_html(batch_id, b, handlers, trust):
    organic_badge = '<span class="badge green">USDA Organic</span>' if b["is_organic"] else '<span class="badge grey">Conventional</span>'
    trust_badge = f'<span class="badge {"green" if trust == "HIGH" else "red"}">{trust} TRUST</span>'

    steps = ""
    for h in handlers:
        tamper_icon = "⚠️" if h["tamper"] else "✅"
        steps += f"""
        <div class="step">
          <div class="step-icon">{tamper_icon}</div>
          <div class="step-body">
            <strong>{h['handler'].title()}</strong>
            <span>{h['location']}</span>
            <span class="ts">{h['timestamp'] or ''}</span>
          </div>
        </div>"""

    if not steps:
        steps = '<p class="muted">No supply chain steps recorded yet.</p>'

    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>FarmChain — {b['crop_name']}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:system-ui,sans-serif;background:#f0f4f0;color:#1a1a1a;padding:20px}}
  .card{{background:#fff;border-radius:14px;padding:28px;max-width:480px;margin:0 auto 20px;box-shadow:0 2px 12px rgba(0,0,0,.08)}}
  h1{{font-size:1.6rem;margin-bottom:4px}}
  .sub{{color:#666;font-size:.9rem;margin-bottom:16px}}
  .badge{{display:inline-block;padding:4px 12px;border-radius:99px;font-size:.8rem;font-weight:600;margin-right:6px}}
  .green{{background:#d4edda;color:#155724}}
  .red{{background:#f8d7da;color:#721c24}}
  .grey{{background:#e2e3e5;color:#383d41}}
  .divider{{border:none;border-top:1px solid #eee;margin:20px 0}}
  h3{{font-size:1rem;font-weight:600;margin-bottom:12px;color:#444}}
  .row{{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid #f5f5f5;font-size:.9rem}}
  .row span:first-child{{color:#666}}
  .step{{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid #f5f5f5}}
  .step:last-child{{border-bottom:none}}
  .step-icon{{font-size:1.4rem;line-height:1}}
  .step-body{{display:flex;flex-direction:column;font-size:.9rem}}
  .step-body strong{{margin-bottom:2px}}
  .step-body span{{color:#666;font-size:.82rem}}
  .ts{{font-style:italic}}
  .muted{{color:#888;font-size:.9rem}}
  .id{{font-size:.75rem;color:#aaa;margin-top:16px;text-align:center}}
  .logo{{text-align:center;font-weight:700;color:#2d6a2d;margin-bottom:20px;font-size:1.1rem;letter-spacing:.5px}}
</style>
</head>
<body>
  <div class="logo">🌿 FarmChain</div>

  <div class="card">
    <h1>{b['crop_name']}</h1>
    <div class="sub">Batch #{batch_id}</div>
    {organic_badge}
    {trust_badge}
    <hr class="divider">
    <h3>Product Details</h3>
    <div class="row"><span>Harvest Date</span><span>{b['harvest_date']}</span></div>
    <div class="row"><span>Quantity</span><span>{b['quantity_kg']} kg</span></div>
    <div class="row"><span>Farmer Wallet</span><span style="font-size:.78rem;word-break:break-all">{b['farmer_wallet']}</span></div>
    {'<div class="row"><span>Notes</span><span>' + b["notes"] + '</span></div>' if b["notes"] else ""}
  </div>

  <div class="card">
    <h3>Supply Chain</h3>
    {steps}
  </div>

  <div class="id">Verified on FarmChain blockchain · Batch {batch_id}</div>
</body></html>"""
