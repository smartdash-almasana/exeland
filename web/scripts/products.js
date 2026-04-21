const WHATSAPP_URL = 'https://wa.me/5491100000000?text=Hola%20Exceland,%20quiero%20que%20me%20ayuden%20a%20elegir%20una%20planilla';
const TELEGRAM_URL = 'https://t.me/exceland';

// Ruta al manifest: funciona en local (/web/ → ../warehouse/) y en producción (raíz → /warehouse/)
// /warehouse/ está siempre al mismo nivel que index.html (tanto en local como en producción)
const MANIFEST_URL = '/warehouse/manifest.json';

function formatPrice(price, isFree) {
  if (isFree || Number(price) === 0) return 'Gratis';
  return `${Number(price).toLocaleString('es-AR')}`;
}

function badgeMarkup(product) {
  if (product.free || Number(product.price_ars) === 0) {
    return '<span class="inline-flex rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-xs font-semibold uppercase tracking-wide">Gratis</span>';
  }
  if (Array.isArray(product.tags) && product.tags.length) {
    return `<span class="inline-flex rounded-full bg-teal-50 text-brand px-3 py-1 text-xs font-semibold uppercase tracking-wide">${product.tags[0]}</span>`;
  }
  return '<span class="inline-flex rounded-full bg-slate-100 text-slate-700 px-3 py-1 text-xs font-semibold uppercase tracking-wide">Producto</span>';
}

function productFeatures(product) {
  const tags = Array.isArray(product.tags) ? product.tags.slice(0, 4) : [];
  if (!tags.length) {
    return [
      'Listo para descargar',
      'Diseño claro',
      'Celdas protegidas',
      'Uso inmediato'
    ];
  }
  return tags;
}

function toPublicDownloadHref(outputFile) {
  if (!outputFile) return '#contacto';
  const normalized = String(outputFile).replace(/\\/g, '/');
  const filename = normalized.split('/').pop();
  if (!filename) return '#contacto';
  return `/warehouse/templates/${encodeURIComponent(filename)}`;
}

function productCard(product) {
  const price = formatPrice(product.price_ars, product.free);
  const features = productFeatures(product)
    .map(item => `<div class="rounded-2xl bg-slate-50 p-4">✔ ${item}</div>`)
    .join('');

  const downloadHref = toPublicDownloadHref(product.output_file);
  const primaryText = product.free ? 'Descargar gratis' : 'Comprar este Excel';
  const category = product.category ? `<p class="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">${product.category}</p>` : '';
  const subtitle = product.subtitle || 'Herramienta lista para usar';

  return `
    <article class="rounded-3xl bg-white border border-slate-200 shadow-soft overflow-hidden">
      <div class="p-8">
        <div class="flex items-start justify-between gap-4">
          <div>
            ${badgeMarkup(product)}
            <h3 class="mt-4 text-2xl font-bold tracking-tight text-ink">${product.title}</h3>
            ${category}
            <p class="mt-3 text-slate-600">${subtitle}</p>
          </div>
          <div class="text-right shrink-0">
            <p class="text-sm text-slate-500">${product.free ? 'Lead magnet' : 'Pago único'}</p>
            <p class="text-3xl font-bold text-ink">${price}</p>
          </div>
        </div>

        <div class="mt-6 grid sm:grid-cols-2 gap-4 text-sm text-slate-700">
          ${features}
        </div>

        <div class="mt-8 flex flex-col sm:flex-row gap-3">
          <a href="${downloadHref}" class="inline-flex items-center justify-center rounded-2xl bg-ink text-white px-5 py-3 font-semibold hover:bg-slate-800">${primaryText}</a>
          <a href="${WHATSAPP_URL}" class="inline-flex items-center justify-center rounded-2xl border border-slate-300 px-5 py-3 font-semibold text-slate-900 hover:border-slate-400">Consultar por WhatsApp</a>
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
