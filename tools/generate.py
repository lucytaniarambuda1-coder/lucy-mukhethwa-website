#!/usr/bin/env python3
"""Builds the site into site/. Run from the repo root: python3 tools/generate.py"""
import html
import json
import os
import re
import shutil
import sys
import urllib.request
from email.utils import parsedate_to_datetime

sys.path.insert(0, os.path.dirname(__file__))
from content import SITE, BOOK, ARTICLES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "site")
S = SITE
SUB = S["substack"].rstrip("/")
SUBPUB = S.get("substack_pub", "").rstrip("/")
CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "substack_cache.json")


def load_substack():
    """Latest Substack posts from the RSS feed; falls back to the last saved copy if offline."""
    if not SUBPUB:
        return []
    try:
        req = urllib.request.Request(SUBPUB + "/feed", headers={"User-Agent": "Mozilla/5.0 (site build)"})
        xml = urllib.request.urlopen(req, timeout=15).read().decode("utf-8", "replace")
        posts = []
        for item in re.findall(r"<item>(.*?)</item>", xml, re.S):
            def field(tag):
                m = re.search(rf"<{tag}>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</{tag}>", item, re.S)
                return html.unescape(m.group(1).strip()) if m else ""
            date = field("pubDate")
            try:
                date = parsedate_to_datetime(date).strftime("%-d %B %Y")
            except Exception:
                pass
            posts.append({"title": field("title"), "dek": field("description"), "url": field("link"), "date": date})
        if posts:
            with open(CACHE, "w", encoding="utf-8") as f:
                json.dump(posts, f, indent=1, ensure_ascii=False)
            return posts
    except Exception as err:
        print("Substack feed unavailable, using saved copy:", err)
    if os.path.exists(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    return []


POSTS = load_substack()

ICON = {
    "ig": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
    "in": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.6c0-1.3 0-3-1.9-3s-2.1 1.4-2.1 2.9V21H9z"/></svg>',
    "book": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5V21h16"/></svg>',
    "pen": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
    "flow": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 12h4l3-8 4 16 3-8h4"/></svg>',
    "arrow": '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M5 12h14M13 6l6 6-6 6"/></svg>',
}
ARROW = ICON["arrow"]

NAV = [("Home", "/"), ("About", "/about/"), ("The Book", "/book/"), ("Articles", "/articles/"), ("Contact", "/contact/")]


def e(t):
    return html.escape(t, quote=True)


def page(path, title, desc, body, active=""):
    cur = ' class="active" aria-current="page"'
    nav = "".join(
        f'<li><a href="{href}"{cur if label == active else ""}>{label}</a></li>'
        for label, href in NAV
    )
    canonical = f'<link rel="canonical" href="{S["url"]}{path}">' if S["url"] else ""
    og_img = f'{S["url"]}/assets/og-image.jpg' if S["url"] else "/assets/og-image.jpg"
    sub_link = f'<li><a href="{SUB}" target="_blank" rel="noopener">Substack</a></li>' if SUB else ""
    doc = f"""<!DOCTYPE html>
<html lang="en-ZA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{canonical}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{og_img}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#FFFFFF">
<link rel="icon" href="/assets/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=EB+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/styles.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="nav">
  <div class="wrap">
    <a class="brand" href="/">Lucy Mukhethwa<small>Author · Founder · Strategist</small></a>
    <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
    <ul class="nav-links" id="menu">{nav}<li><a class="btn btn-pink" href="/book/#buy">Buy the book</a></li></ul>
  </div>
</header>
<main id="main">
{body}
</main>
<footer>
  <div class="wrap">
    <div class="cols">
      <div>
        <a class="brand" href="/">Lucy Mukhethwa</a>
        <p style="margin-top:1rem;max-width:26rem">Christian author, career strategist and founder of Flow Corner. Helping people find their flow in faith, work and life. Based in Johannesburg, South Africa.</p>
        <p class="verse">“Rejoice in the Lord always. I will say it again: Rejoice!” — Philippians 4:4</p>
      </div>
      <div>
        <h4>Explore</h4>
        <ul>{nav}{sub_link}</ul>
      </div>
      <div>
        <h4>Connect</h4>
        <ul>
          <li><a href="{S['amazon']}" target="_blank" rel="noopener">Buy on Amazon</a></li>
          <li><a href="{S['flow_corner']}" target="_blank" rel="noopener">Flow Corner</a></li>
          <li><a href="{S['instagram']}" target="_blank" rel="noopener">Instagram {S['instagram_handle']}</a></li>
          <li><a href="{S['linkedin']}" target="_blank" rel="noopener">LinkedIn</a></li>
        </ul>
      </div>
    </div>
    <div class="base"><span>© 2026 Lucy Mukhethwa. All rights reserved.</span><span>Johannesburg, South Africa</span></div>
  </div>
</footer>
<script>
(function(){{
  var b=document.querySelector('.nav-toggle'),m=document.getElementById('menu');
  b.addEventListener('click',function(){{var o=m.classList.toggle('open');b.setAttribute('aria-expanded',o);}});
  var els=document.querySelectorAll('.reveal');
  if(!('IntersectionObserver' in window)){{els.forEach(function(x){{x.classList.add('in')}});return;}}
  var io=new IntersectionObserver(function(es){{es.forEach(function(en){{if(en.isIntersecting){{en.target.classList.add('in');io.unobserve(en.target);}}}})}},{{threshold:.12}});
  els.forEach(function(x){{if(x.getBoundingClientRect().top<innerHeight){{x.style.transition='none';x.classList.add('in');}}else{{io.observe(x);}}}});
}})();
</script>
</body>
</html>
"""
    dest = os.path.join(OUT, path.strip("/"), "index.html") if path != "/" else os.path.join(OUT, "index.html")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(doc)


# ---------- shared blocks ----------

def article_cards(items):
    out = []
    for a in items:
        out.append(f"""<a class="article-card reveal" href="/articles/{a['slug']}/">
  <div class="top"><div class="meta" >{e(a['tag'])}</div><h3>{e(a['title'])}</h3></div>
  <div class="body"><p>{e(a['dek'])}</p><span class="read-more">Read · {a['minutes']} min →</span></div>
</a>""")
    return "\n".join(out)


def substack_cards(items):
    out = []
    for p in items:
        out.append(f"""<a class="article-card reveal" href="{e(p['url'])}" target="_blank" rel="noopener">
  <div class="top"><div class="meta">Substack · {e(p['date'])}</div><h3>{e(p['title'])}</h3></div>
  <div class="body"><p>{e(p['dek'])}</p><span class="read-more">Read on Substack →</span></div>
</a>""")
    return "\n".join(out)


def subscribe_block():
    if SUBPUB:
        action = f"""<a class="btn btn-navy" href="{SUBPUB}/subscribe" target="_blank" rel="noopener">Subscribe on Substack {ARROW}</a>
<p style="margin-top:1rem;font-size:1rem">Free. New posts go straight to your inbox. <a href="{SUB}" target="_blank" rel="noopener">See my Substack profile →</a></p>"""
    else:
        action = """<form name="newsletter" method="POST" data-netlify="true" netlify-honeypot="company" action="/thanks/">
  <input type="hidden" name="form-name" value="newsletter">
  <p class="hidden"><label>Leave this empty <input name="company"></label></p>
  <input type="email" name="email" placeholder="Your email address" required aria-label="Email address">
  <button class="btn btn-navy" type="submit">Send me new writing</button>
</form>"""
    return f"""<div class="subscribe reveal">
  <div>
    <span class="eyebrow" >Letters from the middle</span>
    <h2>Get my new writing in your inbox</h2>
    <p>Honest reflections on faith, waiting seasons, purpose and work. No spam, just a note when something new is up.</p>
  </div>
  <div>{action}</div>
</div>"""


def flow_band():
    return f"""<div class="fc-band reveal">
  <img src="/assets/logo-mark.png" alt="Flow Corner logo" width="110" height="110">
  <div>
    <span class="eyebrow" >My business</span>
    <h2>Flow Corner: helping you find your flow</h2>
    <p>Flow Corner is my career development and personal growth platform. CVs that get past the filters, LinkedIn profiles people can find, career guidance, free tools, a learning hub and a weekly opportunities board for South African job seekers.</p>
  </div>
  <a class="btn btn-navy" href="{S['flow_corner']}" target="_blank" rel="noopener">Visit Flow Corner {ARROW}</a>
</div>"""


def buy_buttons(extra=""):
    return f"""<a class="btn btn-pink" href="{S['amazon']}" target="_blank" rel="noopener">Buy on Amazon {ARROW}</a>{extra}"""


# ---------- pages ----------

def home():
    marquee_words = ["Passion", "Purpose", "Peace", "Faith", "Becoming", "Career", "Flow"]
    mq = "".join(f"<span>{w}</span><span>✦</span>" for w in marquee_words) * 4
    quotes = "".join(f'<div class="quote-card reveal"><p class="quote">“{e(q)}”</p></div>' for q in BOOK["quotes"][:3])
    body = f"""
<section class="hero">
  <div class="wrap">
    <div>
      <span class="eyebrow">Hi, I’m Lucy</span>
      <h1>Faithful in the <span class="hl">middle</span>. Building what’s next.</h1>
      <div class="roles"><span>Christian author</span><span>Founder, Flow Corner</span><span>Career strategist</span><span>I&amp;O Psychology</span></div>
      <p class="lead">I write for people who love God but feel behind, and I help capable people stop getting filtered out of the careers they’re made for. My debut book, <em>Passion. Purpose. Peace.</em>, is out now.</p>
      <div class="ctas">
        <a class="btn btn-pink" href="/book/#buy">Buy the book {ARROW}</a>
        <a class="btn btn-ghost" href="{S['flow_corner']}" target="_blank" rel="noopener">Visit Flow Corner</a>
      </div>
    </div>
    <div class="hero-photo">
      <div class="frame"><img src="/assets/lucy-sea.jpg" alt="Lucy Mukhethwa standing by the ocean in a floral dress" width="700" height="700"></div>
      <div class="sticker s1">Debut book<small>out now on Amazon</small></div>
      <div class="sticker s2">Founder<small>Flow Corner</small></div>
    </div>
  </div>
</section>
<div class="marquee" aria-hidden="true"><div>{mq}</div></div>

<section>
  <div class="wrap split">
    <div class="photo-stack reveal"><span class="tape"></span><img src="/assets/re3.jpg" alt="Lucy looking out over the sea from a wooden deck" width="1000" height="1000" loading="lazy"></div>
    <div class="reveal">
      <span class="eyebrow">About me</span>
      <h2>Writer, strategist, and a lifelong learner</h2>
      <p>I’m Lucy Mukhethwa, a South African writer based in Johannesburg. My three guiding words are <strong>passion, purpose and peace</strong>, and they shape everything I build.</p>
      <p>By day I work in AI projects and leadership support, after 6+ years in HR and operations. I’m studying a Master’s in Industrial &amp; Organisational Psychology, with my research focused on career psychology. And I run Flow Corner, where I help people get hired and grow.</p>
      <p>Rooted in my Christian faith, I care about helping people uncover the value in who they are, not just what they achieve.</p>
      <a class="btn btn-outline" href="/about/" style="margin-top:.6rem">Read my story {ARROW}</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap book-feature">
    <div class="book-cover reveal"><img src="/assets/book-cover.jpg" alt="Cover of Passion. Purpose. Peace. Becoming Whole in Christ by Lucy Mukhethwa" width="562" height="900" loading="lazy"><span class="badge">Out now</span></div>
    <div class="reveal">
      <span class="eyebrow">My debut book</span>
      <h2>{BOOK['title']}</h2>
      <p class="sub">{BOOK['subtitle']}</p>
      <p class="big-hook">{BOOK['hook']}</p>
      <p style="margin-top:1rem">{BOOK['blurb'][0]}</p>
      <div class="buy">{buy_buttons(' <a class="btn btn-ghost" href="/book/">Look inside</a>')}</div>
      <div class="book-meta"><div><b>Formats</b>{BOOK['formats']}</div><div><b>Released</b>{BOOK['released']}</div><div><b>Includes</b>Prayers &amp; reflection questions</div></div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head center reveal" style="text-align:center">
      <span class="eyebrow">What I stand for</span>
      <h2>Three words I try to live by</h2>
      <p>They aren’t goals to achieve. They’re realities to return to, one faithful day at a time.</p>
    </div>
    <div class="grid g3">
      <div class="card value reveal"><div class="num">01</div><h3>Passion</h3><p>Passion doesn’t die, it gets buried. I believe God restores what life covered up, without pressure, and that your gifts still matter.</p></div>
      <div class="card value reveal"><div class="num">02</div><h3>Purpose</h3><p>Purpose is built daily, not discovered once. Small, faithful steps at work, in ministry and at home add up to a life that counts.</p></div>
      <div class="card value reveal"><div class="num">03</div><h3>Peace</h3><p>Peace is a practice. Obedience over hustle, honesty over performance, and trusting that God was never rushing you.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal">
      <span class="eyebrow">Where I’m going</span>
      <h2>My dreams, out loud</h2>
      <p>Writing them here keeps me honest. This is what I’m building towards.</p>
    </div>
    <div class="grid g4">
      <div class="card reveal"><div class="icon">i.</div><h3>Write more books</h3><p>My second book, <em>Meet Me in the Middle</em>, is in the works. I want to keep writing honest, faith-filled books for people in the middle.</p></div>
      <div class="card reveal"><div class="icon y">ii.</div><h3>Grow Flow Corner</h3><p>From an online platform to a physical internet café and digital learning hub, where people can print a CV, learn skills and get help applying.</p></div>
      <div class="card reveal"><div class="icon n">iii.</div><h3>Help other writers</h3><p>Through Author Corner, I want to walk other South African writers from first draft to published book, the way I learned to.</p></div>
      <div class="card reveal"><div class="icon">iv.</div><h3>Finish my master’s</h3><p>Complete my research in career psychology, so the advice I give people is grounded in evidence, not guesswork.</p></div>
    </div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">From the book</span><h2>Lines I needed to hear first</h2></div>
    <div class="grid g3">{quotes}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal" style="display:flex;justify-content:space-between;align-items:flex-end;gap:1.5rem;flex-wrap:wrap;max-width:none">
      <div style="max-width:620px"><span class="eyebrow">Articles</span><h2>Latest writing</h2><p>Fresh from my Substack: faith, growth, and life in the middle.</p></div>
      <a class="btn btn-outline" href="/articles/">All articles {ARROW}</a>
    </div>
    <div class="grid g3">{substack_cards(POSTS[:3]) if POSTS else article_cards(ARTICLES[:3])}</div>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">{flow_band()}</div>
</section>

<section style="padding-top:0">
  <div class="wrap">{subscribe_block()}</div>
</section>
"""
    page("/", "Lucy Mukhethwa | Author, Career Strategist & Founder of Flow Corner",
         "Christian author of Passion. Purpose. Peace., career strategist and founder of Flow Corner. Read my story, my articles, and buy the book.", body, "Home")


def about():
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow" >About Lucy</span>
    <h1>Hi, I’m <span class="text-pink">Lucy</span>.</h1>
    <p>Christian author, career strategist, AI projects manager, master’s student in Industrial &amp; Organisational Psychology, and the founder of Flow Corner. Johannesburg is home.</p>
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">My bio</span>
      <h2>Faith, people, and the work in between</h2>
      <p>My full name is Mukhethwa Lucytania Rambuda, but most people call me Lucy. I’m a South African writer, reader and lifelong learner whose three guiding words are peace, purpose and passion.</p>
      <p>With a background in Industrial Psychology, I’m passionate about people development: helping individuals uncover the value in who they are, not just what they achieve. I have 6+ years in HR and operations, growing from HR Assistant to Generalist and into operations and leadership support. Today I work as an AI Projects Manager, running AI adoption projects like voice bots, chatbot integration and automation strategy.</p>
      <p>Rooted in my Christian faith, I write from lived experience: the quiet seasons of waiting, the courage obedience requires, and the slow, steady work of becoming whole in Christ.</p>
      <p>And through <a href="{S['flow_corner']}" target="_blank" rel="noopener">Flow Corner</a>, I help capable people stop getting filtered out because of a weak CV or a LinkedIn profile nobody can find.</p>
    </div>
    <div class="photo-stack reveal"><span class="tape"></span><img src="/assets/re2.jpg" alt="Lucy smiling on a wooden deck above the sea" width="1000" height="1000" loading="lazy"></div>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">My story</span><h2>A road full of detours</h2><p>Every time I thought I had it figured out, a door closed. And every time, God redirected me. Not loudly. Faithfully.</p></div>
    <ol class="timeline">
      <li class="reveal"><h3>The doctor dream</h3><p>In high school I wanted to study medicine. I didn’t qualify.</p></li>
      <li class="reveal"><h3>Industrial Psychology</h3><p>So I chose Industrial Psychology. Practical. “Close enough.” It became the foundation for everything I do now.</p></li>
      <li class="reveal"><h3>A bank internship, then COVID</h3><p>My first job was an internship at a bank. Then the contract ended, and I was unemployed with a degree.</p></li>
      <li class="reveal"><h3>Trying other doors</h3><p>Police, like my dad? That door never opened. Teaching, like my mom? PGCE, practicals, student teaching. Honest work, but not my work.</p></li>
      <li class="reveal"><h3>HR, and something clicked</h3><p>An HR Generalist role came up, and it fitted. HR grew into operations, C-suite support and AI projects.</p></li>
      <li class="reveal"><h3>Author and founder</h3><p>I started Flow Corner, began my master’s, and on {BOOK['released']} I published my debut book. I’m doing the work I once prayed for, and I never forced it into existence.</p></li>
    </ol>
    <a class="btn btn-outline reveal" href="/articles/i-wanted-to-be-a-doctor/" style="margin-top:1rem">Read the full story {ARROW}</a>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Qualifications &amp; experience</span><h2>What I bring</h2></div>
    <div class="grid g2">
      <div class="card qual reveal"><div><span class="status">In progress</span><h3>Master’s in Industrial &amp; Organisational Psychology</h3><p>UNISA, research master’s. My dissertation focuses on career psychology.</p></div></div>
      <div class="card qual reveal"><div><span class="status">Completed</span><h3>Degree in Industrial Psychology</h3><p>The foundation of my work in people development, HR and careers.</p></div></div>
      <div class="card qual reveal"><div><span class="status">6+ years</span><h3>HR &amp; Operations</h3><p>HR Assistant → Generalist → Coordinator. Employee relations, policy, onboarding, compliance, and executive-level operations across multiple countries.</p></div></div>
      <div class="card qual reveal"><div><span class="status">Current</span><h3>AI Projects Manager</h3><p>Leading AI adoption in a contact-centre environment: voice bots, chatbot integration and automation strategy, working with C-suite leadership.</p></div></div>
      <div class="card qual reveal"><div><span class="status">Published 2026</span><h3>Author</h3><p><em>Passion. Purpose. Peace. Becoming Whole in Christ</em>, written, designed and published end to end.</p></div></div>
      <div class="card qual reveal"><div><span class="status">Founder</span><h3>Flow Corner &amp; web projects</h3><p>Built and run Flow Corner, and built websites for corporate and church organisations.</p></div></div>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="wrap big-quote reveal">
    <p class="quote">“What I want is simple: for capable people to stop getting filtered out, and for people in the middle to know they are not late. They are becoming.”</p>
    <cite>Lucy Mukhethwa</cite>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">What I’m working on</span><h2>Right now</h2></div>
    <div class="grid g3">
      <div class="card reveal"><div class="icon">Writing</div><h3>Meet Me in the Middle</h3><p>My second book. Writing and editing, a few focused sessions a week.</p></div>
      <div class="card reveal"><div class="icon y">Building</div><h3>The Flow Corner café</h3><p>Planning a physical internet café and digital learning hub, so help is close for people without a laptop at home.</p></div>
      <div class="card reveal"><div class="icon n">Serving</div><h3>Author Corner</h3><p>Guides, templates and coaching for writers who want to publish their own book.</p></div>
    </div>
  </div>
</section>

<section style="padding-top:0"><div class="wrap">{flow_band()}</div></section>
"""
    page("/about/", "About Lucy Mukhethwa | Author & Career Strategist",
         "My story, qualifications, experience and what I'm building: author, career strategist, AI projects manager and founder of Flow Corner.", body, "About")


def book():
    toc = []
    for part, label, title in BOOK["contents"]:
        if part and part != "Bonus":
            toc.append(f'<li class="part">{part}</li>')
        elif part == "Bonus":
            toc.append('<li class="part">Bonus</li>')
        toc.append(f'<li><span class="n">{label}</span><span>{e(title)}</span></li>')
    inside = "".join(f"<li>{e(i)}</li>" for i in BOOK["inside"])
    quotes = "".join(f'<div class="quote-card reveal"><p class="quote">“{e(q)}”</p></div>' for q in BOOK["quotes"])
    foryou = "".join(f'<div class="card reveal"><p style="font-size:1.1rem;color:var(--deep-blue)">…{e(x)}.</p></div>' for x in BOOK["for_you_if"])
    body = f"""
<section style="padding-top:5rem">
  <div class="wrap book-feature">
    <div class="book-cover reveal"><img src="/assets/book-cover.jpg" alt="Cover of Passion. Purpose. Peace. Becoming Whole in Christ" width="562" height="900"><span class="badge">Out now</span></div>
    <div class="reveal">
      <span class="eyebrow">The book</span>
      <h1 style="font-size:clamp(2.6rem,5.4vw,4rem)">{BOOK['title']}</h1>
      <p class="sub">{BOOK['subtitle']}</p>
      <p class="big-hook">{BOOK['hook']}</p>
      {''.join(f'<p style="margin-top:1rem">{b}</p>' for b in BOOK['blurb'])}
      <div class="buy">{buy_buttons()}</div>
      <div class="book-meta"><div><b>Formats</b>{BOOK['formats']}</div><div><b>Released</b>{BOOK['released']}</div><div><b>ISBN</b>{BOOK['isbn']}</div></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap split">
    <div class="reveal">
      <span class="eyebrow">Inside this book</span>
      <h2>You will discover</h2>
      <ul class="prose" style="padding:0;margin:0 0 0 1.2rem;font-size:1.05rem">{inside}</ul>
      <p style="margin-top:1.2rem;color:var(--ink-soft)"><strong >Bonus section:</strong> {BOOK['bonus']}</p>
    </div>
    <div class="card reveal" style="padding:2.4rem">
      <span class="eyebrow">Contents</span>
      <ul class="toc">{''.join(toc)}</ul>
    </div>
  </div>
</section>

<section class="on-dark">
  <div class="wrap big-quote reveal">
    <p class="quote">“{BOOK['dedication']}”</p>
    <cite>The dedication</cite>
  </div>
</section>

<section class="tint">
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Who it’s for</span><h2>This book is for you if…</h2></div>
    <div class="grid g3">{foryou}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">Lines from the book</span><h2>A few to hold on to</h2></div>
    <div class="grid g3">{quotes}</div>
  </div>
</section>

<section class="tint" id="buy">
  <div class="wrap">
    <div class="section-head center reveal" style="text-align:center"><span class="eyebrow">Get your copy</span><h2>Buy the book</h2><p>Read it on your own, journal through it, or study it with your small group. It also makes a good gift for a friend who is in the middle.</p></div>
    <div class="grid g3">
      <div class="card buy-card featured reveal"><div class="icon">eBook</div><h3>Kindle eBook</h3><p class="price-note">Read on any phone, tablet or Kindle with the free Kindle app.</p><a class="btn btn-pink" href="{S['amazon']}" target="_blank" rel="noopener">Buy on Amazon {ARROW}</a></div>
      <div class="card buy-card reveal"><div class="icon y">Print</div><h3>Paperback</h3><p class="price-note">5.5 × 8.5 inch paperback, printed and shipped by Amazon.</p><a class="btn btn-navy" href="{S['amazon']}" target="_blank" rel="noopener">Order the paperback {ARROW}</a></div>
      <div class="card buy-card reveal"><div class="icon n">Locally</div><h3>In South Africa?</h3><p class="price-note">For a local or signed copy, a church order, or a book club set, send me a message and I’ll tell you what’s available.</p><a class="btn btn-outline" href="/contact/?reason=Book%20order">Ask about a copy {ARROW}</a></div>
    </div>
    <p class="reveal" style="text-align:center;margin-top:2rem;color:var(--ink-soft)">Already read it? A short Amazon review means the world to me</p>
  </div>
</section>
"""
    page("/book/", "Passion. Purpose. Peace. — Becoming Whole in Christ | Lucy Mukhethwa",
         "For everyone in the middle: faithful, but tired. Buy Passion. Purpose. Peace. by Lucy Mukhethwa on Kindle and paperback.", body, "The Book")


def articles_index():
    sub = f' <a class="btn btn-yellow" href="{SUB}" target="_blank" rel="noopener">Read me on Substack {ARROW}</a>' if SUB else ""
    substack_section = f"""<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">On my Substack</span><h2>Latest posts</h2><p>I write regularly on Substack about faith, growth, relationships and everyday life. Every post opens on Substack.</p></div>
    <div class="grid g3">{substack_cards(POSTS)}</div>
  </div>
</section>""" if POSTS else ""
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow" >Articles</span>
    <h1>Writing from the <span class="text-pink">middle</span></h1>
    <p>Honest reflections on faith, waiting seasons, purpose and work. Some of these grew out of my book, and some out of my own detours.</p>
    <div style="margin-top:1.8rem;display:flex;gap:.8rem;flex-wrap:wrap"><a class="btn btn-pink" href="/book/">Read the book {ARROW}</a>{sub}</div>
  </div>
</section>
{substack_section}
<section>
  <div class="wrap">
    <div class="section-head reveal"><span class="eyebrow">From the book</span><h2>Reflections from <em>Passion. Purpose. Peace.</em></h2><p>Pieces that grew out of my book and my own detours.</p></div>
    <div class="grid g3">{article_cards(ARTICLES)}</div>
    <div class="card reveal" style="margin-top:2.5rem;display:flex;justify-content:space-between;align-items:center;gap:1.5rem;flex-wrap:wrap">
      <div><span class="eyebrow">Career writing</span><h3>Looking for CV, LinkedIn and job-hunting advice?</h3><p>My career articles and free guides live on the Flow Corner Learning Hub.</p></div>
      <a class="btn btn-navy" href="{S['flow_corner']}/learning-hub/" target="_blank" rel="noopener">Flow Corner Learning Hub {ARROW}</a>
    </div>
  </div>
</section>
<section style="padding-top:0"><div class="wrap">{subscribe_block()}</div></section>
"""
    page("/articles/", "Articles | Lucy Mukhethwa", "Articles by Lucy Mukhethwa on faith, waiting seasons, obedience, peace and purpose.", body, "Articles")


def article(a, idx):
    nxt = ARTICLES[(idx + 1) % len(ARTICLES)]
    sub = f'<p style="text-align:center;margin:-2rem 0 2.5rem"><a href="{SUB}" target="_blank" rel="noopener">More on my Substack →</a></p>' if SUB else ""
    body = f"""
<article>
<header class="post-hero">
  <div class="wrap">
    <a class="back" href="/articles/">← All articles</a>
    <div class="meta" >{e(a['tag'])} · {a['minutes']} min read</div>
    <h1>{e(a['title'])}</h1>
    <p>{e(a['dek'])}</p>
    <div class="byline"><img src="/assets/lucy-face.jpg" alt="" width="46" height="46"><span>By <strong>Lucy Mukhethwa</strong></span></div>
  </div>
</header>
<div class="wrap"><div class="prose">{a['body']}</div></div>
</article>
<div class="wrap">
  <div class="post-end">
    <img src="/assets/book-cover.jpg" alt="Passion. Purpose. Peace. book cover" width="110" height="176" loading="lazy">
    <div><h3>Want more like this?</h3><p>My book <em>Passion. Purpose. Peace.</em> goes deeper, with prayers and reflection questions for every chapter.</p>{buy_buttons()}</div>
  </div>
  {sub}
  <p style="max-width:720px;margin:0 auto 5rem">Next article: <a href="/articles/{nxt['slug']}/" style="font-weight:700">{e(nxt['title'])} →</a></p>
</div>
"""
    page(f"/articles/{a['slug']}/", f"{a['title']} | Lucy Mukhethwa", a["dek"], body, "Articles")


def contact():
    body = f"""
<section class="page-hero">
  <div class="wrap">
    <span class="eyebrow" >Contact</span>
    <h1>Let’s <span class="text-pink">talk</span></h1>
    <p>Book orders, speaking or ministry invitations, interviews, collaborations, or just to say the book helped you. I read every message.</p>
  </div>
</section>
<section>
  <div class="wrap split" style="align-items:start">
    <form class="form card reveal" name="contact" method="POST" data-netlify="true" netlify-honeypot="company" action="/thanks/">
      <input type="hidden" name="form-name" value="contact">
      <p class="hidden"><label>Leave this empty <input name="company"></label></p>
      <label>Your name<input name="name" required autocomplete="name"></label>
      <label>Email<input type="email" name="email" required autocomplete="email"></label>
      <label>What is it about?
        <select name="reason" id="reason">
          <option>Book order</option>
          <option>Speaking or ministry invitation</option>
          <option>Interview or media</option>
          <option>Flow Corner services</option>
          <option>Collaboration</option>
          <option selected>Just saying hello</option>
        </select>
      </label>
      <label>Message<textarea name="message" required></textarea></label>
      <button class="btn btn-pink" type="submit" style="justify-self:start">Send message {ARROW}</button>
    </form>
    <div class="reveal">
      <span class="eyebrow">Find me online</span>
      <h2 style="margin-bottom:1.4rem">Other ways to connect</h2>
      <ul class="links-list">
        <li><a href="{S['instagram']}" target="_blank" rel="noopener">{ICON['ig']}<div>Instagram<span>{S['instagram_handle']} · faith, books and behind the scenes</span></div></a></li>
        <li><a href="{S['linkedin']}" target="_blank" rel="noopener">{ICON['in']}<div>LinkedIn<span>Work, HR and AI projects</span></div></a></li>
        <li><a href="{S['flow_corner']}" target="_blank" rel="noopener">{ICON['flow']}<div>Flow Corner<span>CVs, LinkedIn, career help and opportunities</span></div></a></li>
        <li><a href="{S['amazon']}" target="_blank" rel="noopener">{ICON['book']}<div>Passion. Purpose. Peace.<span>Kindle and paperback on Amazon</span></div></a></li>
        {f'<li><a href="{SUB}" target="_blank" rel="noopener">{ICON["pen"]}<div>Substack<span>My newsletter and longer writing</span></div></a></li>' if SUB else ''}
      </ul>
    </div>
  </div>
</section>
<script>
(function(){{var r=new URLSearchParams(location.search).get('reason');if(!r)return;var s=document.getElementById('reason');for(var i=0;i<s.options.length;i++){{if(s.options[i].text===r)s.selectedIndex=i;}}}})();
</script>
"""
    page("/contact/", "Contact | Lucy Mukhethwa", "Get in touch with Lucy Mukhethwa about book orders, speaking, interviews, Flow Corner or collaborations.", body, "Contact")


def thanks():
    body = f"""
<section class="page-hero" style="min-height:60vh">
  <div class="wrap">
    <span class="eyebrow" >Thank you</span>
    <h1>Got it, <span class="text-pink">thank you</span></h1>
    <p>Your message is with me. I’ll get back to you as soon as I can.</p>
    <div style="margin-top:2rem;display:flex;gap:.8rem;flex-wrap:wrap"><a class="btn btn-pink" href="/articles/">Read an article {ARROW}</a><a class="btn btn-ghost" href="/">Back home</a></div>
  </div>
</section>"""
    page("/thanks/", "Thank you | Lucy Mukhethwa", "Thanks for getting in touch.", body)


def not_found():
    body = f"""
<section class="page-hero" style="min-height:60vh">
  <div class="wrap">
    <span class="eyebrow" >404</span>
    <h1>This page is still in the <span class="text-pink">middle</span>.</h1>
    <p>It doesn’t exist (yet). Let’s get you somewhere that does.</p>
    <div style="margin-top:2rem"><a class="btn btn-pink" href="/">Go home {ARROW}</a></div>
  </div>
</section>"""
    page("/404-tmp/", "Page not found | Lucy Mukhethwa", "Page not found.", body)
    shutil.move(os.path.join(OUT, "404-tmp", "index.html"), os.path.join(OUT, "404.html"))
    os.rmdir(os.path.join(OUT, "404-tmp"))


def sitemap():
    if not S["url"]:
        return
    paths = ["/", "/about/", "/book/", "/articles/", "/contact/"] + [f"/articles/{a['slug']}/" for a in ARTICLES]
    urls = "".join(f"<url><loc>{S['url']}{p}</loc></url>" for p in paths)
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {S['url']}/sitemap.xml\n")
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')


def main():
    # Empty site/ without removing the folder itself (keeps a running preview server happy).
    os.makedirs(OUT, exist_ok=True)
    for name in os.listdir(OUT):
        full = os.path.join(OUT, name)
        shutil.rmtree(full) if os.path.isdir(full) else os.remove(full)
    shutil.copytree(os.path.join(ROOT, "static"), OUT, dirs_exist_ok=True)
    home(); about(); book(); articles_index(); contact(); thanks(); not_found()
    for i, a in enumerate(ARTICLES):
        article(a, i)
    sitemap()
    print("Built", sum(len(f) for _, _, f in os.walk(OUT)), "files into site/")


if __name__ == "__main__":
    main()
