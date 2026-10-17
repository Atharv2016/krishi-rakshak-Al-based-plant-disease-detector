const $ = (selector) => document.querySelector(selector);
const API_BASE = window.KRISHI_API_BASE || '';
const HISTORY_KEY = 'krishiRakshakHistoryV1';
let currentLanguage = localStorage.getItem('krishiLanguage') || 'en';
let firebaseServices = null;

const translations = {
 en: {
  tagline:'AI Plant Health Assistant', language:'Language', eyebrow:'SMART FARMING • HEALTHIER CROPS', heroTitle:'A healthier crop starts with a leaf.', heroSubtitle:'Upload a clear leaf photo to screen for common tomato, potato and grape diseases.', startScan:'Scan a leaf', growTogether:'Grow with confidence', feature1:'Leaf image scan', feature2:'AI-powered screening', feature3:'English + Marathi', detectorEyebrow:'PLANT HEALTH CHECK', detectorTitle:'Check your plant', detectorSubtitle:'Choose a clear, well-lit image showing the leaf symptoms.', uploadTitle:'Upload a leaf photo', uploadHint:'JPG, PNG or WEBP · up to 8 MB', browse:'Choose image', removeImage:'Remove image', confirmLeaf:'I have selected a plant leaf image, not a person or unrelated object.', analyze:'Analyze leaf', analyzing:'Analyzing…', privacyNote:'Your photo is sent to the prediction server for analysis. Do not upload private or sensitive images.', photoTipsTitle:'Tips for a better scan', tip1:'Use natural light and keep the leaf in focus.', tip2:'Include the affected area and some of the leaf edges.', tip3:'Avoid strong shadows and blurry photos.', tip4:'For better results, photograph one leaf at a time.', resultEyebrow:'SCREENING RESULT', symptomsLabel:'Symptoms to check', adviceLabel:'General next steps', newScan:'Scan another leaf', historyEyebrow:'YOUR RECENT SCANS', historyTitle:'Scan history', historySubtitle:'Recent results are saved in this browser. Firebase can be enabled for cloud history.', emptyHistory:'Your scans will appear here.', clearHistory:'Clear local history', footerText:'Built to support farmers with accessible AI screening.', footerWarning:'This tool is not a confirmed diagnosis. Consult an agricultural expert before treatment.', noFile:'Please choose a leaf image first.', consent:'Please confirm that the selected image is a plant leaf.', invalidType:'Please select a JPG, PNG or WEBP image.', tooLarge:'Image must be 8 MB or smaller.', modelMissing:'The AI model is not ready yet. Train the model and place the model files in the model folder. See README.md.', genericError:'Could not analyze this image. Please try again.', serverError:'Could not connect to the prediction server. Check that the Flask API is running.', saved:'Saved', confidence:'model confidence', unknown:'Unknown result', scanLabel:'Scan', historyEmpty:'No scans yet.', deleteConfirm:'Clear all scan history stored in this browser?', disclaimer:'AI screening only. Image predictions can be wrong. Confirm the condition with an agricultural expert before choosing treatment.', historyCloud:'Cloud history enabled', historyLocal:'Browser-only history', scanError:'Error'
 },
 mr: {
  tagline:'AI आधारित पीक आरोग्य सहाय्यक', language:'भाषा', eyebrow:'स्मार्ट शेती • निरोगी पिके', heroTitle:'निरोगी पिकाची सुरुवात पानापासून.', heroSubtitle:'टोमॅटो, बटाटा आणि द्राक्षांवरील सामान्य रोगांची प्राथमिक तपासणी करण्यासाठी पानाचा स्पष्ट फोटो अपलोड करा.', startScan:'पान तपासा', growTogether:'विश्वासाने शेती करा', feature1:'पानाच्या फोटोची तपासणी', feature2:'AI आधारित प्राथमिक निदान', feature3:'मराठी + इंग्रजी', detectorEyebrow:'पीक आरोग्य तपासणी', detectorTitle:'तुमच्या पिकाची तपासणी करा', detectorSubtitle:'लक्षणे स्पष्ट दिसतील असा, चांगल्या प्रकाशातील फोटो निवडा.', uploadTitle:'पानाचा फोटो अपलोड करा', uploadHint:'JPG, PNG किंवा WEBP · कमाल 8 MB', browse:'फोटो निवडा', removeImage:'फोटो काढून टाका', confirmLeaf:'मी व्यक्तीचा किंवा असंबंधित वस्तूचा नव्हे, तर वनस्पतीच्या पानाचा फोटो निवडला आहे.', analyze:'पान तपासा', analyzing:'तपासणी सुरू आहे…', privacyNote:'तपासणीसाठी फोटो prediction server वर पाठवला जातो. खाजगी किंवा संवेदनशील फोटो अपलोड करू नका.', photoTipsTitle:'चांगल्या तपासणीसाठी टिप्स', tip1:'नैसर्गिक प्रकाशात आणि स्पष्ट फोकसमध्ये फोटो घ्या.', tip2:'बाधित भागासह पानाच्या कडा देखील दिसू द्या.', tip3:'गडद सावल्या आणि धूसर फोटो टाळा.', tip4:'चांगल्या निकालासाठी एका वेळी एकाच पानाचा फोटो घ्या.', resultEyebrow:'प्राथमिक तपासणीचा निकाल', symptomsLabel:'तपासण्यासारखी लक्षणे', adviceLabel:'सामान्य पुढील उपाय', newScan:'दुसरे पान तपासा', historyEyebrow:'अलीकडील तपासण्या', historyTitle:'तपासणी इतिहास', historySubtitle:'अलीकडील निकाल या ब्राउझरमध्ये जतन होतात. क्लाउड इतिहासासाठी Firebase सुरू करता येईल.', emptyHistory:'तुमच्या तपासण्या येथे दिसतील.', clearHistory:'ब्राउझरमधील इतिहास पुसा', footerText:'शेतकऱ्यांसाठी सुलभ AI तपासणी.', footerWarning:'हे निश्चित निदान नाही. उपचार करण्यापूर्वी कृषी तज्ज्ञांचा सल्ला घ्या.', noFile:'कृपया पानाचा फोटो निवडा.', consent:'कृपया निवडलेला फोटो वनस्पतीच्या पानाचा आहे याची पुष्टी करा.', invalidType:'कृपया JPG, PNG किंवा WEBP फोटो निवडा.', tooLarge:'फोटोचा आकार 8 MB किंवा त्यापेक्षा कमी असावा.', modelMissing:'AI मॉडेल अद्याप तयार नाही. मॉडेल ट्रेन करून model फोल्डरमध्ये फाइल ठेवा. README.md पहा.', genericError:'फोटो तपासता आला नाही. पुन्हा प्रयत्न करा.', serverError:'Prediction server शी संपर्क होत नाही. Flask API सुरू आहे का ते तपासा.', saved:'जतन केले', confidence:'मॉडेलचा विश्वास स्कोअर', unknown:'अज्ञात निकाल', scanLabel:'तपासणी', historyEmpty:'अजून तपासणी नाही.', deleteConfirm:'या ब्राउझरमधील सर्व तपासणी इतिहास पुसायचा का?', disclaimer:'ही केवळ AI आधारित प्राथमिक तपासणी आहे. अंदाज चुकीचा असू शकतो. उपचार निवडण्यापूर्वी कृषी तज्ज्ञांकडून खात्री करा.', historyCloud:'क्लाउड इतिहास सुरू आहे', historyLocal:'फक्त ब्राउझरमध्ये इतिहास', scanError:'त्रुटी'
 }
};

function t(key) { return (translations[currentLanguage] || translations.en)[key] || translations.en[key] || key; }
function setLanguage(lang) {
 currentLanguage = lang === 'mr' ? 'mr' : 'en';
 localStorage.setItem('krishiLanguage', currentLanguage);
 document.documentElement.lang = currentLanguage === 'mr' ? 'mr' : 'en';
 document.querySelectorAll('[data-i18n]').forEach(el => { const key = el.dataset.i18n; if (t(key)) el.textContent = t(key); });
 renderHistory();
}
function showStatus(message, type='info') {
 const el = $('#statusMessage'); el.hidden = !message; el.textContent = message; el.className = `status-message ${type}`;
}
function loadHistory() { try { return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); } catch { return []; } }
function saveHistory(items) { localStorage.setItem(HISTORY_KEY, JSON.stringify(items.slice(0, 10))); }
function renderHistory() {
 const root = $('#historyList'); const history = loadHistory(); root.replaceChildren();
 if (!history.length) { const p = document.createElement('p'); p.className = 'empty-history'; p.textContent = t('emptyHistory'); root.append(p); return; }
 history.forEach(item => {
  const row = document.createElement('article'); row.className = 'history-item';
  const icon = document.createElement('span'); icon.className = 'history-icon'; icon.textContent = item.className?.startsWith('Tomato') ? '🍅' : item.className?.startsWith('Potato') ? '🥔' : '🍇';
  const detail = document.createElement('div'); detail.className = 'history-detail';
  const title = document.createElement('strong'); title.textContent = item.title || item.className || t('unknown');
  const meta = document.createElement('small'); meta.textContent = `${new Date(item.time).toLocaleString(currentLanguage === 'mr' ? 'mr-IN' : 'en-IN')} · ${item.confidence}% ${t('confidence')}`;
  detail.append(title, meta); row.append(icon, detail); root.append(row);
 });
}
function validateFile(file) {
 if (!file) return t('noFile');
 if (!['image/jpeg','image/png','image/webp'].includes(file.type)) return t('invalidType');
 if (file.size > 8 * 1024 * 1024) return t('tooLarge');
 return '';
}
function resetImage() {
 $('#leafImage').value = ''; $('#previewWrap').hidden = true; $('#previewImage').removeAttribute('src');
 $('#dropZone').hidden = false; $('#analyzeButton').disabled = true; showStatus('');
}
$('#languageSelect').value = currentLanguage;
$('#languageSelect').addEventListener('change', e => setLanguage(e.target.value));
setLanguage(currentLanguage);

$('#leafImage').addEventListener('change', () => {
 const file = $('#leafImage').files[0]; const error = validateFile(file);
 if (error) { resetImage(); showStatus(error, 'error'); return; }
 $('#previewImage').src = URL.createObjectURL(file); $('#previewWrap').hidden = false; $('#dropZone').hidden = true;
 $('#analyzeButton').disabled = !$('#confirmLeaf').checked; showStatus('');
});
$('#confirmLeaf').addEventListener('change', () => { $('#analyzeButton').disabled = !$('#confirmLeaf').checked || !$('#leafImage').files[0]; });
$('#removeImage').addEventListener('click', resetImage);
$('#newScanButton').addEventListener('click', () => { resetImage(); $('#resultCard').hidden = true; $('#detector').scrollIntoView({behavior:'smooth'}); });
$('#clearHistory').addEventListener('click', () => { if (confirm(t('deleteConfirm'))) { localStorage.removeItem(HISTORY_KEY); renderHistory(); } });

$('#uploadForm').addEventListener('submit', async event => {
 event.preventDefault(); const file = $('#leafImage').files[0]; const error = validateFile(file);
 if (error) return showStatus(error, 'error');
 if (!$('#confirmLeaf').checked) return showStatus(t('consent'), 'error');
 const button = $('#analyzeButton'); button.disabled = true; button.querySelector('span').textContent = t('analyzing'); showStatus(t('analyzing'));
 const form = new FormData(); form.append('image', file); form.append('language', currentLanguage);
 try {
  const response = await fetch(`${API_BASE}/api/predict`, {method:'POST', body:form});
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
   if (data.code === 'MODEL_NOT_READY') throw new Error(t('modelMissing'));
   throw new Error(data.error || t('genericError'));
  }
  $('#resultTitle').textContent = data.info?.title || data.class_name || t('unknown');
  $('#confidence').textContent = `${data.confidence}% ${t('confidence')}`;
  $('#resultSymptoms').textContent = data.info?.symptoms || '';
  $('#resultAdvice').textContent = data.info?.advice || '';
  $('#resultDisclaimer').textContent = currentLanguage === 'mr' ? t('disclaimer') : (data.disclaimer || t('disclaimer'));
  $('#resultCard').hidden = false; $('#resultCard').scrollIntoView({behavior:'smooth', block:'start'}); showStatus('');
  const history = loadHistory(); history.unshift({className:data.class_name, title:data.info?.title || data.class_name, confidence:data.confidence, time:new Date().toISOString()}); saveHistory(history); renderHistory();
  if (firebaseServices) await saveCloudHistory(data).catch(err => console.warn('Cloud history save failed:', err));
 } catch (err) {
  showStatus(err.message === 'Failed to fetch' ? t('serverError') : err.message || t('genericError'), 'error');
 } finally { button.disabled = !$('#confirmLeaf').checked || !$('#leafImage').files[0]; button.querySelector('span').textContent = t('analyze'); }
});
renderHistory();

// Firebase is optional. Anonymous auth + Firestore rules in firebase/firestore.rules restrict each user to their own records.
async function initFirebase() {
 const cfg = window.KRISHI_FIREBASE_CONFIG || {};
 if (!cfg.apiKey || cfg.apiKey.startsWith('YOUR_') || !cfg.projectId || cfg.projectId.startsWith('YOUR_')) return;
 try {
  const [appMod, authMod, firestoreMod] = await Promise.all([
   import('https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js'),
   import('https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js'),
   import('https://www.gstatic.com/firebasejs/10.14.1/firebase-firestore.js')
  ]);
  const app = appMod.initializeApp(cfg); const auth = authMod.getAuth(app); await authMod.signInAnonymously(auth);
  firebaseServices = {auth, firestore:firestoreMod, db:firestoreMod.getFirestore(app)};
  console.info(t('historyCloud'));
 } catch (error) { console.warn('Firebase not enabled; using local history.', error); firebaseServices = null; }
}
async function saveCloudHistory(data) {
 if (!firebaseServices?.auth.currentUser) return;
 const {collection, addDoc, serverTimestamp} = firebaseServices.firestore;
 await addDoc(collection(firebaseServices.db, 'users', firebaseServices.auth.currentUser.uid, 'scans'), {
  className: data.class_name, title: data.info?.title || data.class_name, confidence: data.confidence, createdAt: serverTimestamp()
 });
}
initFirebase();
