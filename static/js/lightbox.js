/* =============================================================
   lightbox.js — tiny, dependency-free image lightbox.
   -------------------------------------------------------------
   Collects every <a class="lightbox"> in the article (i.e. every
   image in the post) into one navigable set. Uses a native
   <dialog>, so Esc-to-close, focus-trapping and inertness of the
   page behind come for free. Prev/next via buttons, arrow keys,
   or click-on-backdrop to dismiss. Styled entirely by blog.css.
   ============================================================= */
(function () {
  "use strict";

  function init() {
    var links = Array.prototype.slice.call(
      document.querySelectorAll("a.lightbox")
    );
    if (!links.length) return;

    var dialog = document.createElement("dialog");
    dialog.className = "lightbox-modal";
    dialog.setAttribute("data-single", links.length === 1 ? "true" : "false");
    dialog.innerHTML =
      '<div class="lb-stage">' +
      '<button class="lb-close" type="button" aria-label="Close">✕</button>' +
      '<button class="lb-prev" type="button" aria-label="Previous image">←</button>' +
      '<img class="lb-img" alt="" />' +
      '<button class="lb-next" type="button" aria-label="Next image">→</button>' +
      '<div class="lb-caption"><span class="lb-text"></span> <span class="lb-count"></span></div>' +
      "</div>";
    document.body.appendChild(dialog);

    var img = dialog.querySelector(".lb-img");
    var textEl = dialog.querySelector(".lb-text");
    var countEl = dialog.querySelector(".lb-count");
    var current = 0;

    function show(i) {
      current = (i + links.length) % links.length;
      var a = links[current];
      img.src = a.getAttribute("href");
      var caption = a.getAttribute("data-caption") || "";
      textEl.textContent = caption;
      countEl.textContent =
        links.length > 1 ? current + 1 + " / " + links.length : "";
    }

    function open(i) {
      show(i);
      if (!dialog.open) dialog.showModal();
    }

    links.forEach(function (a, i) {
      a.addEventListener("click", function (e) {
        e.preventDefault();
        open(i);
      });
    });

    dialog.querySelector(".lb-next").addEventListener("click", function () {
      show(current + 1);
    });
    dialog.querySelector(".lb-prev").addEventListener("click", function () {
      show(current - 1);
    });
    dialog.querySelector(".lb-close").addEventListener("click", function () {
      dialog.close();
    });

    dialog.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") { e.preventDefault(); show(current + 1); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); show(current - 1); }
    });

    // Click on the backdrop / empty stage (but not the image or a button) closes.
    dialog.addEventListener("click", function (e) {
      if (e.target === dialog || e.target.classList.contains("lb-stage")) {
        dialog.close();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
