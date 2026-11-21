# Lucy Mukhethwa — personal website

Author site for Lucy Mukhethwa: bio, *Passion. Purpose. Peace.*, articles, Flow Corner link and contact.

- All the words live in `tools/content.py` (site links, book, articles).
- Styles: `static/assets/styles.css`, built on the Lucy Mukhethwa design system (white, Cormorant Garamond + EB Garamond, pink and blue accents).
- Build: `python3 tools/generate.py` writes the site into `site/`. Netlify runs this on every push to `main` (see `netlify.toml`).
- Substack posts are read from the RSS feed each time the site builds; `tools/substack_cache.json` is the saved copy used when the feed can't be reached (Substack blocks build servers). To add a new post: run `python3 tools/generate.py` on a Mac (where the feed works) and commit the updated `tools/substack_cache.json`.
