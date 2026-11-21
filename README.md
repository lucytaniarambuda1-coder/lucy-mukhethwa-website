# Lucy Mukhethwa — personal website

Author site for Lucy Mukhethwa: bio, *Passion. Purpose. Peace.*, articles, Flow Corner link and contact.

- All the words live in `tools/content.py` (site links, book, articles).
- Styles: `static/assets/styles.css`, built on the Lucy Mukhethwa design system (white, Cormorant Garamond + EB Garamond, pink and blue accents).
- Build: `python3 tools/generate.py` writes the site into `site/`. Netlify runs this on every push to `main` (see `netlify.toml`).
- To add your Substack, paste its address into `SITE["substack"]` in `tools/content.py`.
