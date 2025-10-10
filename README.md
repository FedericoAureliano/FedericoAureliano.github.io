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

## Quick Start

1. **Fork and then clone the repository**
   ```bash
   git clone https://github.com/FedericoAureliano/FedericoAureliano.github.io.git
   cd FedericoAureliano.github.io
   ```

2. **Install Pandoc**
   - macOS: `brew install pandoc`
   - Linux: `sudo apt-get install pandoc` or see [Pandoc installation guide](https://pandoc.org/installing.html)
   - Windows: Download from [Pandoc releases](https://github.com/jgm/pandoc/releases)

3. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```
   This will create a virtual environment and install Python dependencies.

4. **Build the website**
   ```bash
   ./build.sh
   ```
   Generated HTML files will be in the `docs/` directory.

5. **Admire the website**
   - Open `docs/index.html`


## Requirements

- [Pandoc](https://pandoc.org/)
- Python >3.10
- Python packages (installed automatically by `setup.sh`):
  - panflute
  - pybtex
  - markdown
