const gallery = document.querySelector("#figure-gallery");
const figureCount = document.querySelector(".figure-count");

function createFigureCard(figure) {
  const article = document.createElement("article");
  article.className = "gallery-card";
  article.dataset.category = figure.category;

  const button = document.createElement("button");
  button.className = "image-button";
  button.dataset.full = figure.path;
  button.dataset.title = figure.title;

  const image = document.createElement("img");
  image.src = figure.path;
  image.alt = figure.title;
  image.loading = "lazy";
  button.append(image);

  const meta = document.createElement("span");
  meta.className = `figure-meta figure-meta-${figure.category}`;
  meta.textContent = figure.group;

  const title = document.createElement("h3");
  title.textContent = figure.title;

  const description = document.createElement("p");
  description.textContent = figure.description;

  article.append(button, meta, title, description);
  return article;
}

const figures = typeof FIGURES !== "undefined" && Array.isArray(FIGURES) ? FIGURES : [];

if (gallery && figures.length > 0) {
  figures.forEach((figure) => gallery.append(createFigureCard(figure)));
  if (figureCount) {
    const counts = figures.reduce((acc, figure) => {
      acc[figure.category] = (acc[figure.category] || 0) + 1;
      return acc;
    }, {});
    figureCount.textContent = `총 ${figures.length}개 figure · 통합 ${counts.integrated || 0} · 주거 ${counts.residential || 0} · 노동 ${counts.employment || 0} · 교통 ${counts.transport || 0} · 복제본 ${counts.archive || 0}`;
  }
}

const filterButtons = document.querySelectorAll(".filter-button");

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    const galleryCards = document.querySelectorAll(".gallery-card");

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

document.addEventListener("click", (event) => {
  const button = event.target.closest(".image-button");
  if (!button) return;

  if (!button.dataset.full) return;
  if (!dialog || !dialogImage || !dialogTitle) return;

  dialogImage.src = button.dataset.full;
  dialogImage.alt = button.dataset.title || "확대 이미지";
  dialogTitle.textContent = button.dataset.title || "";
  dialog.showModal();
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
