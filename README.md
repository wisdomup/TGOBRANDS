# TGO Brands

The TGO Brands website — English at `/`, 中文 at `/zh/`. v4 positions TGO as a senior brand operator and
R&D partner for Chinese brands entering Pakistan, India, the Philippines and the UAE: services, the Launch
programme, market playbooks, an entry estimator, Expeditions and a Partner Portal preview.

| Folder | What it is |
| --- | --- |
| `site/` | The production site: static, pre-rendered, built with the Python standard library. Copy, templates and styles live here — see [site/README.md](site/README.md). |
| `api/` | Vercel functions. `lead.py` delivers partner applications by email and WhatsApp — setup in [site/README.md](site/README.md#lead-delivery-apilead). |
| `design/` | The "TGO Brands v3 Glass" Claude Design prototype the site was built from. Reference only; not deployed. |

```bash
python3 site/build.py                                   # writes site/dist
python3 -m http.server 8000 --directory site/dist       # preview at http://localhost:8000
```

Vercel builds every push to `main` with `python3 site/build.py --out dist` and serves `dist/` (see `vercel.json`).
