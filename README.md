# Personal Academic Website

This repository contains the source code for Federico Mora Rocha's personal academic website, hosted at [federico.morarocha.ca](https://federico.morarocha.ca).

## Structure

- `index.md` — Main homepage content
- `cv.md` — Curriculum vitae
- `main.bib` - List of publications
- `posts/` — Blog posts in Markdown
- `templates/` — HTML templates for Pandoc
- `filters/` — Python filters for Pandoc
- `docs/` — Generated HTML files (served by GitHub Pages)

## Requirements

`build.sh` checks for each of these and stops with an error if one is missing.

- **[uv](https://docs.astral.sh/uv/)** — runs Pandoc with a Python (>= 3.10) environment that has the packages in `requirements.txt` (`panflute`, `pybtex`, `markdown`). uv downloads Python and the packages on first run, so you don't need to install Python or create a virtualenv yourself.
- **[Pandoc](https://pandoc.org/)** — converts the Markdown sources to HTML and PDF.
- **XeLaTeX** (from a TeX distribution such as MacTeX, BasicTeX, or TeX Live) — builds `docs/cv.pdf`.
- **LaTeX packages** used by `templates/cv.latex`: `fontspec`, `geometry`, `enumitem`, `fancyhdr`, `lastpage`, `hyperref`, `xcolor`, `longtable`, `booktabs`, `array`, `ragged2e`, `calc`, `varwidth`, `multirow`, `makecell`, `etoolbox`. The full MacTeX/TeX Live install has all of them; BasicTeX is missing several.
- **The Times New Roman font**, which the CV PDF uses. It ships with macOS; on Linux, install it (e.g. `sudo apt-get install ttf-mscorefonts-installer`).

## Quick Start

1. **Fork and then clone the repository**
   ```bash
   git clone https://github.com/FedericoAureliano/FedericoAureliano.github.io.git
   cd FedericoAureliano.github.io
   ```

2. **Install uv**
   - macOS: `brew install uv`
   - macOS/Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
   - See the [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/) for other options.

3. **Install Pandoc**
   - macOS: `brew install pandoc`
   - Linux: `sudo apt-get install pandoc` or see [Pandoc installation guide](https://pandoc.org/installing.html)
   - Windows: Download from [Pandoc releases](https://github.com/jgm/pandoc/releases)

4. **Install XeLaTeX and the LaTeX packages**
   - macOS (full, ~5 GB, includes everything): `brew install --cask mactex`
   - macOS (minimal): `brew install --cask basictex`, open a new terminal, then add the missing packages:
     ```bash
     sudo tlmgr update --self
     sudo tlmgr install enumitem fancyhdr lastpage booktabs ragged2e varwidth multirow makecell etoolbox
     ```
   - Linux: `sudo apt-get install texlive-xetex texlive-latex-extra`

   If a package is still missing, `build.sh` prints the exact `tlmgr install` command to run.

5. **Build the website**
   ```bash
   ./build.sh
   ```
   Generated files (`index.html`, `cv.html`, `cv.pdf`, `posts/*.html`) will be in the `docs/` directory. The first run takes a little longer while uv fetches Python and the dependencies.

6. **Admire the website**
   - Open `docs/index.html`
