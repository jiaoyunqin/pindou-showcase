/* Progressive enhancement only: all content, anchors and disclosure work
   without JavaScript. Image links fall back to their public crop files. */
(() => {
  "use strict";

  const dialog = document.querySelector(".lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;

  const title = dialog.querySelector("#lightbox-title");
  const caption = dialog.querySelector("#lightbox-caption");
  const image = dialog.querySelector(".lightbox-image");
  const scroller = dialog.querySelector(".lightbox-scroller");
  const sourceLink = dialog.querySelector(".source-link");
  const zoomButton = dialog.querySelector(".zoom-button");
  const closeButton = dialog.querySelector(".close-button");
  const errorMessage = dialog.querySelector(".lightbox-error");
  let trigger = null;

  function setZoom(enabled) {
    scroller.classList.toggle("is-zoomed", enabled);
    zoomButton.setAttribute("aria-pressed", String(enabled));
    zoomButton.textContent = enabled ? "适应窗口" : "原始尺寸";
    scroller.scrollTo({ top: 0, left: 0, behavior: "instant" });
  }

  document.querySelectorAll("a[data-lightbox]").forEach((link) => {
    link.setAttribute("aria-haspopup", "dialog");
    link.addEventListener("click", (event) => {
      // Keep standard new-tab/download gestures available.
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      trigger = link;
      title.textContent = link.dataset.title;
      caption.textContent = link.dataset.caption;
      image.alt = link.querySelector("img").alt;
      errorMessage.hidden = true;
      image.hidden = false;
      image.src = link.href;
      sourceLink.href = link.dataset.source;
      sourceLink.textContent = `${link.dataset.sourceLabel || "查看完整截图"} ↗`;
      setZoom(false);
      dialog.showModal();
      document.body.classList.add("has-lightbox");
      closeButton.focus({ preventScroll: true });
    });
  });

  image.addEventListener("error", () => {
    errorMessage.hidden = false;
    image.hidden = true;
  });

  zoomButton.addEventListener("click", () => {
    setZoom(zoomButton.getAttribute("aria-pressed") !== "true");
  });

  closeButton.addEventListener("click", () => dialog.close());

  // Keep Tab within the reader controls, including in browsers that otherwise
  // visit the browser toolbar between the last and first dialog controls.
  dialog.addEventListener("keydown", (event) => {
    if (event.key !== "Tab") return;
    if (event.shiftKey && document.activeElement === closeButton) {
      event.preventDefault();
      sourceLink.focus();
    } else if (!event.shiftKey && document.activeElement === sourceLink) {
      event.preventDefault();
      closeButton.focus();
    }
  });

  // Close only when the backdrop itself was pressed and released.
  let pressedBackdrop = false;
  const outsideDialog = (event) => {
    const box = dialog.getBoundingClientRect();
    return event.clientX < box.left || event.clientX > box.right ||
      event.clientY < box.top || event.clientY > box.bottom;
  };
  dialog.addEventListener("pointerdown", (event) => {
    pressedBackdrop = event.target === dialog && outsideDialog(event);
  });
  dialog.addEventListener("click", (event) => {
    if (pressedBackdrop && event.target === dialog && outsideDialog(event)) dialog.close();
    pressedBackdrop = false;
  });

  // Escape is handled by the native dialog; close also restores the page.
  dialog.addEventListener("close", () => {
    document.body.classList.remove("has-lightbox");
    setZoom(false);
    if (trigger && trigger.isConnected) trigger.focus({ preventScroll: true });
  });
})();
