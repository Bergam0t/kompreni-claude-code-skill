# Scenario 27: inside an existing Quarto project

**Setup:** A repo with a `_quarto.yml` (website) at its root, Quarto installed.

**Task:** Make a change, run `/kompreni:walkthrough`.

**Expect:** Writes the `.qmd` but doesn't render it, and says why: it belongs to the site project. The front matter has no `grid`, `theme`, `respect-user-color-scheme` or `include-in-header`, so the site's layout and theme apply. Says once that the site's next full render will include `kompreni/walkthroughs/` unless excluded in `_quarto.yml`. With `render=yes`, it renders and reports the HTML's path in the project's output folder.
