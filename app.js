const state = {
  preset: 'photoreal',
  skinTone: 'light neutral',
  hairStyle: 'long wavy',
  hairColor: '#3b2f2f',
  bodyType: 'slim',
  outfit: 'summer dress',
  outfitColors: ['#9b5de5', '#ffd6e7'],
  pose: 'natural standing',
  seed: Math.floor(Math.random() * 1000000),
  backend: { type: 'a1111', url: '', model: '' },
  files: { reference: null, pose: null, mask: null },
  referenceStrength: 0.6,
};

const PRESETS = [
  { id: 'photoreal', label: 'Photoreal' },
  { id: 'editorial', label: 'Editorial' },
  { id: 'soft_glam', label: 'Soft glam' },
  { id: 'anime', label: 'Anime' },
];

const SKIN_TONES = [
  { label: 'Light', value: 'light neutral' },
  { label: 'Fair warm', value: 'fair warm' },
  { label: 'Medium', value: 'medium neutral' },
  { label: 'Tan', value: 'tan warm' },
  { label: 'Deep', value: 'deep neutral' },
];

const HAIR_STYLES = [
  { id: 'long_wavy', label: 'Long wavy' },
  { id: 'straight_bob', label: 'Straight bob' },
  { id: 'ponytail', label: 'Ponytail' },
  { id: 'braids', label: 'Braids' },
  { id: 'bun', label: 'Bun' },
];

const HAIR_COLORS = ['#0e0e10', '#3b2f2f', '#5c3b1e', '#b57f50', '#cfa16c', '#e2c285', '#ddb3d6', '#ff8fa3', '#7aa2ff'];

const BODY_TYPES = [
  { id: 'slim', label: 'Slim' },
  { id: 'athletic', label: 'Athletic' },
  { id: 'curvy', label: 'Curvy' },
  { id: 'petite', label: 'Petite' },
  { id: 'tall', label: 'Tall' },
];

const OUTFITS = [
  { id: 'summer_dress', label: 'Summer dress' },
  { id: 'tee_jeans', label: 'Tee + jeans' },
  { id: 'hoodie_skirt', label: 'Hoodie + skirt' },
  { id: 'blazer_trousers', label: 'Blazer + trousers' },
  { id: 'sportswear', label: 'Sportswear' },
];

const OUTFIT_COLORS = ['#9b5de5', '#7aa2ff', '#ff8fab', '#ffd166', '#06d6a0', '#222222', '#f0f0f0'];

const POSES = [
  { id: 'natural', label: 'Natural standing' },
  { id: 'hands_hips', label: 'Hands on hips' },
  { id: 'walking', label: 'Walking' },
  { id: 'seated', label: 'Seated' },
];

function $(id) { return document.getElementById(id); }

function createChip(label, selected, onClick) {
  const el = document.createElement('div');
  el.className = 'chip' + (selected ? ' selected' : '');
  el.textContent = label;
  el.onclick = onClick;
  return el;
}

function createCard({ label, img }, selected, onClick) {
  const el = document.createElement('div');
  el.className = 'card' + (selected ? ' selected' : '');
  const image = document.createElement('img');
  image.alt = label;
  // Placeholder pattern background; you can replace with SD-generated thumbnails.
  image.style.backgroundImage = 'linear-gradient(135deg, #f3f4f6 25%, transparent 25%), linear-gradient(225deg, #f3f4f6 25%, transparent 25%), linear-gradient(45deg, #f3f4f6 25%, transparent 25%), linear-gradient(315deg, #f3f4f6 25%, #fff 25%)';
  image.style.backgroundSize = '10px 10px';
  image.style.backgroundPosition = '0 0, 0 5px, 5px -5px, -5px 0px';
  const title = document.createElement('div');
  title.textContent = label;
  el.appendChild(image);
  el.appendChild(title);
  el.onclick = onClick;
  return el;
}

function createSwatch(hex, selected, onClick) {
  const el = document.createElement('div');
  el.className = 'swatch' + (selected ? ' selected' : '');
  el.style.background = hex;
  el.title = hex;
  el.onclick = onClick;
  return el;
}

function renderSelectors() {
  const presetGrid = $('presetGrid');
  presetGrid.innerHTML = '';
  PRESETS.forEach(p => {
    presetGrid.appendChild(createChip(p.label, state.preset === p.id, () => { state.preset = p.id; renderSelectors(); }));
  });

  const skinGrid = $('skinGrid');
  skinGrid.innerHTML = '';
  SKIN_TONES.forEach(s => {
    skinGrid.appendChild(createChip(s.label, state.skinTone === s.value, () => { state.skinTone = s.value; renderSelectors(); }));
  });

  const hairStyleGrid = $('hairStyleGrid');
  hairStyleGrid.innerHTML = '';
  HAIR_STYLES.forEach(h => {
    hairStyleGrid.appendChild(createCard({ label: h.label }, state.hairStyle === h.label.toLowerCase(), () => { state.hairStyle = h.label.toLowerCase(); renderSelectors(); }));
  });

  const hairColorGrid = $('hairColorGrid');
  hairColorGrid.innerHTML = '';
  HAIR_COLORS.forEach(hex => {
    hairColorGrid.appendChild(createSwatch(hex, state.hairColor === hex, () => { state.hairColor = hex; renderSelectors(); }));
  });

  const bodyTypeGrid = $('bodyTypeGrid');
  bodyTypeGrid.innerHTML = '';
  BODY_TYPES.forEach(b => {
    bodyTypeGrid.appendChild(createChip(b.label, state.bodyType === b.label.toLowerCase(), () => { state.bodyType = b.label.toLowerCase(); renderSelectors(); }));
  });

  const outfitGrid = $('outfitGrid');
  outfitGrid.innerHTML = '';
  OUTFITS.forEach(o => {
    outfitGrid.appendChild(createCard({ label: o.label }, state.outfit === o.label.toLowerCase(), () => { state.outfit = o.label.toLowerCase(); renderSelectors(); }));
  });

  const outfitColorGrid = $('outfitColorGrid');
  outfitColorGrid.innerHTML = '';
  OUTFIT_COLORS.forEach(hex => {
    const selected = state.outfitColors.includes(hex);
    outfitColorGrid.appendChild(createSwatch(hex, selected, () => {
      const set = new Set(state.outfitColors);
      if (set.has(hex)) { set.delete(hex); } else { set.add(hex); }
      state.outfitColors = Array.from(set).slice(0, 3);
      renderSelectors();
    }));
  });

  const poseGrid = $('poseGrid');
  poseGrid.innerHTML = '';
  POSES.forEach(p => {
    poseGrid.appendChild(createChip(p.label, state.pose.startsWith(p.label.split(' ')[0].toLowerCase()), () => { state.pose = p.label.toLowerCase(); renderSelectors(); }));
  });

  updatePromptOutputs();
}

function hexToName(hex) {
  const map = {
    '#0e0e10': 'jet black', '#3b2f2f': 'dark brown', '#5c3b1e': 'chestnut', '#b57f50': 'auburn',
    '#cfa16c': 'dark blonde', '#e2c285': 'honey blonde', '#ddb3d6': 'pastel lavender', '#ff8fa3': 'pastel pink', '#7aa2ff': 'pastel blue',
    '#9b5de5': 'violet', '#ffd6e7': 'soft pink', '#ff8fab': 'pink', '#ffd166': 'mustard yellow', '#06d6a0': 'mint green', '#222222': 'black', '#f0f0f0': 'white'
  };
  return map[hex.toLowerCase()] || hex;
}

function buildPrompt() {
  const stylePreset = {
    photoreal: 'photorealistic, natural skin texture, soft lighting, 85mm lens, high detail',
    editorial: 'fashion editorial, dramatic lighting, studio background, sharp details',
    soft_glam: 'soft glam, diffused light, pastel palette, gentle makeup',
    anime: 'anime style, clean lineart, cel shading, high detail',
  }[state.preset] || '';

  const subject = `young adult woman, ${state.skinTone}, ${state.hairStyle} hair, ${hexToName(state.hairColor)} hair, ${state.bodyType} body`;
  const outfitColors = state.outfitColors.map(hexToName).join(', ');
  const outfit = `${state.outfit} in ${outfitColors}`;
  const pose = state.pose;

  const base = `${subject}, wearing ${outfit}, ${pose}, full body, ${stylePreset}`;
  const negatives = 'lowres, blurry, bad hands, extra fingers, deformed, watermark, jpeg artifacts, text, nsfw';
  return { prompt: base, negative: negatives };
}

function buildApiPayload() {
  const { prompt, negative } = buildPrompt();
  return {
    prompt,
    negative_prompt: negative,
    seed: state.seed,
    steps: 28,
    cfg_scale: state.preset === 'anime' ? 6.5 : 5.5,
    width: 768,
    height: 1152,
    sampler_name: 'DPM++ 2M Karras',
  };
}

function updatePromptOutputs() {
  const { prompt, negative } = buildPrompt();
  $('promptOut').value = prompt;
  $('negativeOut').value = negative;
  $('apiPayload').textContent = JSON.stringify(buildApiPayload(), null, 2);
}

function randomize() {
  const pick = arr => arr[Math.floor(Math.random() * arr.length)];
  state.preset = pick(PRESETS).id;
  state.skinTone = pick(SKIN_TONES).value;
  state.hairStyle = pick(HAIR_STYLES).label.toLowerCase();
  state.hairColor = pick(HAIR_COLORS);
  state.bodyType = pick(BODY_TYPES).label.toLowerCase();
  state.outfit = pick(OUTFITS).label.toLowerCase();
  state.outfitColors = [pick(OUTFIT_COLORS), pick(OUTFIT_COLORS)].filter((v, i, a) => a.indexOf(v) === i).slice(0, 2);
  state.pose = pick(POSES).label.toLowerCase();
  state.seed = Math.floor(Math.random() * 100000000);
  renderSelectors();
}

function copyPrompt() {
  const t = $('promptOut').value + '\nNEGATIVE: ' + $('negativeOut').value;
  navigator.clipboard.writeText(t);
}

function init() {
  $('btn-random').addEventListener('click', randomize);
  $('btn-generate-prompt').addEventListener('click', updatePromptOutputs);
  $('btn-copy').addEventListener('click', copyPrompt);
  $('backendType').addEventListener('change', e => { state.backend.type = e.target.value; });
  $('backendUrl').addEventListener('input', e => { state.backend.url = e.target.value.trim(); });
  $('modelName').addEventListener('input', e => { state.backend.model = e.target.value.trim(); });
  $('input-reference').addEventListener('change', e => { state.files.reference = e.target.files[0] || null; });
  $('input-pose').addEventListener('change', e => { state.files.pose = e.target.files[0] || null; });
  $('input-mask').addEventListener('change', e => { state.files.mask = e.target.files[0] || null; });
  $('referenceStrength').addEventListener('input', e => { state.referenceStrength = Number(e.target.value); });
  $('btn-test-backend').addEventListener('click', testBackend);
  $('btn-generate-img').addEventListener('click', () => generateImage('txt2img'));
  $('btn-generate-img2img').addEventListener('click', () => generateImage('img2img'));
  $('btn-export-video-json').addEventListener('click', exportVideoJSON);
  renderSelectors();
}

document.addEventListener('DOMContentLoaded', init);

async function testBackend() {
  if (!state.backend.url) { alert('Enter backend URL'); return; }
  try {
    const res = await fetch(state.backend.url + '/sdapi/v1/sd-models', { method: 'GET' });
    if (!res.ok) throw new Error(await res.text());
    alert('Backend reachable.');
  } catch (e) {
    alert('Backend error: ' + e.message);
  }
}

function fileToDataURL(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = reject;
    r.readAsDataURL(file);
  });
}

async function generateImage(mode) {
  const url = state.backend.url;
  if (!url) { alert('Set backend URL'); return; }
  const payload = buildApiPayload();
  if (state.backend.model) payload.override_settings = { sd_model_checkpoint: state.backend.model };

  let endpoint = '/sdapi/v1/txt2img';
  if (mode === 'img2img') endpoint = '/sdapi/v1/img2img';

  const controlnetArgs = [];
  if (state.files.pose) {
    const b64 = await fileToDataURL(state.files.pose);
    controlnetArgs.push({
      input_image: b64,
      module: 'openpose',
      model: 'control_v11p_sd15_openpose [cab727d4]',
      weight: 0.8,
      resize_mode: 1,
      guidance: 1.0,
      guidance_start: 0.0,
      guidance_end: 1.0,
    });
  }
  if (controlnetArgs.length > 0) {
    payload.alwayson_scripts = payload.alwayson_scripts || {};
    payload.alwayson_scripts.controlnet = { args: controlnetArgs };
  }

  if (mode === 'img2img' && state.files.reference) {
    payload.init_images = [await fileToDataURL(state.files.reference)];
    payload.denoising_strength = state.referenceStrength;
    if (state.files.mask) payload.mask = await fileToDataURL(state.files.mask);
  }

  try {
    const res = await fetch(url + endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    const images = data.images || [];
    const container = document.getElementById('results');
    container.innerHTML = '';
    images.forEach(imgB64 => {
      const card = document.createElement('div');
      card.className = 'card';
      const img = document.createElement('img');
      img.src = 'data:image/png;base64,' + imgB64;
      card.appendChild(img);
      container.appendChild(card);
    });
  } catch (e) {
    alert('Generation error: ' + e.message);
  }
}

function exportVideoJSON() {
  const { prompt, negative } = buildPrompt();
  const deforum = {
    animation_mode: '2D',
    max_frames: 120,
    fps: 12,
    seed: state.seed,
    sampler: 'DPM++ 2M Karras',
    steps: 25,
    cfg_scale: state.preset === 'anime' ? 6.5 : 5.5,
    width: 768,
    height: 1152,
    text_prompts: {
      '0': prompt,
    },
    negative_prompt: negative,
  };
  const blob = new Blob([JSON.stringify(deforum, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'video_prompt.json';
  a.click();
}

