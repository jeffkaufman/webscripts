window.addEventListener("load", () => {
  var pifr = document.getElementById("preview-iframe");
  document.querySelectorAll("a[href^='/p/']").forEach(a => {
    a.addEventListener("mouseover", hoverInnerLink);
  });


  var waitingForLoad = false;
  var nextPreview = null;
  var currentPreview = null;
  var nextPreviewY = null;
  var currentPreviewY = null;

  function hoverInnerLink(e) {
    if (window.innerWidth < 1000) {
      return;
    }
    if (currentPreview == e.target.href) {
      return;
    }
    nextPreview = e.target.href;
    nextPreviewPageY = e.pageY;
    nextPreviewClientY = e.clientY;
    if (waitingForLoad) {
      return;
    }
    loadPreview();
  }

  function loadPreview() {
    if (!nextPreview) {
      return;
    }

    var iframeTarget = nextPreview;

    var preview = document.getElementById("preview");
    pifr.style.display = "block";
    var open = document.getElementById("preview-open");
    open.style.display = "block";
    open.onclick = function() {
      window.top.location = iframeTarget;
    };

    // amount of padding needed to put the preview at mouse location
    var newPreviewY = nextPreviewPageY
        - document.getElementById("top-posts").getBoundingClientRect().height
        - 38;

    var approxPreviewHeight = window.innerHeight/2 + 100;

    if (nextPreviewClientY > window.innerHeight - approxPreviewHeight) {
      newPreviewY -= (nextPreviewClientY - (
          window.innerHeight - approxPreviewHeight));
    }

    if (newPreviewY < 0) {
      newPreviewY = 0;
    }

    if (currentPreviewY && Math.abs(newPreviewY - currentPreviewY) < 30) {
      newPreviewY = currentPreviewY;
    }
    preview.style.marginTop = newPreviewY + "px";

    pifr.addEventListener("load", () => {
      pifr.contentWindow.addEventListener("click", function() {
        window.top.location = iframeTarget;
      });
      loadPreview();
    });

    // https://stackoverflow.com/questions/5259154/firefox-back-button-vs-iframes
    pifr.contentWindow.location.replace(iframeTarget);

    currentPreview = nextPreview;
    nextPreview = null;
    currentPreviewY = newPreviewY;
    nextPreviewPageY = null;
    nextPreviewClientY = null;
  }
});
