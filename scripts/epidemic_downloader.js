/**
 * Epidemic Sound Bulk Downloader
 *
 * USO:
 * 1. Abre https://www.epidemicsound.com/music/search/ en Chrome
 * 2. Asegurate de estar logueado con tu suscripcion activa
 * 3. Abre la consola del navegador (F12 > Console)
 * 4. Copia y pega TODO este script
 * 5. Ejecuta uno de los comandos al final del script
 *
 * Los archivos se descargan a tu carpeta de descargas del navegador.
 * Luego muevelos a media/music/{categoria}/
 */

// ============================================================
// CONFIGURACION
// ============================================================
const DELAY_BETWEEN_DOWNLOADS = 200;
const QUALITY = 'hq'; // 'hq' (320kbps) o 'normal' (128kbps)

// Registro de tracks descargados (persiste en localStorage)
const STORAGE_KEY = 'epidemic_downloaded_tracks';

// ============================================================
// REGISTRO DE DESCARGAS (anti-duplicados)
// ============================================================

function getDownloadedSet() {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    return data ? new Set(JSON.parse(data)) : new Set();
  } catch {
    return new Set();
  }
}

function markAsDownloaded(kosmosId) {
  const set = getDownloadedSet();
  set.add(kosmosId);
  localStorage.setItem(STORAGE_KEY, JSON.stringify([...set]));
}

function isAlreadyDownloaded(kosmosId) {
  return getDownloadedSet().has(kosmosId);
}

function getDownloadedCount() {
  return getDownloadedSet().size;
}

function clearDownloadHistory() {
  localStorage.removeItem(STORAGE_KEY);
  console.log('🗑️ Historial de descargas limpiado');
}

// ============================================================
// FUNCIONES PRINCIPALES
// ============================================================

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function searchTracks(term, limit = 50, offset = 0) {
  const res = await fetch(`/json/search/tracks/?term=${encodeURIComponent(term)}&limit=${limit}&offset=${offset}`);
  const data = await res.json();
  const tracks = [];

  if (data.entities && data.entities.tracks) {
    for (const [id, track] of Object.entries(data.entities.tracks)) {
      tracks.push({
        id: id,
        kosmosId: track.kosmosId,
        title: track.title,
        artist: track.creatives?.mainArtists?.[0]?.name || 'Unknown',
        genre: track.genres?.[0]?.displayTag || '',
        mood: track.moods?.[0]?.displayTag || '',
        bpm: track.bpm,
        duration: track.length,
        hasVocals: track.hasVocals
      });
    }
  }

  return tracks;
}

async function getDownloadUrl(kosmosId) {
  const params = new URLSearchParams({
    sound_id: kosmosId,
    stemType: 'full',
    qualityType: QUALITY,
    bundle: 'false',
    is_sfx: 'false',
    useBundler: 'true',
    context: 'MODAL_MUSIC_DOWNLOAD'
  });

  const res = await fetch(`/download/?${params}`);
  if (!res.ok) throw new Error(`Download API failed: ${res.status}`);
  const data = await res.json();
  return { url: data.assetUrl, remaining: data.remainingDownloads };
}

async function downloadTrack(track, category) {
  // Check duplicado
  if (isAlreadyDownloaded(track.kosmosId)) {
    console.log(`  ⏭️ ${track.title} (ya descargado, saltando)`);
    return 'skipped';
  }

  try {
    const { url, remaining } = await getDownloadUrl(track.kosmosId);

    const cleanTitle = track.title.replace(/[^a-zA-Z0-9\s-]/g, '').trim().replace(/\s+/g, '_');
    const cleanArtist = track.artist.replace(/[^a-zA-Z0-9\s-]/g, '').trim().replace(/\s+/g, '_');
    const filename = `${category}__${cleanArtist}__${cleanTitle}.mp3`;

    const response = await fetch(url);
    const blob = await response.blob();
    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(blobUrl);

    // Registrar como descargado
    markAsDownloaded(track.kosmosId);

    console.log(`  ✅ ${filename} (quedan ${remaining} descargas en Epidemic)`);
    return 'downloaded';
  } catch (e) {
    console.error(`  ❌ Error: ${track.title}: ${e.message}`);
    return 'failed';
  }
}

async function downloadByTerm(term, count = 50) {
  console.log(`\n🔍 Buscando "${term}" (${count} tracks)...`);

  // Puede que necesitemos buscar mas de count si hay duplicados
  const searchLimit = Math.min(count * 2, 500);
  const tracks = await searchTracks(term, searchLimit);
  console.log(`  Encontrados: ${tracks.length} tracks en Epidemic Sound`);

  let downloaded = 0, skipped = 0, failed = 0;
  const category = term.replace(/\s+/g, '_').toLowerCase();

  for (const track of tracks) {
    if (downloaded >= count) break;

    console.log(`  [${downloaded + 1}/${count}] ${track.artist} - ${track.title}`);
    const result = await downloadTrack(track, category);

    if (result === 'downloaded') {
      downloaded++;
      await sleep(DELAY_BETWEEN_DOWNLOADS);
    } else if (result === 'skipped') {
      skipped++;
    } else {
      failed++;
      await sleep(1000);
    }
  }

  console.log(`\n📊 "${term}": ${downloaded} descargados, ${skipped} saltados, ${failed} fallidos`);
  return { term, downloaded, skipped, failed };
}

async function downloadByTerms(terms, countPerTerm = 50) {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`🎵 EPIDEMIC SOUND BULK DOWNLOADER`);
  console.log(`${'='.repeat(60)}`);
  console.log(`Categorias: ${terms.join(', ')}`);
  console.log(`Tracks por categoria: ${countPerTerm}`);
  console.log(`Total estimado: ${terms.length * countPerTerm} tracks`);
  console.log(`Calidad: ${QUALITY === 'hq' ? '320kbps' : '128kbps'}`);
  console.log(`Ya descargados previamente: ${getDownloadedCount()}`);
  console.log(`${'='.repeat(60)}\n`);

  const results = [];

  for (let i = 0; i < terms.length; i++) {
    const result = await downloadByTerm(terms[i], countPerTerm);
    results.push(result);

    if (i < terms.length - 1) {
      console.log(`\n⏳ Pausa de 5 segundos...\n`);
      await sleep(5000);
    }
  }

  // Resumen
  console.log(`\n${'='.repeat(60)}`);
  console.log(`📊 RESUMEN FINAL`);
  console.log(`${'='.repeat(60)}`);

  let totalDown = 0, totalSkip = 0, totalFail = 0;
  for (const r of results) {
    console.log(`  ${r.term}: ${r.downloaded} ✅ / ${r.skipped} ⏭️ / ${r.failed} ❌`);
    totalDown += r.downloaded;
    totalSkip += r.skipped;
    totalFail += r.failed;
  }

  console.log(`${'─'.repeat(40)}`);
  console.log(`  TOTAL: ${totalDown} descargados, ${totalSkip} saltados, ${totalFail} fallidos`);
  console.log(`  Historial acumulado: ${getDownloadedCount()} tracks unicos`);
  console.log(`${'='.repeat(60)}`);

  return results;
}

/**
 * Descarga N tracks distribuidos equitativamente entre categorias diversas
 */
async function downloadDiversified(totalTracks = 1000) {
  const categories = [
    'energetic', 'chill', 'epic', 'fun', 'ambient',
    'electronic', 'happy', 'dark', 'dramatic', 'upbeat',
    'romantic', 'inspiring', 'aggressive', 'peaceful', 'groovy',
    'sad', 'tropical', 'retro', 'cinematic', 'quirky'
  ];

  const perCategory = Math.ceil(totalTracks / categories.length);

  console.log(`\n🎯 Descarga diversificada: ${totalTracks} tracks`);
  console.log(`   ${categories.length} categorias x ${perCategory} tracks cada una\n`);

  return await downloadByTerms(categories, perCategory);
}

// ============================================================
// LISTO!
// ============================================================

console.log('✅ Epidemic Sound Downloader cargado!');
console.log(`📦 Tracks ya descargados: ${getDownloadedCount()}`);
console.log('');
console.log('COMANDOS:');
console.log('');
console.log('  🎯 Descargar 1000 tracks diversificados (20 categorias x 50):');
console.log('     await downloadDiversified(1000)');
console.log('');
console.log('  📁 Descargar por categorias especificas:');
console.log('     await downloadByTerms(["epic", "chill", "fun"], 30)');
console.log('');
console.log('  📁 Descargar una sola categoria:');
console.log('     await downloadByTerm("epic", 50)');
console.log('');
console.log('  🔍 Buscar sin descargar:');
console.log('     await searchTracks("chill", 10)');
console.log('');
console.log('  📊 Ver cuantos tracks ya tienes:');
console.log('     getDownloadedCount()');
console.log('');
console.log('  🗑️ Limpiar historial (para re-descargar):');
console.log('     clearDownloadHistory()');
