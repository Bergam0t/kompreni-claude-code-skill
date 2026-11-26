// Open the Compare tab named in the URL hash (#explain, #walkthrough,
// #code-tour), and keep the hash in step when the reader switches tabs,
// so a tab can be linked to directly.
(() => {
  const slug = text => text.trim().toLowerCase().replace(/\s+/g, "-");
  const links = () =>
    [...document.querySelectorAll(".kompreni-compare .nav-link")];

  const showFromHash = () => {
    const wanted = decodeURIComponent(location.hash.slice(1));
    const link = links().find(a => slug(a.textContent) === wanted);
    if (link && window.bootstrap) {
      bootstrap.Tab.getOrCreateInstance(link).show();
      link.closest(".panel-tabset").scrollIntoView();
    }
  };

  document.addEventListener("DOMContentLoaded", () => {
    for (const link of links()) {
      link.addEventListener("shown.bs.tab", () =>
        history.replaceState(null, "", "#" + slug(link.textContent)));
    }
    showFromHash();
  });
  window.addEventListener("hashchange", showFromHash);
})();
