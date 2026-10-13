window.addEventListener("load", () => {
  let pifr = document.getElementById("preview-iframe");
  const preview = document.getElementById("preview");
  const openBtn = document.getElementById("preview-open");
  const cache = new Map(); // href -> Promise<string>

  document.querySelectorAll("a[href^='/p/']").forEach(a => {
    a.addEventListener("mouseover", hoverInnerLink);
  });

  let loading = false;
  let next = null;            // { href, pageY, clientY }
  let currentPreview = null;
  let currentPreviewY = null;

  function hoverInnerLink(e) {
    if (window.innerWidth < 1000) return;
    // currentTarget is always the <a>, even when hovering a child like <em>
    const href = e.currentTarget.href;
    if (href === currentPreview) return;
    next = { href, pageY: e.pageY, clientY: e.clientY };
    if (!loading) loadPreview();
  }

  function fetchPage(href) {
    if (!cache.has(href)) {
      const p = fetch(href)
        .then(r => {
          if (!r.ok) throw new Error(r.status + " " + href);
          return r.text();
        })
        .catch(err => {
          cache.delete(href); // allow retry on a later hover
          throw err;
        });
      cache.set(href, p);
    }
    return cache.get(href);
  }

  // srcdoc documents have the URL about:srcdoc, so relative links, images and
  // stylesheets would break without a <base>. target=_top makes any link
  // inside the preview navigate the main window.
  function withBase(html, href) {
    const base = `<base href="${href}" target="_top">`;
    const headRe = /<head[^>]*>/i;
    return headRe.test(html)
      ? html.replace(headRe, m => m + base)
      : base + html;
  }

  function positionPreview(pageY, clientY) {
    // amount of padding needed to put the preview at mouse location
    let y = pageY
      - document.getElementById("top-posts").getBoundingClientRect().height
      - 38;

    const approxPreviewHeight = window.innerHeight / 2 + 100;
    if (clientY > window.innerHeight - approxPreviewHeight) {
      y -= clientY - (window.innerHeight - approxPreviewHeight);
    }
    if (y < 0) y = 0;
    if (currentPreviewY !== null && Math.abs(y - currentPreviewY) < 30) {
      y = currentPreviewY;
    }
    preview.style.marginTop = y + "px";
    currentPreviewY = y;
  }

  // Build a brand-new iframe with srcdoc already set, so its content arrives
  // as the iframe's *first* load. A first load never creates a session-history
  // entry, in Firefox or anywhere else. Re-navigating an existing iframe
  // (src, location.replace, or even changing srcdoc) can.
  function showHtml(html, href) {
    return new Promise(resolve => {
      const fresh = pifr.cloneNode(false);
      fresh.removeAttribute("src");
      fresh.style.display = "none"; // still loads; swapped in when ready (no flicker)
      fresh.srcdoc = html;

      fresh.addEventListener("load", () => {
        const doc = fresh.contentDocument; // null if the iframe is sandboxed
        if (doc) {
          doc.addEventListener("click", e => {
            e.preventDefault();
            window.top.location = href;
          });
        }
        pifr.remove();
        fresh.style.display = "block";
        pifr = fresh;
        resolve();
      }, { once: true });

      pifr.after(fresh);
    });
  }

  async function loadPreview() {
    if (!next) return;
    const { href, pageY, clientY } = next;
    next = null;
    loading = true;
    currentPreview = href;

    try {
      const html = await fetchPage(href);
      if (next) {
        // user already hovered something else; skip this stale one
        currentPreview = null;
      } else {
        positionPreview(pageY, clientY);
        openBtn.style.display = "block";
        openBtn.onclick = () => { window.top.location = href; };
        await showHtml(withBase(html, href), href);
      }
    } catch (err) {
      console.warn("preview failed:", err);
      currentPreview = null;
    }

    loading = false;
    loadPreview(); // handle anything hovered while we were busy
  }
});
