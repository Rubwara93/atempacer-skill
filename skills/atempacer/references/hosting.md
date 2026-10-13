# Putting the pacer online

The `dist/` folder has to be reachable over **HTTPS** for the home screen icon and the offline mode. Any static host works – there is no server code. Upload the *contents* of `dist/` (or the folder itself, then the link ends in `/dist/`).

Recommend one option, not all of them:

| Situation | Option | How |
|---|---|---|
| No website, wants it quick | **Netlify Drop** (free) | Open app.netlify.com/drop, drag the `dist` folder into the browser window, get a link. Without an account the site is removed after a short time, so create the free account and keep the site; it can be renamed to e.g. `firma-atem.netlify.app`. |
| Has a GitHub account | **GitHub Pages** (free) | New public repository → "uploading an existing file" → drop the contents of `dist/` → Settings → Pages → Branch `main` / root. Link: `https://<user>.github.io/<repo>/`. |
| Has a Cloudflare account | **Cloudflare Pages** (free) | Workers & Pages → Create → Pages → Upload assets → drag `dist`. |
| Has a website (IONOS, Strato, All-Inkl, WordPress host …) | **Own webspace** | Upload the contents of `dist/` via FTP/file manager into a new folder, e.g. `/atem/`. Link: `https://www.firma.de/atem/`. Looks most professional for clients. |

After uploading:
1. Open the link on a phone. Check that logo, colours and the exercise look right.
2. iPhone: Safari → Share → "Add to Home Screen". Android: Chrome menu → "Add to Home screen" / "Install app". The icon must show the brand icon, not a screenshot. If it shows a screenshot, `apple-touch-icon.png` wasn't uploaded next to `index.html`.
3. Start it once from the home screen while online – from then on it also opens offline.

**Updating:** rebuild, upload again (overwrite). Installed apps update on the next start with network.

**Without hosting at all:** `index.html` can be sent by email and opened on a laptop or desktop. On iPhones it won't run from a mail attachment, and no home screen icon is possible without a link.
