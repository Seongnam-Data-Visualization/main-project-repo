const gallery = document.querySelector("#figure-gallery");
const figureCount = document.querySelector(".figure-count");

const CATEGORY_LABELS = {
  integrated: "통합",
  residential: "주거",
  employment: "노동",
  transport: "교통",
};

const groups = typeof FIGURE_GROUPS !== "undefined" ? FIGURE_GROUPS : [];

function createGroupCard(group) {
  const article = document.createElement("article");
  article.className = "gallery-card";
  article.dataset.category = group.category;

  const preview = document.createElement("div");
  preview.className = "gallery-card-preview";

  const image = document.createElement("img");
  image.src = group.figures[0].path;
  image.alt = group.figures[0].title;
  image.loading = "lazy";
  preview.append(image);

  if (group.figures.length > 1) {
    const badge = document.createElement("span");
    badge.className = "figure-count-badge";
    badge.textContent = group.figures.length;
    preview.append(badge);
  }

  const meta = document.createElement("span");
  meta.className = `figure-meta figure-meta-${group.category}`;
  meta.textContent = CATEGORY_LABELS[group.category] || group.category;

  const title = document.createElement("h3");
  title.textContent = group.title;

  const desc = document.createElement("p");
  desc.textContent = group.description;

  article.append(preview, meta, title, desc);
  article.addEventListener("click", () => openGroupModal(group, 0));
  return article;
}

if (gallery && groups.length > 0) {
  groups.forEach((group) => gallery.append(createGroupCard(group)));

  if (figureCount) {
    const counts = groups.reduce((acc, g) => {
      acc[g.category] = (acc[g.category] || 0) + 1;
      return acc;
    }, {});
    figureCount.textContent = `${groups.length}개 그룹 · 통합 ${counts.integrated || 0} · 주거 ${counts.residential || 0} · 노동 ${counts.employment || 0} · 교통 ${counts.transport || 0}`;
  }
}

// Filter
document.querySelectorAll(".filter-button").forEach((button) => {
  button.addEventListener("click", () => {
    const filter = button.dataset.filter;
    document.querySelectorAll(".filter-button").forEach((b) =>
      b.classList.toggle("is-active", b === button)
    );
    document.querySelectorAll(".gallery-card").forEach((card) => {
      card.classList.toggle("is-hidden", filter !== "all" && card.dataset.category !== filter);
    });
  });
});

// Modal
const dialog = document.querySelector(".image-dialog");
const dialogImage = dialog?.querySelector("img");
const dialogTitle = dialog?.querySelector(".dialog-figure-title");
const dialogCounter = dialog?.querySelector(".dialog-counter");
const dialogPrev = dialog?.querySelector(".dialog-prev");
const dialogNext = dialog?.querySelector(".dialog-next");
const dialogDots = dialog?.querySelector(".dialog-dots");
const closeButton = dialog?.querySelector(".dialog-close");

let currentGroup = null;
let currentIndex = 0;

function openGroupModal(group, index) {
  currentGroup = group;
  currentIndex = index;
  renderDots();
  updateModal();
  dialog.showModal();
}

function renderDots() {
  if (!dialogDots || !currentGroup) return;
  dialogDots.innerHTML = "";
  if (currentGroup.figures.length <= 1) return;
  currentGroup.figures.forEach((_, i) => {
    const dot = document.createElement("button");
    dot.className = "dialog-dot" + (i === currentIndex ? " is-active" : "");
    dot.setAttribute("aria-label", `${i + 1}번째 그림`);
    dot.addEventListener("click", (e) => {
      e.stopPropagation();
      currentIndex = i;
      updateModal();
    });
    dialogDots.append(dot);
  });
}

function updateModal() {
  if (!currentGroup || !dialogImage || !dialogTitle) return;
  const figure = currentGroup.figures[currentIndex];
  dialogImage.src = figure.path;
  dialogImage.alt = figure.title;
  dialogTitle.textContent = figure.title;

  const total = currentGroup.figures.length;
  if (dialogCounter) {
    dialogCounter.textContent = total > 1 ? `${currentIndex + 1} / ${total}` : "";
  }
  if (dialogPrev) dialogPrev.disabled = currentIndex === 0;
  if (dialogNext) dialogNext.disabled = currentIndex === total - 1;

  dialogDots?.querySelectorAll(".dialog-dot").forEach((dot, i) =>
    dot.classList.toggle("is-active", i === currentIndex)
  );
}

dialogImage?.addEventListener("click", () => {
  if (currentGroup && currentIndex < currentGroup.figures.length - 1) {
    currentIndex++;
    updateModal();
  }
});

// Section image-buttons (residential / employment / transport sections)
document.addEventListener("click", (event) => {
  const button = event.target.closest(".image-button");
  if (!button || !button.dataset.full) return;
  openGroupModal(
    { figures: [{ path: button.dataset.full, title: button.dataset.title || "" }] },
    0
  );
});

dialogPrev?.addEventListener("click", (e) => {
  e.stopPropagation();
  if (currentIndex > 0) { currentIndex--; updateModal(); }
});

dialogNext?.addEventListener("click", (e) => {
  e.stopPropagation();
  if (currentGroup && currentIndex < currentGroup.figures.length - 1) {
    currentIndex++; updateModal();
  }
});

closeButton?.addEventListener("click", () => dialog?.close());

dialog?.addEventListener("click", (event) => {
  if (event.target === dialog) dialog.close();
});

document.addEventListener("keydown", (event) => {
  if (!dialog?.open) return;
  if (event.key === "Escape") dialog.close();
  if (event.key === "ArrowRight" && currentGroup && currentIndex < currentGroup.figures.length - 1) {
    currentIndex++; updateModal();
  }
  if (event.key === "ArrowLeft" && currentIndex > 0) {
    currentIndex--; updateModal();
  }
});
