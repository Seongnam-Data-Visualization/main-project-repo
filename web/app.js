const filterButtons = document.querySelectorAll(".filter-button");
const galleryCards = document.querySelectorAll(".gallery-card");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;

    filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));
    galleryCards.forEach((card) => {
      const shouldShow = filter === "all" || card.dataset.category === filter;
      card.classList.toggle("is-hidden", !shouldShow);
    });
  });
});

const dialog = document.querySelector(".image-dialog");
const dialogImage = dialog?.querySelector("img");
const dialogTitle = dialog?.querySelector("h2");
const closeButton = dialog?.querySelector(".dialog-close");

document.querySelectorAll(".image-button").forEach((button) => {
  button.addEventListener("click", () => {
    if (!dialog || !dialogImage || !dialogTitle) return;

    dialogImage.src = button.dataset.full;
    dialogImage.alt = button.dataset.title || "확대 이미지";
    dialogTitle.textContent = button.dataset.title || "";
    dialog.showModal();
  });
});

closeButton?.addEventListener("click", () => dialog.close());

dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) {
    dialog.close();
  }
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && dialog?.open) {
    dialog.close();
  }
});
