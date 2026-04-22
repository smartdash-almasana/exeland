const WHATSAPP_URL = 'https://wa.me/5491100000000?text=Hola%20Exceland,%20quiero%20que%20me%20ayuden%20a%20elegir%20una%20planilla';
const TELEGRAM_URL = 'https://t.me/exceland';
const MANIFEST_URL = '/warehouse/manifest.json';

function formatPrice(price, isFree) {
  if (isFree || Number(price) === 0) return 'Gratis';
  return `${Number(price).toLocaleString('es-AR')}`;
}

function formatCategoryLabel(category) {
  const map = {
    cashflow: 'Caja y flujo',
    pricing: 'Precios',
    stock: 'Stock',
    financial: 'Finanzas'
  };
  return map[category] || 'Plantilla';
}

function categoryTheme(category, isFree) {
  if (isFree) {
    return {
      accent: 'from-emerald-500 to-teal-500',
      soft: 'bg-emerald-50 text-emerald-700 border-emerald-100',
      iconWrap: 'bg-emerald-100 text-emerald-700',
      ring: 'group-hover:border-emerald-200'
    };
  }

  const themes = {
    cashflow: {
      accent: 'from-sky-500 to-cyan-500',
      soft: 'bg-sky-50 text-sky-700 border-sky-100',
      iconWrap: 'bg-sky-100 text-sky-700',
      ring: 'group-hover:border-sky-200'
    },
    pricing: {
      accent: 'from-violet-500 to-fuchsia-500',
      soft: 'bg-violet-50 text-violet-700 border-violet-100',
      iconWrap: 'bg-violet-100 text-violet-700',
      ring: 'group-hover:border-violet-200'
    },
    stock: {
      accent: 'from-amber-500 to-orange-500',
      soft: 'bg-amber-50 text-amber-700 border-amber-100',
      iconWrap: 'bg-amber-100 text-amber-700',
      ring: 'group-hover:border-amber-200'
    },
    financial: {
      accent: 'from-teal-500 to-emerald-500',
      soft: 'bg-teal-50 text-teal-700 border-teal-100',
      iconWrap: 'bg-teal-100 text-teal-700',
      ring: 'group-hover:border-teal-200'
    }
  };

  return themes[category] || {
    accent: 'from-slate-500 to-slate-700',
    soft: 'bg-slate-100 text-slate-700 border-slate-200',
    iconWrap: 'bg-slate-100 text-slate-700',
    ring: 'group-hover:border-slate-300'
  };
}

function categoryIcon(category, isFree) {
  if (isFree) {
    return `
      <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
        <path d="M12 3l2.8 5.67L21 9.58l-4.5 4.38 1.06 6.2L12 17.27 6.44 20.16l1.06-6.2L3 9.58l6.2-.91L12 3z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>
      </svg>
    `;
  }

  const icons = {
    cashflow: `
      <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
        <path d="M4 7h16M7 4v6m10-6v6M5 11h14v8H5z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `,
    pricing: `
      <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
        <path d="M7 7h10M7 12h6m-6 5h10M5 4h14a1 1 0 011 1v14a1 1 0 01-1 1H5a1 1 0 01-1-1V5a1 1 0 011-1z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `,
    stock: `
      <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
        <path d="M4 8l8-4 8 4-8 4-8-4zm0 4l8 4 8-4m-16 4l8 4 8-4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    `,
    financial: `
      <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
        <path d="M5 19V9m7 10V5m7 14v-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
        <path d="M3 19h18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
      </svg>
    `
  };

  return icons[category] || `
    <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6">
      <path d="M5 5h14v14H5z" stroke="currentColor" stroke-width="1.8"/>
    </svg>
  `;
}

function badgeMarkup(product, theme) {
  if (product.free || Number(product.price_ars) === 0) {
    return '<span class="inline-flex rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-xs font-semibold uppercase tracking-wide border border-emerald-100">Gratis</span>';
  }
  if (Array.isArray(product.tags) && product.tags.length) {
    return `<span class="inline-flex rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-wide border ${theme.soft}">${product.tags[0]}</span>`;
  }
  return '<span class="inline-flex rounded-full bg-slate-100 text-slate-700 px-3 py-1 text-xs font-semibold uppercase tracking-wide border border-slate-200">Producto</span>';
}

function productFeatures(product) {
  const tags = Array.isArray(product.tags) ? product.tags.slice(0, 4) : [];
  if (!tags.length) {
    return ['Listo para descargar', 'Diseño claro', 'Celdas protegidas', 'Uso inmediato'];
  }
  return tags.map((tag) => String(tag).replace(/_/g, ' '));
}

function toPublicDownloadHref(outputFile) {
  if (!outputFile) return '#contacto';
  const normalized = String(outputFile).replace(/\\/g, '/');
  const filename = normalized.split('/').pop();
  if (!filename) return '#contacto';
  return `/warehouse/templates/${encodeURIComponent(filename)}`;
}

function featureMarkup(feature, theme) {
  return `
    <div class="flex items-center gap-2 rounded-2xl border ${theme.soft} px-3 py-2">
      <span class="inline-flex w-5 h-5 items-center justify-center rounded-full bg-white/80">
        <svg viewBox="0 0 20 20" fill="none" class="w-3.5 h-3.5">
          <path d="M5 10l3 3 7-7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </span>
      <span class="capitalize">${feature}</span>
    </div>
  `;
}

function productCard(product) {
  const isFree = product.free || Number(product.price_ars) === 0;
  const theme = categoryTheme(product.category, isFree);
  const price = formatPrice(product.price_ars, isFree);
  const categoryLabel = formatCategoryLabel(product.category);
  const features = productFeatures(product).map((item) => featureMarkup(item, theme)).join('');
  const downloadHref = toPublicDownloadHref(product.output_file);
  const primaryText = isFree ? 'Descargar gratis' : 'Comprar este Excel';
  const subtitle = product.subtitle || 'Herramienta lista para usar';
  const icon = categoryIcon(product.category, isFree);

  return `
    <article class="group relative overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-card transition duration-300 hover:-translate-y-1 hover:shadow-soft ${theme.ring}">
      <div class="absolute inset-x-0 top-0 h-1.5 bg-gradient-to-r ${theme.accent}"></div>

      <div class="p-8">
        <div class="flex items-start justify-between gap-4">
          <div class="min-w-0">
            <div class="flex items-center gap-3">
              <div class="inline-flex h-12 w-12 items-center justify-center rounded-2xl ${theme.iconWrap}">
                ${icon}
              </div>
              <div class="min-w-0">
                ${badgeMarkup(product, theme)}
                <p class="mt-2 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">${categoryLabel}</p>
              </div>
            </div>

            <h3 class="mt-5 text-2xl font-bold tracking-tight text-ink">${product.title}</h3>
            <p class="mt-3 max-w-xl text-slate-600">${subtitle}</p>
          </div>

          <div class="shrink-0 text-right">
            <p class="text-xs font-medium uppercase tracking-wide text-slate-400">${isFree ? 'Lead magnet' : 'Pago único'}</p>
            <p class="mt-2 text-3xl font-bold text-ink">${price}</p>
          </div>
        </div>

        <div class="mt-6 grid sm:grid-cols-2 gap-3 text-sm font-medium">
          ${features}
        </div>

        <div class="mt-7 flex items-center justify-between gap-4 rounded-2xl bg-slate-50 px-4 py-3">
          <div>
            <p class="text-sm font-semibold text-ink">${isFree ? 'Descarga inmediata' : 'Compra simple y rápida'}</p>
            <p class="text-xs text-slate-500">${isFree ? 'Bajala ahora y empezá a usarla hoy.' : 'Pago único. Sin mensualidad ni vueltas.'}</p>
          </div>
          <div class="hidden sm:flex items-center gap-2 text-slate-400">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span class="text-xs font-medium">Lista para usar</span>
          </div>
        </div>

        <div class="mt-7 flex flex-col sm:flex-row gap-3">
          <a href="${downloadHref}" class="inline-flex items-center justify-center gap-2 rounded-2xl bg-ink text-white px-5 py-3.5 font-semibold hover:bg-slate-800 transition">
            <span>${primaryText}</span>
            <svg viewBox="0 0 20 20" fill="none" class="w-4 h-4">
              <path d="M10 3v9m0 0l-3-3m3 3l3-3M4 14.5V16a1 1 0 001 1h10a1 1 0 001-1v-1.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </a>
          <a href="${WHATSAPP_URL}" class="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-300 px-5 py-3.5 font-semibold text-slate-900 hover:border-slate-400 hover:bg-slate-50 transition">
            <span>Consultar por WhatsApp</span>
          </a>
        </div>
      </div>
    </article>
  `;
}

async function loadManifestProducts() {
  const loading = document.getElementById('products-loading');
  const error = document.getElementById('products-error');
  const grid = document.getElementById('products-grid');

  try {
    const response = await fetch(MANIFEST_URL, { cache: 'no-store' });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const manifest = await response.json();
    const productsObj = manifest.products || {};
    const products = Object.values(productsObj);

    if (!products.length) throw new Error('Manifest sin productos');

    products.sort((a, b) => {
      if ((a.free ? 1 : 0) !== (b.free ? 1 : 0)) return (a.free ? 1 : 0) - (b.free ? 1 : 0);
      return Number(a.price_ars || 0) - Number(b.price_ars || 0);
    });

    grid.innerHTML = products.map(productCard).join('');
    loading.classList.add('hidden');
  } catch (err) {
    console.error('Manifest load error:', err);
    loading.classList.add('hidden');
    error.classList.remove('hidden');
  }
}

loadManifestProducts();