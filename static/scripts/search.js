document.addEventListener("DOMContentLoaded", () => {
  const map = L.map("map").setView([56.2639, 9.5018], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png").addTo(map);

  let markers = [];
  const items = window.initialItems || [];
  let currentItems = [...items];
  let currentIndex = 0;

  const resultsEl = document.getElementById("results");
  const detailsEl = document.getElementById("item-details");
  const loadMoreBtn = document.getElementById("load-more");

  function renderItems(start = 0, count = 2) {
    const slice = currentItems.slice(start, start + count);
    slice.forEach(item => {
      const card = document.createElement("div");
      card.className = "result-card";
      card.setAttribute("data-id", item.item_pk);
      card.innerHTML = `
        <img src="/static/uploads/${item.item_image}" alt="">
        <h3>${item.item_name}</h3>
        <p>${item.item_description}</p>
        <p><strong>${item.item_price} DKK (${item.item_price_eur} EUR)</strong></p>
      `;
      card.addEventListener("click", () => selectItem(item.item_pk));
      resultsEl.appendChild(card);
    });
    currentIndex += count;
    if (currentIndex >= currentItems.length) {
      loadMoreBtn.style.display = "none";
    }
  }

  function renderMarkers(data) {
    markers.forEach(m => map.removeLayer(m));
    markers = [];
    data.forEach(item => {
      const marker = L.marker([parseFloat(item.item_lat), parseFloat(item.item_lon)], {
        itemId: item.item_pk
      }).addTo(map);
      marker.bindPopup(`<strong>${item.item_name}</strong><br>${item.item_address}`);
      marker.on("click", () => selectItem(item.item_pk));
      markers.push(marker);
    });
  }

  function showDetails(item) {
    detailsEl.innerHTML = `
      <div class="detail-view">
        <img src="/static/uploads/${item.item_image}" style="width:100%; border-radius: 6px;">
        <h3>${item.item_name}</h3>
        <p>${item.item_description}</p>
        <p><strong>${item.item_price} DKK (${item.item_price_eur} EUR)</strong></p>
        <p>${item.item_address}</p>
        <p>${item.item_opening_hours || ""}</p>
      </div>
    `;
  }

  function selectItem(id) {
    const item = currentItems.find(i => i.item_pk == id);
    if (!item) return;

    showDetails(item);

    const lat = parseFloat(item.item_lat);
    const lon = parseFloat(item.item_lon);
    map.setView([lat, lon], 13);

    const marker = markers.find(m => m.options.itemId == item.item_pk);
    if (marker) marker.openPopup();

    // highlight valgt kort
    document.querySelectorAll(".result-card").forEach(card =>
      card.classList.remove("active"));
    const activeCard = document.querySelector(`.result-card[data-id="${item.item_pk}"]`);
    if (activeCard) {
      activeCard.classList.add("active");
      activeCard.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  const searchInput = document.getElementById("search-query");
  let searchTimeout = null;

  searchInput.addEventListener("input", function () {
    clearTimeout(searchTimeout);
    const query = this.value.trim().toLowerCase();
    if (!query) {
      resetSearch();
      return;
    }

    searchTimeout = setTimeout(async () => {
      const lang = document.documentElement.lang || "da";
      const res = await fetch(`/api/items/search?lang=${lang}&q=${encodeURIComponent(query)}`);
      const data = await res.json();
      currentItems = data;
      currentIndex = 0;
      resultsEl.innerHTML = "";
      loadMoreBtn.style.display = data.length > 2 ? "block" : "none";
      renderItems(0, 2);
      renderMarkers(data);
    }, 300);
  });

  loadMoreBtn.addEventListener("click", () => {
    const oldHeight = resultsEl.offsetHeight;
    renderItems(currentIndex, 2);
    const newHeight = resultsEl.offsetHeight;
    if (newHeight > oldHeight) {
      setTimeout(() => {
        resultsEl.scrollTo({
          top: resultsEl.scrollHeight,
          behavior: "smooth"
        });
      }, 100);
    }
  });

  function resetSearch() {
    currentItems = [...items];
    currentIndex = 0;
    resultsEl.innerHTML = "";
    loadMoreBtn.style.display = currentItems.length > 2 ? "block" : "none";
    renderItems(0, 2);
    renderMarkers(currentItems);
  }

  resetSearch();
});
