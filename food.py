"""
FoodDash - Food Order Processing System
A Flask web app that uses a FIFO queue (collections.deque) to process orders.

Run:
    
    python app.py
Then open http://127.0.0.1:5000
"""
from collections import deque
from datetime import datetime

from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

MENU = {
    "Cheeseburger Deluxe": "🍔",
    "Pepperoni Pizza": "🍕",
    "Chicken Burger": "🍔",
    "Loaded Fries": "🍟",
    "Italian Pasta": "🍝",
}

STATUS_FLOW = ["Pending", "Preparing", "Ready"]


def now():
    return datetime.now().strftime("%H:%M:%S")


# ---------- Data (FIFO queue + history) ----------
queue = deque()
completed = []
next_id = 101


def seed():
    global next_id
    queue.clear()
    completed.clear()
    for oid, name, item, qty, t in [
      
    ]:
        completed.insert(0, dict(id=oid, name=name, item=item, qty=qty, status="Ready", time=t))
    for oid, name, item, qty, status, t in [
        
    ]:
        queue.append(dict(id=oid, name=name, item=item, qty=qty, status=status, time=t))
    next_id = 106


seed()

# ---------- Routes ----------
@app.route("/")
def home():
    return render_template_string(PAGE, queue=list(queue), completed=completed, menu=MENU)


@app.route("/order", methods=["POST"])
def place_order():
    global next_id
    name = request.form.get("name", "").strip()
    item = request.form.get("item")
    try:
        qty = max(1, int(request.form.get("qty", 1)))
    except ValueError:
        qty = 1
    if name and item in MENU:
        queue.append(dict(id=next_id, name=name, item=item, qty=qty, status="Pending", time=now()))
        next_id += 1
    return redirect(url_for("home") + "#queue")


@app.route("/update/<int:oid>", methods=["POST"])
def update(oid):
    # FIFO rule: only the order at the front of the queue can be processed
    if queue and queue[0]["id"] == oid:
        order = queue[0]
        idx = STATUS_FLOW.index(order["status"])
        if idx < len(STATUS_FLOW) - 2:
            order["status"] = STATUS_FLOW[idx + 1]          # Pending -> Preparing
        else:
            done = queue.popleft()                          # Preparing -> Ready (dequeue)
            done["status"] = "Ready"
            done["time"] = now()
            completed.insert(0, done)
    return redirect(url_for("home") + "#queue")


@app.route("/cancel/<int:oid>", methods=["POST"])
def cancel(oid):
    for o in list(queue):
        if o["id"] == oid:
            queue.remove(o)
            break
    return redirect(url_for("home") + "#queue")


@app.route("/reset")
def reset():
    seed()
    return redirect(url_for("home"))


# ---------- Template ----------
PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>FoodDash - Food Order Processing System</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Caveat:wght@600&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0b0d2e; --panel:#12163f; --panel2:#171c4d; --line:#2a3170;
    --pink:#ff2d87; --pink2:#ff5a5f; --cyan:#22e3ff; --text:#eef0ff; --muted:#9aa3d6;
    --yellow:#ffc21a; --blue:#2f7bff; --green:#12b886;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Poppins',sans-serif;color:var(--text);min-height:100vh;
       background:radial-gradient(circle at 20% 0%,#23195a 0%,var(--bg) 55%);}
  header{display:flex;align-items:center;justify-content:space-between;gap:20px;padding:18px 36px;
         background:linear-gradient(90deg,#1a1240,#2a1250 50%,#3a1a2a);border-bottom:1px solid var(--line);}
  .logo{display:flex;align-items:center;gap:14px}
  .logo .emoji{font-size:54px}
  .logo h1{font-size:44px;font-weight:800;line-height:1}
  .logo h1 span{color:var(--pink2)}
  .logo small{color:var(--muted);letter-spacing:.5px}
  .tagline{font-family:'Caveat',cursive;font-size:34px;color:#fff;text-align:center}
  .tagline em{color:var(--pink2);font-style:normal}
  .hero-emoji{font-size:64px}
  .layout{display:grid;grid-template-columns:250px 1fr;gap:20px;padding:20px 24px}
  aside{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:14px;height:fit-content;position:sticky;top:16px}
  aside a{display:flex;align-items:center;gap:12px;padding:13px 16px;margin-bottom:6px;border-radius:12px;
          color:var(--text);text-decoration:none;font-weight:500}
  aside a.active,aside a:hover{background:linear-gradient(90deg,#d6246e,#9b2a6c)}
  .quote{font-family:'Caveat',cursive;font-size:30px;line-height:1.1;text-align:center;margin:26px 0 10px;color:#ffe9a8}
  .big-emoji{font-size:90px;text-align:center}
  main{display:flex;flex-direction:column;gap:18px}
  .card{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:18px;padding:18px 22px}
  .card-head{display:flex;align-items:center;gap:14px;margin-bottom:14px}
  .card-head .ico{font-size:34px}
  .card-head h2{font-size:22px;font-weight:600}
  .card-head p{font-size:13px;color:var(--muted)}
  .pink{color:#ff4fa0}.cyan{color:var(--cyan)}.green{color:#2ee6b6}
  .badge{background:var(--pink);border-radius:50%;padding:1px 9px;font-size:13px;margin-left:8px;vertical-align:middle;color:#fff}
  .script{margin-left:auto;font-family:'Caveat',cursive;font-size:26px;color:var(--yellow)}
  form.order{display:grid;grid-template-columns:1fr 1fr .6fr auto;gap:14px;align-items:end}
  .field{background:#0f1340;border:1px solid var(--line);border-radius:12px;padding:10px 12px}
  .field label{display:block;font-size:14px;margin-bottom:6px}
  .field input,.field select{width:100%;background:#0b0e33;border:1px solid var(--line);color:var(--text);
        padding:10px 12px;border-radius:8px;font-family:inherit;font-size:15px;outline:none}
  .field input:focus,.field select:focus{border-color:var(--pink)}
  .btn-order{background:linear-gradient(90deg,#ff2d87,#ff5a5f);border:0;color:#fff;font-size:20px;font-weight:600;
        padding:22px 48px;border-radius:14px;cursor:pointer;font-family:inherit;box-shadow:0 8px 24px rgba(255,45,135,.35)}
  .btn-order:hover{filter:brightness(1.1)}
  .table-wrap{border:1px solid var(--line);border-radius:12px;overflow:hidden}
  table{width:100%;border-collapse:collapse}
  th{background:#0f1340;font-weight:500;padding:12px;font-size:14px;border-bottom:1px solid var(--line)}
  td{padding:10px 12px;text-align:center;font-size:14px;border-bottom:1px solid #1d2260}
  tr:last-child td{border-bottom:0}
  td.left{text-align:left}
  .food{display:flex;align-items:center;gap:12px;text-align:left}
  .food span.e{font-size:28px}
  .pill{display:inline-block;min-width:92px;padding:5px 12px;border-radius:8px;font-size:12px;font-weight:600}
  .Pending{background:var(--yellow);color:#2b2200}
  .Preparing{background:var(--blue);color:#fff}
  .Ready{background:var(--green);color:#fff}
  .upd{background:var(--blue);color:#fff;border:0;padding:8px 18px;border-radius:8px;cursor:pointer;font-family:inherit;font-size:14px}
  .upd:disabled{background:#2a3170;color:#7b84c4;cursor:not-allowed}
  .dots{background:none;border:0;color:var(--text);font-size:20px;cursor:pointer;margin-left:10px}
  .empty{padding:24px;color:var(--muted);text-align:center}
  footer{display:flex;justify-content:space-between;align-items:center;padding:10px 36px 30px;color:var(--muted)}
  footer b{color:#fff}
  @media(max-width:1000px){
    .layout{grid-template-columns:1fr} aside{position:static}
    form.order{grid-template-columns:1fr} .tagline,.hero-emoji{display:none}
    .table-wrap{overflow-x:auto}
  }
</style>
</head>
<body>

<header>
  <div class="logo">
    <div class="emoji">🍔</div>
    <div><h1>Food<span>Dash</span></h1><small>Good Food &nbsp;•&nbsp; Happy Mood</small></div>
  </div>
  <div class="tagline">Fresh Food<br><em>Fast Service ♥</em></div>
  <div class="hero-emoji">🍔🍟🥤</div>
  <div class="tagline">Eat Good<br>Feel Good ♥</div>
</header>

<div class="layout">
  <aside>
    <a href="#top" class="active">🏠 Home</a>
    <a href="#place">➕ Place Order</a>
    <a href="#queue">📋 Queue</a>
    <a href="#completed">✅ Completed Orders</a>
    <a href="{{ url_for('reset') }}" onclick="return confirm('Reset all orders to the sample data?')">⚙️ Settings (Reset)</a>
    <div class="quote">Life is<br>Better<br>with<br>Food ♥</div>
    <div class="big-emoji">🍔🍟</div>
  </aside>

  <main id="top">
    <!-- Place order -->
    <section class="card" id="place">
      <div class="card-head">
        <div class="ico">📝</div>
        <div><h2 class="pink">Place New Order</h2><p>Add a new food order to the queue</p></div>
        <div class="script">Order Now!</div>
      </div>
      <form class="order" method="post" action="{{ url_for('place_order') }}">
        <div class="field"><label>👤 Customer Name</label>
          <input type="text" name="name" placeholder="Enter customer name" required></div>
        <div class="field"><label>🍴 Food Item</label>
          <select name="item">
            {% for name, emoji in menu.items() %}<option value="{{ name }}">{{ emoji }} {{ name }}</option>{% endfor %}
          </select></div>
        <div class="field"><label>📦 Quantity</label>
          <input type="number" name="qty" value="1" min="1" max="20"></div>
        <button class="btn-order" type="submit">🛒 Place Order</button>
      </form>
    </section>

    <!-- Live queue -->
    <section class="card" id="queue">
      <div class="card-head">
        <div class="ico">🎯</div>
        <div><h2 class="cyan">Live Order Queue (FIFO) <span class="badge">{{ queue|length }}</span></h2>
             <p>Orders are processed in the order they are received</p></div>
        <div class="script">👨‍🍳 In Progress</div>
      </div>
      <div class="table-wrap">
        <table>
          <tr><th>ID</th><th>Customer Name</th><th>Food Item</th><th>Quantity</th><th>Status</th><th>Time</th><th>Action</th></tr>
          {% for o in queue %}
          <tr>
            <td>{{ o.id }}</td>
            <td>{{ o.name }}</td>
            <td><div class="food"><span class="e">{{ menu[o.item] }}</span>{{ o.item }}</div></td>
            <td>{{ o.qty }}</td>
            <td><span class="pill {{ o.status }}">{{ o.status }}</span></td>
            <td>{{ o.time }}</td>
            <td>
              <form method="post" action="{{ url_for('update', oid=o.id) }}" style="display:inline">
                <button class="upd" {% if not loop.first %}disabled title="FIFO: only the first order can be processed"{% endif %}>🔄 Update</button>
              </form>
              <form method="post" action="{{ url_for('cancel', oid=o.id) }}" style="display:inline"
                    onsubmit="return confirm('Cancel order #{{ o.id }}?')">
                <button class="dots" title="Cancel order">⋮</button>
              </form>
            </td>
          </tr>
          {% else %}
          <tr><td colspan="7" class="empty">No orders in the queue 🎉</td></tr>
          {% endfor %}
        </table>
      </div>
    </section>

    <!-- Completed -->
    <section class="card" id="completed">
      <div class="card-head">
        <div class="ico">✅</div>
        <div><h2 class="green">Completed Orders History</h2><p>Successfully delivered orders</p></div>
        <div class="script">✔ Completed</div>
      </div>
      <div class="table-wrap">
        <table>
          <tr><th>ID</th><th>Customer Name</th><th>Food Item</th><th>Quantity</th><th>Status</th><th>Time</th></tr>
          {% for o in completed %}
          <tr>
            <td>{{ o.id }}</td><td>{{ o.name }}</td>
            <td><div class="food"><span class="e">{{ menu[o.item] }}</span>{{ o.item }}</div></td>
            <td>{{ o.qty }}</td>
            <td><span class="pill Ready">Ready</span></td>
            <td>{{ o.time }}</td>
          </tr>
          {% else %}
          <tr><td colspan="6" class="empty">Nothing delivered yet</td></tr>
          {% endfor %}
        </table>
      </div>
    </section>
  </main>
</div>

<footer>
  <div>🔥 <b>FoodDash</b> &nbsp;|&nbsp; Fast • Fresh • Delicious</div>
  <div class="script" style="margin:0">Thank you for ordering! ♥</div>
</footer>

</body>
</html>
"""

#if __name__ == "__main__":
 #   app.run(debug=True)
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)