/* Page interactions. Data and pure helpers load before this deferred script. */
(() => {
  'use strict';

  const { papers, categories } = window.MACatalogueData;
  const { validateCatalogue, specificationFields, filterPapers, paginate, paginationPages, enquiryText, productWhatsAppText, watermarkImages } = window.MACatalogueUtils;
  // SVG keeps action arrows consistent across iOS and desktop font rendering.
  const ACTION_ARROW = "<svg class=\"action-arrow\" viewBox=\"0 0 24 24\" fill=\"none\" aria-hidden=\"true\" focusable=\"false\"><path d=\"M6 18 18 6M6 6h12v12\" /></svg>";
  const WHATSAPP_ICON = "<svg class=\"whatsapp-icon\" width=\"24\" height=\"24\" viewBox=\"0 0 24 24\" fill=\"currentColor\" aria-hidden=\"true\">\n        <path d=\"M20.52 3.48A11.86 11.86 0 0 0 12.05 0C5.47 0 .12 5.35 .12 11.93c0 2.1.55 4.15 1.6 5.96L0 24l6.26-1.64a11.9 11.9 0 0 0 5.79 1.48h.01C18.63 23.84 24 18.49 24 11.92a11.85 11.85 0 0 0-3.48-8.44ZM12.06 21.8a9.87 9.87 0 0 1-5.04-1.38l-.36-.21-3.72.98.99-3.63-.24-.38a9.85 9.85 0 0 1-1.51-5.25c0-5.45 4.44-9.88 9.9-9.88a9.8 9.8 0 0 1 7 2.9 9.8 9.8 0 0 1 2.89 6.99c0 5.45-4.44 9.86-9.91 9.86Zm5.42-7.39c-.3-.15-1.76-.87-2.04-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.17-.17.2-.35.22-.65.07-.3-.15-1.26-.46-2.4-1.48-.89-.79-1.48-1.77-1.66-2.07-.17-.3-.02-.46.13-.61l.44-.52c.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.21-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.8.37-.27.3-1.04 1.02-1.04 2.49s1.07 2.89 1.22 3.09c.15.2 2.1 3.2 5.09 4.49.71.3 1.27.49 1.7.63.72.23 1.37.2 1.89.12.58-.09 1.76-.72 2.01-1.42.25-.7.25-1.29.17-1.42-.07-.12-.27-.2-.57-.35Z\"/>\n      </svg>";
  const PAGE_SIZE = 6;
  const PRODUCT_ALIASES = Object.freeze({ 'reusable-cups': 'ribbed-travel-tumbler', 'recycled-hangers': 'sugarcane-hangers', 'grippy-cutting-board': 'cutting-boards', 'solid-cutting-boards': 'cutting-boards', 'sugarcane-a3-paper': 'sugarcane-copy-paper' });
  const CONTACT = Object.freeze({ phone: '919819157417', email: 'info@maindustries.in' });
  const byId = id => document.getElementById(id);
  const dom = {
    grid: byId('products'), pagination: byId('pagination'), count: byId('results-count'),
    categorySelect: byId('category-select'), categoryHeading: byId('active-category'), categoryDescription: byId('category-description'), search: byId('search'), sort: byId('sort'), reset: byId('reset-catalogue'),
    form: byId('brief'), paper: byId('paper'), options: byId('paper-options'),
    status: byId('status'), detail: byId('detail'), detailBody: byId('detail-body'),
    filters: [...document.querySelectorAll('[data-filter]')]
  };
  const requestedCategory = new URLSearchParams(location.search).get('category');
  const state = { category: categories.some(item => item.id === requestedCategory) ? requestedCategory : 'all', page: 1 };
  const paperById = new Map(papers.map(paper => [paper.id, paper]));
  const categoryById = new Map(categories.map(category => [category.id, category]));

  validateCatalogue(papers, categories);

  // Only repository-owned text enters HTML templates. Visitor input uses FormData.
  const escapeHtml = value => String(value).replace(/[&<>"']/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[character]));

  function syncFilterButtons() {
    if (dom.categorySelect) dom.categorySelect.value = state.category;
    if (dom.categoryHeading) dom.categoryHeading.textContent = state.category === 'all' ? 'All products' : categoryById.get(state.category).name;
    // Keep category guidance in the browsing flow rather than a separate page.
    if (dom.categoryDescription) dom.categoryDescription.textContent = state.category === 'all'
      ? 'Search by name or start with what you need to do. The catalogue covers food service, storage, paper and M&A cleaning products.'
      : categoryById.get(state.category).desc;
    for (const button of dom.filters) {
      const active = button.dataset.filter === state.category;
      button.classList.toggle('active', active);
      button.setAttribute('aria-pressed', String(active));
      const sidebar = button.closest('.catalogue-sidebar');
      if (active && sidebar) sidebar.scrollTop = Math.max(0, button.offsetTop - sidebar.clientHeight / 2);

    }
  }

  function setCategory(category) {
    state.category = categoryById.has(category) ? category : 'all';
    state.page = 1;
    syncFilterButtons();
    renderCatalogue();
  }

  function resetCatalogue() {
    dom.search.value = '';
    dom.sort.value = 'collection';
    setCategory('all');
  }

  function productWhatsAppUrl(paper) {
    return 'https://wa.me/' + CONTACT.phone + '?text=' + encodeURIComponent(productWhatsAppText(paper, categoryById.get(paper.group).name));
  }

  function productCard(paper) {
    const name = escapeHtml(paper.name);
    const category = categoryById.get(paper.group);
    const label = category.collection === 'clean-republic' ? 'M&A Cleaning & Hygiene' : category.name;
    const availability = paper.sourcingOnly ? ' &middot; Pre-order' : '';
    const imageAlt = escapeHtml(paper.imageAlt || paper.name);
    return watermarkImages(`<article class="product" data-paper-id="${paper.id}" data-collection="${category.collection}">
      <div class="product-visual" style="--paper:${paper.color};--bg:${paper.bg}">
        <img class="product-photo" src="${escapeHtml(paper.cardImage || paper.image)}" alt="${imageAlt}" width="800" height="800" loading="lazy" decoding="async">
      </div>
      <div class="product-copy">
        <p class="product-category">${escapeHtml(label)}${availability}</p>
        <h3><a class="product-detail-link" href="#paper-${paper.id}">${name}</a></h3>
        <p class="product-card-overview">${escapeHtml(paper.desc)}</p>
        <span class="product-card-cta" aria-hidden="true">View details ${ACTION_ARROW}</span>
      </div>
    </article>`);
  }

  function pageButton(label, page, disabled = false) {
    const button = document.createElement('button');
    button.type = 'button';
    button.textContent = label;
    button.dataset.page = page;
    button.disabled = disabled;
    const isNumber = /^\d+$/.test(label);
    button.setAttribute('aria-label', isNumber ? 'Go to page ' + page : label + ' page');
    if (isNumber && page === state.page) {
      button.setAttribute('aria-current', 'page');
      button.setAttribute('aria-label', 'Page ' + page + ', current page');
    }
    return button;
  }

  function renderPagination(totalPages) {
    dom.pagination.replaceChildren();
    dom.pagination.hidden = totalPages < 2;
    if (totalPages < 2) return;
    const fragment = document.createDocumentFragment();
    if (state.page > 1) fragment.append(pageButton('Previous', state.page - 1));
    for (const page of paginationPages(totalPages, state.page)) {
      if (page === '…') {
        const gap = document.createElement('span');
        gap.className = 'pagination-gap';
        gap.textContent = '…';
        gap.setAttribute('aria-hidden', 'true');
        fragment.append(gap);
      } else fragment.append(pageButton(String(page), page));
    }
    fragment.append(pageButton('Next →', state.page + 1, state.page === totalPages));
    dom.pagination.append(fragment);
  }

  function renderCatalogue() {
    const matches = filterPapers(papers, {
      category: state.category, query: dom.search.value, sort: dom.sort.value
    });
    const page = paginate(matches, state.page, PAGE_SIZE);
    state.page = page.currentPage;
    // One DOM update per render; grid-level listeners survive filtering/paging.
    dom.grid.innerHTML = page.total ? page.items.map(productCard).join('') :
      '<div class="empty-state"><h3>No matching products</h3><p>Try a product name like paper cups, or search for a use like floor care.</p>' +
      '<button class="button" type="button" data-reset-search>Reset search ' + ACTION_ARROW + '</button></div>';
    dom.grid.scrollLeft = 0;
    renderPagination(page.totalPages);
    dom.count.textContent = page.total ?
      `Showing ${page.offset + 1}–${page.offset + page.items.length} of ${page.total} ${page.total === 1 ? 'product' : 'products'} · Page ${state.page} of ${page.totalPages}` :
      'No products found';
  }

  let savedPageScroll = null;

  function lockPageScroll() {
    if (savedPageScroll) return;
    // Fixed positioning prevents background touch scrolling on iOS Safari too.
    savedPageScroll = { x: window.scrollX || 0, y: window.scrollY, top: document.body.style.top };
    document.body.style.top = '-' + savedPageScroll.y + 'px';
    document.documentElement.classList.add('product-modal-open');
    document.body.classList.add('product-modal-open');
  }

  function unlockPageScroll() {
    if (!savedPageScroll) return;
    const saved = savedPageScroll;
    savedPageScroll = null;
    document.body.classList.remove('product-modal-open');
    document.body.style.top = saved.top;
    // Restore before removing the root class so global smooth scrolling cannot animate it.
    window.scrollTo({ left: saved.x, top: saved.y, behavior: 'instant' });
    document.documentElement.classList.remove('product-modal-open');
  }

  function closeProductDialog() {
    dom.detail.close();
    unlockPageScroll();
  }

  function productSpecificationMarkup(product, fields) {
    if (!product.variants?.length) return '<dl class="product-specifications">' + fields.map(item => '<div><dt>' + escapeHtml(item.label) + '</dt><dd>' + escapeHtml(item.value) + '</dd></div>').join('') + '</dl>';
    const dimensions = variant => [variant.thickness && 'Thickness: ' + variant.thickness,
      variant.dimensions, variant.capacity && 'Capacity: ' + variant.capacity, variant.notes].filter(Boolean).join('; ');
    return '<div class="variant-table-wrap" tabindex="0" role="region" aria-label="Product variants and specifications"><table class="variant-table"><caption>Available variants</caption><thead><tr><th scope="col">Variant</th><th scope="col">Dimensions / format</th><th scope="col">Pack / unit</th></tr></thead><tbody>' +
      product.variants.map(variant => '<tr><th scope="row">' + escapeHtml(variant.name) + '</th><td>' + escapeHtml(dimensions(variant) || 'Confirm on enquiry') + '</td><td>' + escapeHtml(variant.pack) + '</td></tr>').join('') + '</tbody></table></div>' +
      (product.technicalNotes ? '<p class="variant-note">' + escapeHtml(product.technicalNotes) + '</p>' : '');
  }

  function openProduct(id) {
    const paper = paperById.get(PRODUCT_ALIASES[id] || id);
    if (!paper) return;
    const category = categoryById.get(paper.group);
    const cleanRepublic = category.collection === 'clean-republic';
    const overview = paper.overview || paper.desc;
    const leadEnd = overview.indexOf('. ') + 1;
    const overviewMarkup = leadEnd
      ? '<strong>' + escapeHtml(overview.slice(0, leadEnd)) + '</strong>' + escapeHtml(overview.slice(leadEnd))
      : escapeHtml(overview);
    const specifications = specificationFields(paper).filter(item =>
      item.label.toLowerCase() !== 'material' &&
      !(paper.specifications?.length && /^Confirm /i.test(item.value)));
    dom.detailBody.innerHTML = watermarkImages(`
      <div class="product-modal-content">
      <div class="product-modal-heading"><span class="dialog-tag">${cleanRepublic ? 'M&A Cleaning &amp; Hygiene &middot; ' : ''}${escapeHtml(category.name)}</span>
        <h2 id="detail-title">${escapeHtml(paper.name)}</h2></div>
      <figure class="detail-photo product-modal-visual"><img src="${escapeHtml(paper.image)}" alt="${escapeHtml(paper.imageAlt || paper.name)}" width="800" height="800" decoding="async"></figure>
      <div class="product-modal-copy">
        <p class="product-modal-overview">${overviewMarkup}</p>
        <section class="product-modal-section"><h3>Material</h3><p>${escapeHtml(paper.material || 'Paper / board; confirm the selected grade and composition on enquiry.')}</p></section>
        <section class="product-modal-section"><h3>Uses &amp; applications</h3><ul class="detail-uses">${paper.uses.map(use => '<li>' + escapeHtml(use) + '</li>').join('')}</ul></section>
        <section class="product-modal-section"><h3>Specifications</h3>${productSpecificationMarkup(paper, specifications)}</section>
        <p class="detail-note">${paper.sourcingOnly ? 'Available by pre-order enquiry. Ask us about pack options and lead time.' : 'Ask us to confirm the format, pack options and current availability.'}</p>
      </div></div>
      <div class="product-enquiry-actions product-modal-actions"><button class="button" type="button" data-choose-paper="${paper.id}" aria-label="Enquire about this product"><span class="action-copy enquiry-full-label">Enquire about this product</span><span class="action-copy enquiry-short-label">Enquire</span></button><a class="button whatsapp-button" href="${escapeHtml(productWhatsAppUrl(paper))}" target="_blank" rel="noopener noreferrer" aria-label="WhatsApp connect">${WHATSAPP_ICON}<span class="action-copy">WhatsApp<span class="connect-word"> connect</span></span></a></div>`);
    if (!dom.detail.open) {
      lockPageScroll();
      dom.detail.showModal();
      window.MAExperience?.enterDialog(dom.detail);
    }
  }

  function handleProductHash() {
    if (location.hash === '#paper-recycled-cleaning-tools') {
      if (dom.grid) setCategory('recycled-household');
      return;
    }
    if (location.hash.startsWith('#paper-')) openProduct(location.hash.slice(7));
    else if (dom.detail.open) closeProductDialog();
  }

  function closeProduct() {
    closeProductDialog();
    // Update the URL without jumping back to the start of the collection.
    window.history.replaceState(null, '', '#collection');
  }

  function initializeCatalogue() {
    if (dom.categorySelect) {
      const options = document.createDocumentFragment();
      options.append(new Option('All products (' + papers.length + ')', 'all'));
      const categoryOrder = [...categories.filter(category => category.collection === 'clean-republic'),
        ...categories.filter(category => category.collection !== 'clean-republic')];
      for (const category of categoryOrder) {
        const count = papers.filter(paper => paper.group === category.id).length;
        options.append(new Option(category.name + ' (' + count + ')', category.id));
      }
      dom.categorySelect.replaceChildren(options);
      dom.categorySelect.value = state.category;
    }
    for (const button of dom.filters) button.addEventListener('click', () => setCategory(button.dataset.filter));
    dom.categorySelect?.addEventListener('change', () => setCategory(dom.categorySelect.value));
    for (const input of [dom.search, dom.sort]) {
      input.addEventListener(input === dom.search ? 'input' : 'change', () => {
        state.page = 1;
        renderCatalogue();
      });
    }
    dom.reset.addEventListener('click', () => {
      resetCatalogue();
      dom.search.focus({ preventScroll: true });
    });
    dom.pagination.addEventListener('click', event => {
      const button = event.target.closest('button[data-page]');
      if (!button || button.disabled) return;
      state.page = Number(button.dataset.page);
      renderCatalogue();
      dom.count.scrollIntoView({ block: 'start' });
      dom.pagination.querySelector('[aria-current]')?.focus({ preventScroll: true });
    });
    dom.grid.addEventListener('click', event => {
      if (event.target.closest('[data-reset-search]')) { resetCatalogue(); return; }
      const link = event.target.closest('.product-detail-link');
      if (link && location.hash === link.getAttribute('href')) {
        openProduct(link.closest('[data-paper-id]').dataset.paperId);
      }
    });
    document.querySelectorAll('[data-category-link]').forEach(link => link.addEventListener('click', () => {
      dom.search.value = '';
      setCategory(link.dataset.categoryLink);
      byId('collection').scrollIntoView();
    }));
    syncFilterButtons();
    renderCatalogue();
  }

  function initializeProductDetails() {
    document.querySelector('.close').addEventListener('click', closeProduct);
    dom.detail.addEventListener('cancel', event => {
      event.preventDefault();
      closeProduct();
    });
    dom.detail.addEventListener('close', () => {
      if (!dom.detail.open) unlockPageScroll();
    });
    dom.detail.addEventListener('click', event => {
      const choice = event.target.closest('[data-choose-paper]');
      if (choice) {
        dom.paper.value = paperById.get(choice.dataset.choosePaper).name;
        closeProductDialog();
        location.hash = 'enquiry';
        byId('enquiry').scrollIntoView();
        dom.paper.focus({ preventScroll: true });
        return;
      }
      // Backdrop clicks hit the dialog itself; padding clicks should not close it.
      if (event.target !== dom.detail) return;
      const bounds = dom.detail.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right ||
          event.clientY < bounds.top || event.clientY > bounds.bottom) closeProduct();
    });
    window.addEventListener('hashchange', handleProductHash);
    handleProductHash();
  }

  function initializeEnquiry() {
    const options = document.createDocumentFragment();
    options.append(new Option('Not sure? Help me choose', 'Help me choose'));
    for (const paper of papers) options.append(new Option(paper.name, paper.name));
    dom.options.replaceChildren(options);
    const choice = paperById.get(new URLSearchParams(location.search).get('paper'));
    if (choice) dom.paper.value = choice.name;
    dom.form.addEventListener('submit', event => {
      event.preventDefault();
      const text = enquiryText(new FormData(dom.form));
      const channel = event.submitter?.value || 'whatsapp';
      if (channel === 'email') {
        location.href = 'mailto:' + CONTACT.email + '?subject=' +
          encodeURIComponent(dom.paper.value ? 'Product enquiry — ' + dom.paper.value : 'Contact enquiry | M&A Industries') + '&body=' + encodeURIComponent(text);
        dom.status.textContent = 'Your email app has been requested. Review the prepared enquiry and send it to ' + CONTACT.email + '.';
      } else {
        const link = document.createElement('a');
        link.href = 'https://wa.me/' + CONTACT.phone + '?text=' + encodeURIComponent(text);
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.click();
        dom.status.textContent = 'WhatsApp has been requested. Review the prepared enquiry and send it to +91 98191 57417.';
      }
      window.MAExperience?.confirmEnquiry(dom.status);
    });
  }

  // Counts come from the catalogue, avoiding drift when product data is edited.
  function initializeCounts() {
    const counts = new Map(categories.map(category => [category.id, papers.filter(paper => paper.group === category.id).length]));
    for (const button of dom.filters) {
      const badge = button.querySelector('small');
      if (badge) badge.textContent = button.dataset.filter === 'all' ? papers.length : counts.get(button.dataset.filter);
    }
    document.querySelectorAll('.category-card[data-category-link]').forEach((card, index) => {
      card.querySelector('.eyebrow').textContent = String(index + 1).padStart(2, '0') + ' / ' + counts.get(card.dataset.categoryLink) + ' PRODUCTS';
    });
  }


  initializeCounts();
  initializeEnquiry();
  if (dom.grid) {
    initializeCatalogue();
    initializeProductDetails();
  } else if (location.hash.startsWith('#paper-') || location.hash === '#collection' || requestedCategory) {
    location.replace('products.html' + location.search + location.hash);
  }
})();
