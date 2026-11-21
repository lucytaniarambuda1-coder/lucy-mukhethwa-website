# Lucy Mukhethwa — personal website

Author site for Lucy Mukhethwa: bio, *Passion. Purpose. Peace.*, articles, Flow Corner link and contact.

- All the words live in `tools/content.py` (site links, book, articles).
- Styles: `static/assets/styles.css`, built on the Lucy Mukhethwa design system (white, Cormorant Garamond + EB Garamond, pink and blue accents).
- Build: `python3 tools/generate.py` writes the site into `site/`. Netlify runs this on every push to `main` (see `netlify.toml`).
- Substack posts are read from the RSS feed each time the site builds (`tools/substack_cache.json` is the saved copy). A daily GitHub Action (`.github/workflows/substack.yml`, 07:00 SAST) commits that file when there is a new post, which redeploys the site. Run it any time from the Actions tab → "Check Substack for new posts" → Run workflow.
