(() => {
  "use strict";

  const catalog = window.MODBUS_MAP_CATALOG;
  const grid = document.querySelector("#mapGrid");
  const searchInput = document.querySelector("#searchInput");
  const manufacturerFilter = document.querySelector("#manufacturerFilter");
  const typeFilter = document.querySelector("#typeFilter");
  const resultCount = document.querySelector("#resultCount");
  const emptyState = document.querySelector("#emptyState");

  if (!catalog || !Array.isArray(catalog.maps)) {
    resultCount.textContent = "The catalog could not be loaded.";
    return;
  }

  const maps = catalog.maps;
  const normalize = (value) => String(value || "").toLocaleLowerCase();
  const options = (values) => [...new Set(values)].sort((a, b) => a.localeCompare(b));

  const addOptions = (select, values) => {
    options(values).forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.append(option);
    });
  };

  addOptions(manufacturerFilter, maps.map((item) => item.manufacturer));
  addOptions(typeFilter, maps.map((item) => item.device_type));
  document.querySelector("#mapMetric").textContent = String(catalog.map_count);
  document.querySelector("#manufacturerMetric").textContent = String(options(maps.map((item) => item.manufacturer)).length);

  const createLink = (label, href, className) => {
    const link = document.createElement("a");
    link.textContent = label;
    link.href = href;
    link.className = className;
    return link;
  };

  const createCard = (item) => {
    const card = document.createElement("article");
    card.className = "map-card";

    const top = document.createElement("div");
    top.className = "card-top";
    const manufacturer = document.createElement("span");
    manufacturer.textContent = item.manufacturer;
    const count = document.createElement("span");
    count.textContent = `${item.register_count} signals`;
    if (item.featured) {
      count.textContent = `◆ popular · ${item.register_count}`;
      count.className = "featured-tag";
    }
    top.append(manufacturer, count);

    const title = document.createElement("h3");
    title.textContent = item.model;
    const description = document.createElement("p");
    description.textContent = item.description;

    const categories = document.createElement("div");
    categories.className = "category-list";
    (item.categories || []).slice(0, 4).forEach((value) => {
      const category = document.createElement("span");
      category.textContent = value;
      categories.append(category);
    });

    const links = document.createElement("div");
    links.className = "card-links";
    links.append(
      createLink("Open JSON", item.json_url, "json-link"),
      createLink("Device guide", item.documentation_url, "docs-link")
    );
    card.append(top, title, description, categories, links);
    return card;
  };

  const render = () => {
    const query = normalize(searchInput.value.trim());
    const manufacturer = manufacturerFilter.value;
    const deviceType = typeFilter.value;
    const filtered = maps.filter((item) => {
      const haystack = normalize([
        item.manufacturer,
        item.model,
        item.device_type,
        item.description,
        ...(item.categories || []),
      ].join(" "));
      return (!query || haystack.includes(query))
        && (!manufacturer || item.manufacturer === manufacturer)
        && (!deviceType || item.device_type === deviceType);
    });

    grid.replaceChildren(...filtered.map(createCard));
    resultCount.textContent = `${filtered.length} of ${maps.length} map previews`;
    emptyState.hidden = filtered.length !== 0;
    grid.hidden = filtered.length === 0;
  };

  [searchInput, manufacturerFilter, typeFilter].forEach((control) => control.addEventListener("input", render));
  render();
})();
