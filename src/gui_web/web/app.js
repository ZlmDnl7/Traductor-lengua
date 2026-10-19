const $ = (id) => document.getElementById(id);

const viewLogin = $("viewLogin");
const viewRegister = $("viewRegister");
const viewRegisterLanguage = $("viewRegisterLanguage");
const viewRegisterAccessibility = $("viewRegisterAccessibility");
const viewMenu = $("viewMenu");
const viewInteraction = $("viewInteraction");
const viewAprendizaje = $("viewAprendizaje");
const viewEvaluacionConfig = $("viewEvaluacionConfig");
const viewEvaluacionRun = $("viewEvaluacionRun");
const viewEvaluacionResultados = $("viewEvaluacionResultados");
const viewEvaluacionHistorial = $("viewEvaluacionHistorial");
const viewSettings = $("viewSettings");

// Evaluation elements
const evalRequestedLetter = $("evalRequestedLetter");
const evalDetectedLetter = $("evalDetectedLetter");
const evalTime = $("evalTime");
const evalScore = $("evalScore");
const evalHits = $("evalHits");
const evalErrors = $("evalErrors");
const evalResultScore = $("evalResultScore");
const evalResultHits = $("evalResultHits");
const evalResultErrors = $("evalResultErrors");
const evalResultDuration = $("evalResultDuration");
const evalResultHitLetters = $("evalResultHitLetters");
const evalResultErrorLetters = $("evalResultErrorLetters");
const evaluationHistoryList = $("evaluationHistoryList");
const evaluationHistoryEmpty = $("evaluationHistoryEmpty");
const evaluationHistorySummary = $("evaluationHistorySummary");
const evaluationHistoryMeta = $("evaluationHistoryMeta");
const historyHitLetters = $("historyHitLetters");
const historyErrorLetters = $("historyErrorLetters");
const evaluationScoreProgress = $("evaluationScoreProgress");
const videoEvaluacion = $("videoEvaluacion");
const videoFallbackEvaluacion = $("videoFallbackEvaluacion");
const evalVideoWrap = $("evalVideoWrap");
const evalOverlay = $("evalOverlay");
const evalExitConfirm = $("evalExitConfirm");
const btnContinueEvaluation = $("btnContinueEvaluation");
const btnExitEvaluation = $("btnExitEvaluation");
const viewReto = $("viewReto");

const loginError = $("loginError");
const regError = $("regError");
const voiceError = $("voiceError");
const voiceLanguage = $("voiceLanguage");
const ttsError = $("ttsError");

const chat = $("chat");
const videoInteraction = $("videoInteraction");
const videoFallbackInteraction = $("videoFallbackInteraction");
const videoAprendizaje = $("videoAprendizaje");
const videoFallbackAprendizaje = $("videoFallbackAprendizaje");
const letterPill = $("letterPill");
const signText = $("signText");
const learningProgress = $("learningProgress");
const learningLetter = $("learningLetter");
const learningReferenceArt = $("learningReferenceArt");
const learningReferenceImage = $("learningReferenceImage");
const learningVideoWrap = $("learningVideoWrap");
const learningOverlay = $("learningOverlay");
const learningDetected = $("learningDetected");
const learningStatusPill = $("learningStatusPill");
const learningCaption = $("learningCaption");
const learningCounter = $("learningCounter");
const learningNotice = $("learningNotice");
const learningComplete = $("learningComplete");
const learningCompleteTitle = $("learningCompleteTitle");
const retoCompletePassed = $("retoCompletePassed");
const btnStarLetter = $("btnStarLetter");
const starIcon = $("starIcon");
const learningDifficultCount = $("learningDifficultCount");
const learningAssistantCard = $("learningAssistantCard");
const learningAssistantMessage = $("learningAssistantMessage");
const learningAssistantLetter = $("learningAssistantLetter");
const learningAssistantCorrect = $("learningAssistantCorrect");
const learningAssistantAccuracy = $("learningAssistantAccuracy");
const learningAssistantAttempts = $("learningAssistantAttempts");
const learningAssistantRecommendation = $("learningAssistantRecommendation");
const btnAssistantFavorite = $("btnAssistantFavorite");
const btnPracticeNow = $("btnPracticeNow");
const btnLogout = $("btnLogout");
const settingsColorBlindMode = $("settingsColorBlindMode");
const settingsAccessibleReadingMode = $("settingsAccessibleReadingMode");
const settingsReadingFontSize = $("settingsReadingFontSize");
const regReadingFontSize = $("regReadingFontSize");
const settingsDyslexiaSpacingMode = $("settingsDyslexiaSpacingMode");
const settingsNightMode = $("settingsNightMode");
const btnSaveSettings = $("btnSaveSettings");
const settingsError = $("settingsError");

// Repaso (letras marcadas con estrella)
const viewRepaso = $("viewRepaso");
const repasoEmptyState = $("repasoEmptyState");
const repasoPracticeWrap = $("repasoPracticeWrap");
const repasoProgress = $("repasoProgress");
const repasoReferenceArt = $("repasoReferenceArt");
const repasoReferenceImage = $("repasoReferenceImage");
const repasoLetter = $("repasoLetter");
const repasoDetected = $("repasoDetected");
const repasoStatusPill = $("repasoStatusPill");
const repasoCaption = $("repasoCaption");
const repasoVideoWrap = $("repasoVideoWrap");
const repasoOverlay = $("repasoOverlay");
const videoRepaso = $("videoRepaso");
const videoFallbackRepaso = $("videoFallbackRepaso");
const btnUnstarRepaso = $("btnUnstarRepaso");
const repasoNotice = $("repasoNotice");
const repasoComplete = $("repasoComplete");
// Asistente IA de Repaso
const repasoAssistantCard = $("repasoAssistantCard");
const repasoAssistantTitle = $("repasoAssistantTitle");
const repasoAssistantMessage = $("repasoAssistantMessage");
const repasoAssistantTip = $("repasoAssistantTip");

// Reto (deletrea tu nombre o una palabra)
const videoReto = $("videoReto");
const videoFallbackReto = $("videoFallbackReto");
const retoTitle = $("retoTitle");
const retoWord = $("retoWord");
const retoGrid = $("retoGrid");
const retoLetter = $("retoLetter");
const retoReferenceArt = $("retoReferenceArt");
const retoReferenceImage = $("retoReferenceImage");
const retoCaption = $("retoCaption");
const retoVideoWrap = $("retoVideoWrap");
const retoOverlay = $("retoOverlay");
const retoSubtitle = $("retoSubtitle");
const retoProgressFill = $("retoProgressFill");
const retoEmpty = $("retoEmpty");
const retoComplete = $("retoComplete");
const retoCompleteText = $("retoCompleteText");
const retoSkipped = $("retoSkipped");
const retoAiHint = $("retoAiHint");
const retoAiHintTitle = $("retoAiHintTitle");
const retoAiHintMessage = $("retoAiHintMessage");
const retoAiHintTip = $("retoAiHintTip");

// ===== Idioma =====
// El idioma de aprendizaje define TODO: textos (i18n.js), alfabeto, imágenes,
// instrucciones de cada seña, voz y respuestas de la IA. El perfil completo lo
// entrega el backend (src/languages/profiles.py) mediante get_language_pack.
const UI_LANGUAGE_STORAGE_KEY = "traductor.uiLanguage";

function loadStoredUiLanguage(){
  try{
    const value = localStorage.getItem(UI_LANGUAGE_STORAGE_KEY);
    return I18N[value] ? value : "es";
  }catch(e){
    return "es";
  }
}

function storeUiLanguage(code){
  try{ localStorage.setItem(UI_LANGUAGE_STORAGE_KEY, code); }catch(e){ /* preferencia opcional */ }
}

let currentLearningLanguage = loadStoredUiLanguage();
const languagePacks = {};
let languagePack = LANGUAGE_FALLBACK[currentLearningLanguage];
let LETTERS = languagePack.learning_alphabet;

function tr(key, ...args){
  const texts = I18N[currentLearningLanguage] || I18N.es;
  const value = (key in texts) ? texts[key] : I18N.es[key];
  if(typeof value === "function") return value(...args);
  return value === undefined ? key : value;
}

const languagePackRequests = {};

async function ensureLanguagePack(code){
  if(languagePacks[code]) return languagePacks[code];
  if(!window.pywebview || !window.pywebview.api || !window.pywebview.api.get_language_pack) return null;
  if(!languagePackRequests[code]){
    languagePackRequests[code] = window.pywebview.api.get_language_pack(code).then((res) => {
      if(res && res.ok && res.language_pack) languagePacks[code] = res.language_pack;
      return languagePacks[code] || null;
    }).catch(() => null).finally(() => { delete languagePackRequests[code]; });
  }
  // Mientras tanto se mantiene el respaldo local (LANGUAGE_FALLBACK).
  return languagePackRequests[code];
}

function signLanguageName(){
  return languagePack.sign_language === "LIBRAS" ? "Libras" : languagePack.sign_language;
}

function signDescription(letter){
  const descriptions = languagePack.sign_descriptions || {};
  return descriptions[letter] || "";
}

function renderSignInstructions(textEl, letter){
  if(!textEl) return;
  const box = textEl.closest(".sign-instructions");
  const description = signDescription(letter);
  if(box){
    const title = box.querySelector(".sign-instructions-title");
    if(title) title.textContent = tr("howToSign", signLanguageName());
    box.classList.toggle("hidden", !description);
  }
  textEl.textContent = description;
}

// ===== Texto a voz (sin dependencias nuevas) =====
// 1) Web Speech API de WebView2 (voces "OneCore" de Windows).
// 2) Si WebView2 no tiene voz del idioma, el backend usa las voces SAPI de
//    escritorio de Windows (src/speech/text_to_speech.py).
// Si ninguna existe, se informa al usuario en lugar de leer el texto con una
// voz de otro idioma.
const TTS = {
  supported: typeof window !== "undefined" && "speechSynthesis" in window && "SpeechSynthesisUtterance" in window,
  voices: [],
  init(){
    if(!this.supported) return;
    const load = () => { this.voices = window.speechSynthesis.getVoices() || []; };
    load();
    window.speechSynthesis.onvoiceschanged = load;
  },
  normalize(lang){ return String(lang || "").toLowerCase().replace("_", "-"); },
  voiceFor(locale){
    const wanted = this.normalize(locale);
    const base = wanted.split("-")[0];
    return this.voices.find((v) => this.normalize(v.lang) === wanted)
      || this.voices.find((v) => this.normalize(v.lang).split("-")[0] === base)
      || null;
  },
  cancel(){
    if(this.supported) window.speechSynthesis.cancel();
    if(window.pywebview && window.pywebview.api && window.pywebview.api.stop_speaking){
      window.pywebview.api.stop_speaking().catch(() => {});
    }
  },
  // Devuelve "" si se está leyendo, o el mensaje de error para el usuario.
  async speak(text, locale){
    const clean = String(text || "").trim();
    if(!clean) return "";
    this.cancel();
    if(this.supported){
      if(!this.voices.length) this.voices = window.speechSynthesis.getVoices() || [];
      const voice = this.voiceFor(locale);
      if(voice){
        const utterance = new SpeechSynthesisUtterance(clean);
        utterance.lang = voice.lang || locale;
        utterance.voice = voice;
        window.speechSynthesis.speak(utterance);
        return "";
      }
    }
    if(window.pywebview && window.pywebview.api && window.pywebview.api.speak){
      try{
        const res = await window.pywebview.api.speak(clean, locale);
        if(res && res.ok) return "";
        if(res && res.code !== "no_voice") return tr("ttsUnsupported");
      }catch(e){
        return tr("ttsUnsupported");
      }
    }
    return tr("ttsNoVoice", locale);
  },
};
TTS.init();

let ttsToastTimer = null;
function showTtsMessage(message){
  if(ttsError && currentView() === "interaction") ttsError.textContent = message;
  let toast = $("ttsToast");
  if(!toast){
    toast = document.createElement("div");
    toast.id = "ttsToast";
    toast.className = "tts-toast hidden";
    toast.setAttribute("role", "status");
    document.body.appendChild(toast);
  }
  toast.textContent = message;
  toast.classList.toggle("hidden", !message);
  if(ttsToastTimer) clearTimeout(ttsToastTimer);
  if(message) ttsToastTimer = setTimeout(() => toast.classList.add("hidden"), 6000);
}

async function speakText(text, locale){
  showTtsMessage(await TTS.speak(text, locale || languagePack.speech_locale));
}

document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-speak-target]");
  if(!button) return;
  const text = button.dataset.speakTarget.split(",")
    .map((id) => ($(id.trim())?.textContent || "").trim())
    .filter(Boolean)
    .join(". ");
  speakText(text);
});

function letterImageSrc(letter){
  const folder = languagePack.image_folder || LANGUAGE_FALLBACK.es.image_folder;
  return `${folder}/${letter.toLowerCase()}.png`;
}

function showReferenceImage(img, art, letter){
  const placeholder = art.querySelector(".reference-placeholder-text");
  img.onerror = () => {
    img.style.display = "none";
    if(placeholder){
      placeholder.textContent = tr("missingImage", letter);
      placeholder.style.display = "";
    }
  };
  const src = letterImageSrc(letter);
  if(img.getAttribute("src") !== src) img.src = src;
  img.alt = tr("signAlt", letter, signLanguageName());
  img.style.display = "block";
  if(placeholder) placeholder.style.display = "none";
}

// ===== Avance automatico (Aprendizaje y Repaso) =====
// Al confirmar la seña correcta se muestra "Correcto" y, tras este tiempo, se
// pasa a la letra siguiente. El Reto hace lo mismo en el backend.
const AUTO_ADVANCE_DELAY_MS = 1000;
// Letras que el modelo del idioma activo puede reconocer (las envía el backend
// en cada get_state). null = todavía no se conocen.
let recognizableLetters = null;

function isRecognizable(letter){
  return !recognizableLetters || recognizableLetters.includes(letter);
}

// Avisa cuando el modelo del idioma todavía no reconoce la letra: en ese caso
// el avance es manual (botón Siguiente) y nunca se simula una detección.
function renderLetterNotice(el, letter){
  if(!el) return;
  const missing = !!letter && !isRecognizable(letter);
  el.classList.toggle("hidden", !missing);
  el.textContent = missing ? tr("letterNotRecognized", letter, signLanguageName()) : "";
}

// ===== Pregunta de la IA tras varios errores (Aprendizaje, Repaso y Reto) =====
// Tras ERRORS_TO_PROMPT intentos equivocados en la misma letra, la IA ofrece
// guardarla para Repaso y deja elegir entre seguir con ella o pasar a la
// siguiente. Mientras la pregunta está abierta la detección queda en pausa.
const ERRORS_TO_PROMPT = 4;
const errorPrompts = [];

function createErrorPrompt(prefix, { onKeep, onNext }){
  const root = $(`${prefix}ErrorPrompt`);
  const message = $(`${prefix}ErrorPromptMessage`);
  const status = $(`${prefix}ErrorPromptStatus`);
  const saveBtn = $(`${prefix}ErrorPromptSave`);
  const prompt = {
    open: false,
    letter: null,
    errors: 0,
    render(){
      const saved = favoriteLetters.has(this.letter);
      message.textContent = saved
        ? tr("errorPromptAlreadySaved", this.letter, this.errors)
        : tr("errorPromptMessage", this.letter, this.errors);
      saveBtn.textContent = saved ? tr("errorPromptSaved") : tr("errorPromptSave");
      saveBtn.disabled = saved;
      saveBtn.setAttribute("aria-pressed", saved ? "true" : "false");
    },
    show(letter, errors){
      this.open = true;
      this.letter = letter;
      this.errors = errors;
      status.classList.add("hidden");
      status.textContent = "";
      this.render();
      root.classList.remove("hidden");
    },
    hide(){
      this.open = false;
      root.classList.add("hidden");
    },
    // Solo agrega la letra a Repaso (nunca la quita) y confirma con el backend.
    async save(){
      const letter = this.letter;
      saveBtn.disabled = true;
      let saved = false;
      try{
        const result = await window.pywebview.api.set_favorite_letter(letter, true);
        if(result && result.ok){
          favoriteLetters = new Set(result.letters || []);
          saved = favoriteLetters.has(letter);
          updateDifficultCount();
          updateStarButton(learningTargetLetter);
          updateAssistantFavoriteButton(learningTargetLetter);
        }
      }catch(e){
        saved = false;
      }
      if(!this.open || this.letter !== letter) return;
      this.render();
      status.classList.toggle("hidden", saved);
      status.textContent = saved ? "" : tr("errorPromptSaveFailed");
    },
  };
  saveBtn.onclick = () => prompt.save();
  $(`${prefix}ErrorPromptKeep`).onclick = onKeep;
  $(`${prefix}ErrorPromptNext`).onclick = onNext;
  errorPrompts.push(prompt);
  return prompt;
}

// Los favoritos cambiaron (estrella, asistente, otro módulo): actualiza el texto.
function refreshOpenErrorPrompts(){
  errorPrompts.forEach((p) => { if(p.open) p.render(); });
}

// --- Favoritos del usuario autenticado (separados por idioma) ---
let favoriteLetters = new Set();
let favoriteUsername = null;

function updateDifficultCount(){
  if(learningDifficultCount){
    learningDifficultCount.textContent = tr("favoritesCount", favoriteLetters.size);
  }
}

function updateStarButton(letter){
  const isStarred = favoriteLetters.has(letter);
  if(btnStarLetter){
    btnStarLetter.classList.toggle("starred", isStarred);
    btnStarLetter.setAttribute("aria-pressed", isStarred ? "true" : "false");
    btnStarLetter.title = isStarred ? tr("removeFavorite") : tr("saveFavorite");
    btnStarLetter.setAttribute("aria-label", isStarred ? tr("removeFavoriteAria") : tr("saveFavoriteAria"));
  }
  if(starIcon){
    starIcon.textContent = isStarred ? "★" : "☆";
  }
}

function updateAssistantFavoriteButton(letter){
  if(!btnAssistantFavorite) return;
  const isFavorite = favoriteLetters.has(letter);
  btnAssistantFavorite.textContent = isFavorite ? tr("assistantFavRemove") : tr("assistantFavSave");
  btnAssistantFavorite.setAttribute("aria-pressed", isFavorite ? "true" : "false");
}

function updateRepasoUnstarButton(){
  if(!btnUnstarRepaso) return;
  btnUnstarRepaso.title = tr("removeFavorite");
  btnUnstarRepaso.setAttribute("aria-label", tr("removeFavoriteAria"));
}

async function refreshFavoriteLetters(){
  try{
    const result = await window.pywebview.api.get_favorite_letters();
    if(!result || !result.ok) return;
    // Ignora respuestas de un idioma anterior (cambio de idioma en curso).
    if(result.language && result.language !== currentLearningLanguage) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    updateStarButton(learningTargetLetter);
    updateAssistantFavoriteButton(learningTargetLetter);
    refreshOpenErrorPrompts();
    if(currentView() === "repaso") syncRepasoView();
  }catch(e){
    // Conserva los favoritos ya cargados si la consulta falla.
  }
}

async function toggleFavoriteLetter(letter){
  if(!letter) return;
  const target = letter.toUpperCase();
  const isFavorite = !favoriteLetters.has(target);
  try{
    const result = await window.pywebview.api.set_favorite_letter(target, isFavorite);
    if(!result || !result.ok) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    updateStarButton(target);
    updateAssistantFavoriteButton(target);
    refreshOpenErrorPrompts();
    if(currentView() === "repaso") syncRepasoView();
  }catch(e){
    // No cambia la UI si el guardado no fue confirmado por el backend.
  }
}

// --- Vista de Repaso (practica solo las letras marcadas con estrella) ---
let repasoList = [];
let repasoIndex = 0;
let repasoInitialLetter = null;
let repasoTargetLetter = null;
let repasoSameStreak = 0;
let repasoLastDetected = null;
let repasoIsCorrect = false;
let repasoAttemptLogged = false;
let repasoAwaitingNewAttempt = false;
let repasoResetTimer = null;
let repasoAdvanceTimer = null;
// Letra recién confirmada: se ignora hasta que la mano cambie o se retire.
let repasoReleaseLetter = null;
// Letras acertadas en la ronda actual; al cubrir todas se muestra el final.
let repasoCompletedLetters = new Set();
let repasoCompleted = false;
let repasoErrorCount = 0;
const REPASO_STREAK_TO_CONFIRM = 3;

function buildRepasoList(){
  // Solo letras del alfabeto activo (los favoritos ya vienen separados por idioma).
  repasoList = Array.from(favoriteLetters).filter((l) => LETTERS.includes(l)).sort((a, b) => LETTERS.indexOf(a) - LETTERS.indexOf(b));
  if(repasoIndex >= repasoList.length){
    repasoIndex = 0;
  }
}

function resetRepasoFeedback(){
  if(repasoResetTimer){
    clearTimeout(repasoResetTimer);
    repasoResetTimer = null;
  }
  if(repasoAdvanceTimer){
    clearTimeout(repasoAdvanceTimer);
    repasoAdvanceTimer = null;
  }
  repasoReleaseLetter = null;
  repasoCompleted = false;
  if(repasoComplete) repasoComplete.classList.add("hidden");
  repasoErrorCount = 0;
  repasoPrompt.hide();
  repasoIsCorrect = false;
  repasoAttemptLogged = false;
  repasoAwaitingNewAttempt = false;
  repasoSameStreak = 0;
  repasoLastDetected = null;
  if(repasoVideoWrap){
    repasoVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(repasoOverlay){
    repasoOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    repasoOverlay.textContent = "";
  }
  if(repasoStatusPill){
    repasoStatusPill.className = "learning-status-pill";
    repasoStatusPill.textContent = tr("waitingSign");
  }
  if(repasoCaption){
    repasoCaption.textContent = tr("repeatSign");
  }
  if(repasoDetected){
    repasoDetected.textContent = "-";
  }
  if(repasoAssistantCard){
    repasoAssistantCard.classList.add("hidden");
  }
}

function resetReviewSession(){
  // Descarta el historial temporal de 5 intentos de la IA de Repaso.
  if(window.pywebview && window.pywebview.api && window.pywebview.api.reset_review_attempts){
    window.pywebview.api.reset_review_attempts().catch(() => {});
  }
}

function syncRepasoView(){
  buildRepasoList();
  updateRepasoUnstarButton();

  if(repasoList.length === 0){
    if(repasoEmptyState) repasoEmptyState.classList.remove("hidden");
    if(repasoPracticeWrap) repasoPracticeWrap.classList.add("hidden");
    return;
  }

  if(repasoEmptyState) repasoEmptyState.classList.add("hidden");
  if(repasoPracticeWrap) repasoPracticeWrap.classList.remove("hidden");

  if(repasoInitialLetter){
    const initialIndex = repasoList.indexOf(repasoInitialLetter);
    if(initialIndex >= 0) repasoIndex = initialIndex;
    repasoInitialLetter = null;
  }

  const letterValue = repasoList[repasoIndex];
  if(letterValue !== repasoTargetLetter) resetReviewSession();
  repasoTargetLetter = letterValue;

  if(repasoLetter) repasoLetter.textContent = letterValue;
  if(repasoProgress) repasoProgress.textContent = `${letterValue} — ${repasoIndex + 1}/${repasoList.length}`;

  if(repasoReferenceImage && repasoReferenceArt){
    showReferenceImage(repasoReferenceImage, repasoReferenceArt, letterValue);
  }
  renderSignInstructions($("repasoInstructions"), letterValue);
  renderLetterNotice(repasoNotice, letterValue);

  resetRepasoFeedback();
}

function startRepasoRound(){
  repasoCompletedLetters = new Set();
}

function showRepasoComplete(){
  repasoCompleted = true;
  // La ronda terminó: la siguiente práctica empieza una ronda nueva.
  startRepasoRound();
  if(repasoComplete) repasoComplete.classList.remove("hidden");
  if(repasoCaption) repasoCaption.textContent = tr("repasoCompleteTitle");
}

// Tras ~1 s pasa a la siguiente letra favorita pendiente de la ronda (solo
// letras que el modelo reconoce) o muestra el mensaje de finalización.
function scheduleRepasoAdvance(){
  const confirmed = repasoTargetLetter;
  repasoCompletedLetters.add(confirmed);
  if(repasoAdvanceTimer) clearTimeout(repasoAdvanceTimer);
  repasoAdvanceTimer = setTimeout(() => {
    repasoAdvanceTimer = null;
    if(currentView() !== "repaso" || repasoTargetLetter !== confirmed) return;
    goToNextPendingRepaso(confirmed);
  }, AUTO_ADVANCE_DELAY_MS);
}

// Siguiente letra pendiente de la ronda o, si no queda ninguna, el final.
function goToNextPendingRepaso(releaseLetter){
  const isPending = (l) => !repasoCompletedLetters.has(l) && isRecognizable(l);
  if(!repasoList.some(isPending)){
    showRepasoComplete();
    return;
  }
  for(let step = 1; step <= repasoList.length; step++){
    const i = (repasoIndex + step) % repasoList.length;
    if(isPending(repasoList[i])){
      repasoIndex = i;
      break;
    }
  }
  syncRepasoView();
  repasoReleaseLetter = releaseLetter || null;
}

const repasoPrompt = createErrorPrompt("repaso", {
  // El aviso "otro intento" ya exige cambiar la seña antes de contar de nuevo.
  onKeep: () => {
    repasoPrompt.hide();
    repasoErrorCount = 0;
  },
  // La letra pasada cuenta como vista en esta ronda (no como acertada).
  onNext: () => {
    const skipped = repasoTargetLetter;
    repasoPrompt.hide();
    repasoErrorCount = 0;
    repasoCompletedLetters.add(skipped);
    goToNextPendingRepaso(repasoLastDetected !== skipped ? repasoLastDetected : null);
  },
});

function moveRepaso(step){
  if(repasoList.length === 0) return;
  repasoIndex = (repasoIndex + step + repasoList.length) % repasoList.length;
  syncRepasoView();
}

async function openRepasoForLetter(letter){
  const target = (letter || "").trim().toUpperCase();
  if(!target) return;
  try{
    const result = await window.pywebview.api.set_favorite_letter(target, true);
    if(!result || !result.ok) return;
    favoriteLetters = new Set(result.letters || []);
    updateDifficultCount();
    repasoInitialLetter = target;
    repasoIndex = 0;
    startRepasoRound();
    setView("repaso");
    syncRepasoView();
  }catch(e){
    // No navega si la recomendacion no pudo guardarse para el usuario.
  }
}

function renderRepasoFeedback(feedback){
  if(!feedback || !repasoAssistantCard) return;
  // La IA responde en el idioma activo; descarta respuestas de otro idioma.
  if(feedback.language && feedback.language !== currentLearningLanguage) return;
  if(repasoAssistantTitle){
    repasoAssistantTitle.textContent = feedback.correct ? tr("wellDone") : "🤖 " + (feedback.title || tr("checkSign"));
  }
  if(repasoAssistantMessage){
    repasoAssistantMessage.textContent = feedback.message || "";
  }
  if(repasoAssistantTip){
    repasoAssistantTip.textContent = feedback.tip || "";
  }
  repasoAssistantCard.classList.remove("hidden");
}

function showRepasoRetry(attemptNumber, attemptLimit){
  const number = attemptNumber || 1;
  const limit = attemptLimit || 5;
  if(repasoCaption){
    repasoCaption.textContent = tr("attemptMismatch", number, limit);
  }
  if(repasoResetTimer) clearTimeout(repasoResetTimer);
  repasoResetTimer = setTimeout(() => {
    if(currentView() !== "repaso" || repasoIsCorrect) return;
    if(repasoVideoWrap){
      repasoVideoWrap.classList.remove("learning-incorrect");
    }
    if(repasoOverlay){
      repasoOverlay.classList.remove("learning-overlay-incorrect");
      repasoOverlay.textContent = "";
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill";
      repasoStatusPill.textContent = tr("attemptRetry", number, limit);
    }
  }, 850);
}

function logRepasoAttempt(detectedLetter){
  if(repasoAttemptLogged) return;
  repasoAttemptLogged = true;
  const target = repasoTargetLetter;
  window.pywebview.api.review_attempt(target, detectedLetter).then((result) => {
    if(target !== repasoTargetLetter) return;
    if(result && result.ok && result.feedback){
      const details = result.feedback.details || [];
      const isComparativeFeedback = details.includes("attempts_analyzed=5");
      // Los primeros cuatro intentos conservan la indicacion corta de la
      // camara. La explicacion de IA se reserva para la comparacion final.
      if(isComparativeFeedback || result.feedback.correct){
        renderRepasoFeedback(result.feedback);
      }
      if(detectedLetter !== target){
        repasoAttemptLogged = false;
        repasoAwaitingNewAttempt = true;
        showRepasoRetry(result.review_attempt, result.review_attempt_limit);
        repasoErrorCount += 1;
        if(repasoErrorCount === ERRORS_TO_PROMPT) repasoPrompt.show(target, repasoErrorCount);
      }
    }else{
      repasoAttemptLogged = false;
    }
  }).catch(() => {
    repasoAttemptLogged = false;
  });
}

function updateRepasoFeedback(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim()) ? String(detectedLetterRaw).trim().toUpperCase() : null;
  if(repasoDetected){
    repasoDetected.textContent = detected || "-";
  }
  if(!repasoTargetLetter) return;
  // Avance en curso, ronda terminada o pregunta de la IA abierta:
  // ninguna detección cuenta como intento.
  if(repasoAdvanceTimer || repasoCompleted || repasoPrompt.open) return;

  if(!detected){
    repasoSameStreak = 0;
    repasoLastDetected = null;
    repasoAwaitingNewAttempt = false;
    repasoReleaseLetter = null;
    return;
  }

  // La seña recién confirmada sigue en cámara: no es un intento de la letra nueva.
  if(repasoReleaseLetter){
    if(detected === repasoReleaseLetter) return;
    repasoReleaseLetter = null;
  }

  // Tras un error, exigir que el usuario cambie o retire la mano antes de
  // confirmar otro intento. Asi una misma seña sostenida no suma intentos
  // repetidos en cada frame.
  if(repasoAwaitingNewAttempt && detected === repasoLastDetected){
    return;
  }
  if(repasoAwaitingNewAttempt){
    repasoAwaitingNewAttempt = false;
  }

  if(detected === repasoLastDetected){
    repasoSameStreak += 1;
  }else{
    repasoSameStreak = 1;
    repasoLastDetected = detected;
  }

  const isMatch = (detected === repasoTargetLetter);

  if(isMatch && repasoSameStreak >= REPASO_STREAK_TO_CONFIRM){
    if(repasoResetTimer){
      clearTimeout(repasoResetTimer);
      repasoResetTimer = null;
    }
    if(!repasoIsCorrect){
      repasoIsCorrect = true;
      logRepasoAttempt(detected);
      scheduleRepasoAdvance();
    }
    if(repasoVideoWrap){
      repasoVideoWrap.classList.add("learning-correct");
      repasoVideoWrap.classList.remove("learning-incorrect");
    }
    if(repasoOverlay){
      repasoOverlay.classList.add("learning-overlay-correct");
      repasoOverlay.classList.remove("learning-overlay-incorrect");
      repasoOverlay.textContent = tr("correct");
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill learning-status-correct";
      repasoStatusPill.textContent = tr("correctExcl");
    }
    if(repasoCaption){
      const morePending = repasoList.some((l) => l !== repasoTargetLetter && !repasoCompletedLetters.has(l) && isRecognizable(l));
      repasoCaption.textContent = morePending ? tr("correctAdvancing") : tr("correctExcl");
    }
  }else if(!isMatch && repasoSameStreak >= REPASO_STREAK_TO_CONFIRM){
    repasoIsCorrect = false;
    logRepasoAttempt(detected);
    if(repasoVideoWrap){
      repasoVideoWrap.classList.add("learning-incorrect");
      repasoVideoWrap.classList.remove("learning-correct");
    }
    if(repasoOverlay){
      repasoOverlay.classList.add("learning-overlay-incorrect");
      repasoOverlay.classList.remove("learning-overlay-correct");
      repasoOverlay.textContent = tr("tryAgain");
    }
    if(repasoStatusPill){
      repasoStatusPill.className = "learning-status-pill learning-status-incorrect";
      repasoStatusPill.textContent = tr("detectedIs", detected);
    }
    if(repasoCaption){
      repasoCaption.textContent = tr("lookForSign", repasoTargetLetter);
    }
  }
}

let pollTimer = null;
let recording = false;
let lastLoggedIn = null;
let learningIndex = 0;
let learningTargetLetter = "A";
let learningCorrectCount = 0;
let learningSameStreak = 0;
let learningLastDetected = null;
let learningIsCorrect = false;
let learningAttemptLogged = false;
let learningAnalysis = null;
let learningAdvanceTimer = null;
// Letra recién confirmada: se ignora hasta que la mano cambie o se retire.
let learningReleaseLetter = null;
let learningCompleted = false;
// Errores confirmados en la letra actual; al llegar al limite la IA pregunta
// si se guarda para Repaso y si seguir con la letra o pasar a la siguiente.
let learningErrorCount = 0;
let accessibilitySettingsDirty = false;
let retoMode = "name";
const LEARNING_STREAK_TO_CONFIRM = 3;

function setView(name){
  viewLogin.classList.toggle("hidden", name !== "login");
  viewRegister.classList.toggle("hidden", name !== "register");
  viewRegisterLanguage.classList.toggle("hidden", name !== "register_language");
  viewRegisterAccessibility.classList.toggle("hidden", name !== "register_accessibility");
  viewMenu.classList.toggle("hidden", name !== "menu");
  viewInteraction.classList.toggle("hidden", name !== "interaction");
  viewAprendizaje.classList.toggle("hidden", name !== "aprendizaje");
  viewEvaluacionConfig.classList.toggle("hidden", name !== "evaluacion_config");
  viewEvaluacionRun.classList.toggle("hidden", name !== "evaluacion_run");
  viewEvaluacionResultados.classList.toggle("hidden", name !== "evaluacion_resultados");
  viewEvaluacionHistorial.classList.toggle("hidden", name !== "evaluacion_historial");
  viewSettings.classList.toggle("hidden", name !== "settings");
  if(typeof viewRepaso !== 'undefined') viewRepaso.classList.toggle("hidden", name !== "repaso");
  viewReto.classList.toggle("hidden", name !== "reto");
}

function currentView(){
  if(!viewRegisterAccessibility.classList.contains("hidden")) return "register_accessibility";
  if(!viewRegisterLanguage.classList.contains("hidden")) return "register_language";
  if(typeof viewRepaso !== 'undefined' && !viewRepaso.classList.contains("hidden")) return "repaso";
  if(!viewEvaluacionRun.classList.contains("hidden")) return "evaluacion_run";
  if(!viewEvaluacionConfig.classList.contains("hidden")) return "evaluacion_config";
  if(!viewEvaluacionResultados.classList.contains("hidden")) return "evaluacion_resultados";
  if(!viewEvaluacionHistorial.classList.contains("hidden")) return "evaluacion_historial";
  if(!viewSettings.classList.contains("hidden")) return "settings";
  if(!viewReto.classList.contains("hidden")) return "reto";
  if(!viewAprendizaje.classList.contains("hidden")) return "aprendizaje";
  if(!viewInteraction.classList.contains("hidden")) return "interaction";
  if(!viewMenu.classList.contains("hidden")) return "menu";
  if(!viewRegister.classList.contains("hidden")) return "register";
  return "login";
}

function applyColorBlindMode(enabled, syncControl = true){
  document.body.classList.toggle("color-blind-mode", !!enabled);
  if(syncControl && settingsColorBlindMode){
    settingsColorBlindMode.checked = !!enabled;
  }
}

function applyAccessibleReadingMode(enabled, fontSize = "medium", syncControl = true){
  document.body.classList.toggle("accessible-reading-mode", !!enabled);
  document.body.classList.remove("reading-size-small", "reading-size-medium", "reading-size-large");
  document.body.classList.add(`reading-size-${["small", "medium", "large"].includes(fontSize) ? fontSize : "medium"}`);
  if(syncControl && settingsAccessibleReadingMode){
    settingsAccessibleReadingMode.checked = !!enabled;
  }
  if(syncControl && settingsReadingFontSize){
    settingsReadingFontSize.value = ["small", "medium", "large"].includes(fontSize) ? fontSize : "medium";
  }
}

function applyDyslexiaSpacingMode(enabled, syncControl = true){
  document.body.classList.toggle("dyslexia-spacing-mode", !!enabled);
  if(syncControl && settingsDyslexiaSpacingMode){
    settingsDyslexiaSpacingMode.checked = !!enabled;
  }
}

function applyNightMode(enabled, syncControl = true){
  const isEnabled = !!enabled;
  document.body.classList.toggle("night-mode", isEnabled);
  if(syncControl && settingsNightMode){
    settingsNightMode.checked = isEnabled;
  }
}

function applyAccessibilityPreferences(colorBlindMode, accessibleReadingMode, nightMode, dyslexiaSpacingMode, readingFontSize = "medium", syncControls = true){
  applyColorBlindMode(colorBlindMode, syncControls);
  applyAccessibleReadingMode(accessibleReadingMode, readingFontSize, syncControls);
  applyNightMode(nightMode, syncControls);
  applyDyslexiaSpacingMode(dyslexiaSpacingMode, syncControls);
}

function renderRetoHint(feedback, target){
  const valid = feedback && feedback.target_letter === target && (!feedback.language || feedback.language === currentLearningLanguage);
  retoAiHint.classList.toggle("hidden", !valid);
  if(!valid) return;
  retoAiHintTitle.textContent = feedback.title || "";
  retoAiHintMessage.textContent = feedback.message || "";
  retoAiHintTip.textContent = feedback.tip || "";
}

function renderReto(st){
  const letters = st.challenge_letters || [];
  const idx = st.challenge_index || 0;
  const done = !!st.challenge_done;
  const mode = st.challenge_mode === "word" ? "word" : "name";
  const word = st.challenge_word || "";

  retoTitle.textContent = mode === "word" ? `${tr("retoTitleWord")} ${word}` : tr("retoTitleName");
  const skipped = Array.from(new Set(st.challenge_skipped || [])).filter((c) => c.trim());
  retoSkipped.classList.toggle("hidden", skipped.length === 0);
  retoSkipped.textContent = skipped.length ? tr("retoSkipped", skipped.join(", ")) : "";

  // El backend pausa el reto tras varios errores y espera la decisión.
  const target = letters[idx];
  if(st.challenge_error_prompt && !done && target){
    if(!retoPrompt.open || retoPrompt.letter !== target) retoPrompt.show(target, st.challenge_error_count);
  }else if(retoPrompt.open){
    retoPrompt.hide();
  }

  if(letters.length === 0){
    retoEmpty.textContent = tr("retoEmpty");
    retoEmpty.classList.remove("hidden");
    retoGrid.classList.add("hidden");
    retoWord.classList.add("hidden");
    retoComplete.classList.add("hidden");
    return;
  }
  retoEmpty.classList.add("hidden");
  retoWord.classList.remove("hidden");

  const passed = Array.isArray(st.challenge_passed) ? st.challenge_passed : [];
  retoWord.innerHTML = "";
  letters.forEach((l, i) => {
    const tile = document.createElement("div");
    let cls = "reto-letter-tile";
    if(passed.includes(i)) cls += " passed";
    else if(i < idx || done) cls += " done";
    else if(i === idx) cls += " current";
    tile.className = cls;
    tile.textContent = l;
    retoWord.appendChild(tile);
  });

  const confirmed = !!st.challenge_confirmed && !done;
  retoVideoWrap.classList.toggle("learning-correct", confirmed);
  retoOverlay.classList.toggle("learning-overlay-correct", confirmed);
  retoOverlay.textContent = confirmed ? tr("correct") : "";

  if(done){
    retoGrid.classList.add("hidden");
    retoComplete.classList.remove("hidden");
    retoSubtitle.textContent = mode === "word" ? tr("wordComplete") : tr("nameComplete");
    retoCompleteText.textContent = mode === "word" ? tr("retoCompleteWord", word) : tr("retoCompleteName");
    const passedLetters = passed.map((i) => letters[i]).filter(Boolean);
    retoCompletePassed.classList.toggle("hidden", passedLetters.length === 0);
    retoCompletePassed.textContent = passedLetters.length ? tr("retoPassedLetters", passedLetters.join(", ")) : "";
    return;
  }

  retoGrid.classList.remove("hidden");
  retoComplete.classList.add("hidden");

  retoLetter.textContent = target;
  showReferenceImage(retoReferenceImage, retoReferenceArt, target);
  renderSignInstructions($("retoInstructions"), target);
  renderRetoHint(st.challenge_feedback, target);
  // El backend confirma la letra y avanza solo ~1 s después.
  retoCaption.textContent = confirmed
    ? (idx === letters.length - 1 ? tr("correctExcl") : tr("correctAdvancing"))
    : tr("retoCaption", target);
  retoSubtitle.textContent = tr("retoLetterOf", idx + 1, letters.length);

  const progress = Math.max(0, Math.min(1, st.challenge_progress || 0));
  retoProgressFill.style.width = (progress * 100) + "%";
}

function renderFrame(frameB64, videoEl, fallbackEl, errorMsg){
  const statusEl = videoEl?.parentElement?.querySelector(".camera-status");
  if(frameB64){
    videoEl.src = "data:image/jpeg;base64," + frameB64;
    videoEl.style.display = "block";
    fallbackEl.style.display = "none";
    if(statusEl){
      statusEl.className = "camera-status camera-status-active";
      statusEl.innerHTML = `<strong>${tr("cameraActive")}</strong><span>${tr("cameraActiveHint")}</span>`;
    }
  }else{
    videoEl.style.display = "none";
    fallbackEl.style.display = "grid";
    const hasCameraError = !!errorMsg;
    fallbackEl.textContent = errorMsg || tr("cameraStarting");
    if(statusEl){
      statusEl.className = `camera-status ${hasCameraError ? "camera-status-error" : "camera-status-loading"}`;
      statusEl.innerHTML = hasCameraError
        ? `<strong>${tr("cameraErrorTitle")}</strong><span>${tr("cameraErrorHint")}</span>`
        : `<strong>${tr("cameraStarting")}</strong><span>${tr("cameraLoadingHint")}</span>`;
    }
  }
}

function resetLearningFeedback(){
  if(learningAdvanceTimer){
    clearTimeout(learningAdvanceTimer);
    learningAdvanceTimer = null;
  }
  learningReleaseLetter = null;
  learningCompleted = false;
  if(learningComplete) learningComplete.classList.add("hidden");
  learningErrorCount = 0;
  learningPrompt.hide();
  learningIsCorrect = false;
  learningAttemptLogged = false;
  learningSameStreak = 0;
  learningLastDetected = null;
  if(learningVideoWrap){
    learningVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(learningOverlay){
    learningOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    learningOverlay.textContent = "";
  }
  if(learningStatusPill){
    learningStatusPill.className = "learning-status-pill";
    learningStatusPill.textContent = tr("waitingSign");
  }
  if(learningCaption){
    learningCaption.textContent = tr("repeatSign");
  }
  if(learningDetected){
    learningDetected.textContent = "-";
  }
}

function logLearningAttempt(detectedLetter){
  if(learningAttemptLogged) return;
  learningAttemptLogged = true;
  window.pywebview.api.learning_attempt(learningTargetLetter, detectedLetter).then((result) => {
    if(result && result.ok && result.analysis){
      renderLearningAssistant(result.analysis, result.letter);
    }
  }).catch(() => {
    learningAttemptLogged = false;
  });
}

function renderLearningAssistant(analysis, letter){
  if(!analysis) return;
  learningAnalysis = analysis;
  learningAssistantLetter.textContent = letter || learningTargetLetter || "-";
  learningAssistantCorrect.textContent = `${analysis.correct}/${analysis.attempts || 5}`;
  learningAssistantAccuracy.textContent = `${analysis.accuracy}%`;
  learningAssistantAttempts.textContent = `${analysis.attempts}/5`;
  learningAssistantMessage.textContent = analysis.message || "";
  learningAssistantRecommendation.textContent = analysis.recommendation === "practice"
    ? tr("recPractice")
    : analysis.recommendation === "optional_practice"
      ? tr("recOptional")
      : analysis.recommendation === "good"
        ? tr("recGood")
        : "";
  updateAssistantFavoriteButton(letter || learningTargetLetter);
}

async function refreshLearningAssistant(letter){
  try{
    const result = await window.pywebview.api.learning_performance(letter);
    if(result && result.ok && result.letter === learningTargetLetter) renderLearningAssistant(result.analysis, result.letter);
  }catch(e){
    // El asistente conserva el ultimo analisis valido si la consulta falla.
  }
}

function syncLearningView(letter, progressText){
  const requested = (letter && letter.trim()) ? letter.trim().toUpperCase() : LETTERS[0];
  const idx = LETTERS.indexOf(requested);
  const finalIndex = idx >= 0 ? idx : 0;
  const letterValue = LETTERS[finalIndex];
  const progressValue = progressText || `${finalIndex + 1}/${LETTERS.length}`;

  learningTargetLetter = letterValue;
  learningLetter.textContent = letterValue;
  learningProgress.textContent = `${letterValue} — ${progressValue}`;

  showReferenceImage(learningReferenceImage, learningReferenceArt, letterValue);
  renderSignInstructions($("learningInstructions"), letterValue);
  renderLetterNotice(learningNotice, letterValue);

  updateStarButton(letterValue);
  updateAssistantFavoriteButton(letterValue);
  resetLearningFeedback();
  if(lastLoggedIn) refreshLearningAssistant(letterValue);
}

// Sigue en la misma letra con un contador de errores nuevo. La seña equivocada
// que siga en camara no cuenta hasta que la mano cambie o se retire.
function keepPracticingLearningLetter(){
  const lastWrong = learningLastDetected;
  learningPrompt.hide();
  learningErrorCount = 0;
  learningSameStreak = 0;
  learningLastDetected = null;
  learningReleaseLetter = lastWrong && lastWrong !== learningTargetLetter ? lastWrong : null;
  if(learningVideoWrap) learningVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  if(learningOverlay){
    learningOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    learningOverlay.textContent = "";
  }
  if(learningStatusPill){
    learningStatusPill.className = "learning-status-pill";
    learningStatusPill.textContent = tr("waitingSign");
  }
  if(learningCaption) learningCaption.textContent = tr("repeatSign");
}

const learningPrompt = createErrorPrompt("learning", {
  onKeep: keepPracticingLearningLetter,
  onNext: () => {
    learningIndex = LETTERS.indexOf(learningTargetLetter);
    moveLearning(1);
  },
});

function isLastLearningLetter(){
  return LETTERS.indexOf(learningTargetLetter) === LETTERS.length - 1;
}

function showLearningComplete(){
  learningCompleted = true;
  if(learningCompleteTitle) learningCompleteTitle.textContent = tr("learningCompleteTitle", signLanguageName());
  if(learningComplete) learningComplete.classList.remove("hidden");
  if(learningCaption) learningCaption.textContent = tr("learningCompleteTitle", signLanguageName());
}

// Tras ~1 s pasa a la letra siguiente (una sola vez por confirmación) o, en la
// última letra del abecedario, muestra el mensaje de finalización.
function scheduleLearningAdvance(){
  const confirmed = learningTargetLetter;
  if(learningAdvanceTimer) clearTimeout(learningAdvanceTimer);
  learningAdvanceTimer = setTimeout(() => {
    learningAdvanceTimer = null;
    if(currentView() !== "aprendizaje" || learningTargetLetter !== confirmed) return;
    if(isLastLearningLetter()){
      showLearningComplete();
      return;
    }
    learningIndex = LETTERS.indexOf(confirmed);
    moveLearning(1);
    learningReleaseLetter = confirmed;
  }, AUTO_ADVANCE_DELAY_MS);
}

function updateLearningFeedback(detectedLetterRaw){
  const detected = (detectedLetterRaw && String(detectedLetterRaw).trim()) ? String(detectedLetterRaw).trim().toUpperCase() : null;
  if(learningDetected){
    learningDetected.textContent = detected || "-";
  }
  // Avance en curso, abecedario terminado o pregunta de la IA abierta:
  // ninguna detección cuenta como intento.
  if(learningAdvanceTimer || learningCompleted || learningPrompt.open) return;

  if(!detected){
    learningReleaseLetter = null;
    learningSameStreak = 0;
    learningLastDetected = null;
    if(!learningIsCorrect){
      if(learningVideoWrap){
        learningVideoWrap.classList.remove("learning-correct", "learning-incorrect");
      }
      if(learningOverlay){
        learningOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
        learningOverlay.textContent = "";
      }
      if(learningStatusPill){
        learningStatusPill.className = "learning-status-pill";
        learningStatusPill.textContent = tr("waitingSign");
      }
      if(learningCaption){
        learningCaption.textContent = tr("repeatSign");
      }
    }
    return;
  }

  // La seña recién confirmada sigue en cámara: no es un intento de la letra nueva.
  if(learningReleaseLetter){
    if(detected === learningReleaseLetter) return;
    learningReleaseLetter = null;
  }

  if(detected === learningLastDetected){
    learningSameStreak += 1;
  }else{
    learningSameStreak = 1;
    learningLastDetected = detected;
  }

  // ===== INICIO: identifica si la letra es correcta y pinta el marco =====
  const isMatch = (detected === learningTargetLetter);

  if(isMatch && learningSameStreak >= LEARNING_STREAK_TO_CONFIRM){
    if(!learningIsCorrect){
      learningIsCorrect = true;
      learningCorrectCount += 1;
      logLearningAttempt(detected);
      if(learningCounter){
        learningCounter.textContent = tr("correctCount", learningCorrectCount);
      }
      scheduleLearningAdvance();
    }
    if(learningVideoWrap){
      learningVideoWrap.classList.add("learning-correct");
      learningVideoWrap.classList.remove("learning-incorrect");
    }
    if(learningOverlay){
      learningOverlay.classList.add("learning-overlay-correct");
      learningOverlay.classList.remove("learning-overlay-incorrect");
      learningOverlay.textContent = tr("correct");
    }
    if(learningStatusPill){
      learningStatusPill.className = "learning-status-pill learning-status-correct";
      learningStatusPill.textContent = tr("correct");
    }
    if(learningCaption){
      learningCaption.textContent = isLastLearningLetter() ? tr("correctExcl") : tr("correctAdvancing");
    }
  }else if(!isMatch && learningSameStreak >= LEARNING_STREAK_TO_CONFIRM){
    learningIsCorrect = false;
    logLearningAttempt(detected);
    if(learningVideoWrap){
      learningVideoWrap.classList.add("learning-incorrect");
      learningVideoWrap.classList.remove("learning-correct");
    }
    if(learningOverlay){
      learningOverlay.classList.add("learning-overlay-incorrect");
      learningOverlay.classList.remove("learning-overlay-correct");
      learningOverlay.textContent = tr("incorrect");
    }
    if(learningStatusPill){
      learningStatusPill.className = "learning-status-pill learning-status-incorrect";
      learningStatusPill.textContent = tr("incorrectDetected", detected);
    }
    if(learningCaption){
      learningCaption.textContent = tr("lookForSign", learningTargetLetter);
    }
    // Cada intento equivocado cuenta una sola vez: al confirmarse (no en cada
    // frame que la misma seña siga en camara).
    if(learningSameStreak === LEARNING_STREAK_TO_CONFIRM){
      learningErrorCount += 1;
      if(learningErrorCount === ERRORS_TO_PROMPT) learningPrompt.show(learningTargetLetter, learningErrorCount);
    }
  }
  // ===== FIN: identifica si la letra es correcta y pinta el marco =====
}

// ===== Chat de interacción =====
// Cada mensaje guarda su tipo ("voice" | "signs") y el idioma en que se dijo:
// la etiqueta se muestra en el idioma activo y "Escuchar" usa la voz del idioma del mensaje.
let chatMessages = [];

function renderBubble(message){
  const isVoice = message.kind ? message.kind === "voice" : String(message.who || "").includes("voz");
  const div = document.createElement("div");
  div.className = "bubble " + (isVoice ? "me" : "other");
  const head = document.createElement("div");
  head.className = "bubble-head";
  const whoDiv = document.createElement("div");
  whoDiv.className = "who";
  whoDiv.textContent = message.kind === "voice" ? tr("chatVoice") : message.kind === "signs" ? tr("chatSigns") : (message.who || "");
  const speakBtn = document.createElement("button");
  speakBtn.type = "button";
  speakBtn.className = "bubble-speak";
  speakBtn.textContent = "🔊";
  speakBtn.title = tr("speakAria");
  speakBtn.setAttribute("aria-label", tr("speakAria"));
  speakBtn.onclick = () => speakText(message.text, message.speech_locale);
  head.appendChild(whoDiv);
  head.appendChild(speakBtn);
  const txt = document.createElement("div");
  txt.textContent = message.text;
  if(message.speech_locale) txt.lang = message.speech_locale;
  div.appendChild(head);
  div.appendChild(txt);
  chat.appendChild(div);
}

function addBubble(message){
  chatMessages.push(message);
  renderBubble(message);
  chat.scrollTop = chat.scrollHeight;
}

function renderChat(){
  chat.innerHTML = "";
  chatMessages.forEach(renderBubble);
  chat.scrollTop = chat.scrollHeight;
}

function clearChat(){
  chatMessages = [];
  chat.innerHTML = "";
}

function updateVoiceLanguage(){
  if(voiceLanguage) voiceLanguage.textContent = tr("voiceListeningIn", languagePack.speech_locale);
}

function updateRecButton(){
  const btn = $("btnRec");
  btn.textContent = recording ? tr("stop") : tr("record");
  btn.classList.toggle("danger", recording);
  btn.classList.toggle("primary", !recording);
}

async function poll(){
  try{
    const st = await window.pywebview.api.get_state();
    if(!languagePacks[currentLearningLanguage]) loadActiveLanguagePack();
    if(st && st.logged_in){
      btnLogout.classList.remove("hidden");
      if(!accessibilitySettingsDirty){
        applyAccessibilityPreferences(st.color_blind_mode, st.accessible_reading_mode, st.night_mode, st.dyslexia_spacing_mode, st.reading_font_size);
      }
      menuUsername = st.username || "";
      $("menuGreeting").textContent = menuGreetingText();
      if(!learningLanguageSaving) renderLearningLanguage(st.learning_language);
      if(st.username && favoriteUsername !== st.username){
        favoriteUsername = st.username;
        refreshFavoriteLetters();
      }
      if(currentView() === "login" || currentView() === "register"){
        setView("menu");
      }

      if(Array.isArray(st.recognizable_letters) && st.learning_language === currentLearningLanguage){
        recognizableLetters = st.recognizable_letters;
        if(currentView() === "aprendizaje") renderLetterNotice(learningNotice, learningTargetLetter);
        if(currentView() === "repaso") renderLetterNotice(repasoNotice, repasoTargetLetter);
      }

      signText.value = st.sign_text || "";
      letterPill.textContent = tr("letterLabel", st.letter || "-");

      if(currentView() === "aprendizaje"){
        updateLearningFeedback(st.letter);
      }

      renderFrame(st.frame_jpeg_b64, videoInteraction, videoFallbackInteraction, st.camera_error);
      renderFrame(st.frame_jpeg_b64, videoAprendizaje, videoFallbackAprendizaje, st.camera_error);
      renderFrame(st.frame_jpeg_b64, videoReto, videoFallbackReto, st.camera_error);
      if(currentView() === "reto") renderReto(st);

      // Si estamos en modo evaluación, mostrar el estado calculado por backend.
      try{
        if(typeof videoEvaluacion !== 'undefined') renderFrame(st.frame_jpeg_b64, videoEvaluacion, videoFallbackEvaluacion, st.camera_error);
        if(typeof evalDetectedLetter !== 'undefined'){
          evalDetectedLetter.textContent = st.evaluation_detected || st.letter || "-";
          evalRequestedLetter.textContent = st.evaluation_target || "-";
          evalTime.textContent = tr("time", formatTimeSec(st.evaluation_remaining || 0));
          evalScore.textContent = tr("score", st.evaluation_score || 0);
          const currentHits = st.evaluation_hits || 0;
          const currentErrors = st.evaluation_errors || 0;
          if(currentHits > evalLastHits){
            showEvalFeedback(true);
          }else if(currentErrors > evalLastErrors){
            showEvalFeedback(false);
          }
          evalLastHits = currentHits;
          evalLastErrors = currentErrors;
          evalHits.textContent = tr("hitsLabel", currentHits);
          evalErrors.textContent = tr("errorsLabel", currentErrors);
          if(currentView() === "evaluacion_run" && !st.evaluation_active && st.evaluation_duration){
            stopEvaluation();
          }
        }
      }catch(e){}

      // Si estamos en modo Repaso, actualizar video y detección
      try{
        if(typeof videoRepaso !== 'undefined') renderFrame(st.frame_jpeg_b64, videoRepaso, videoFallbackRepaso, st.camera_error);
        if(currentView() === 'repaso') updateRepasoFeedback(st.letter);
      }catch(e){}

      // append new messages
      if(Array.isArray(st.new_messages)){
        for(const m of st.new_messages){
          addBubble(m);
        }
      }

      voiceError.textContent = st.voice_error || "";
    }else{
      btnLogout.classList.add("hidden");
      menuUsername = "";
      // No interrumpir el registro mientras todavía no existe una sesión.
      if(["interaction", "menu", "aprendizaje", "reto", "repaso", "evaluacion_run", "evaluacion_config", "evaluacion_resultados", "evaluacion_historial", "settings"].includes(currentView())){
        setView("login");
      }

      // Solo limpiar campos cuando ocurre transición de logueado -> deslogueado
      if(lastLoggedIn === true){
        $("loginUser").value = "";
        $("loginPass").value = "";
        $("regUser").value = "";
        $("regPass").value = "";
        $("regPass2").value = "";
      }
      favoriteLetters = new Set();
      favoriteUsername = null;
      accessibilitySettingsDirty = false;
      applyColorBlindMode(false);
      applyAccessibleReadingMode(false, "medium");
      applyNightMode(false);
      applyDyslexiaSpacingMode(false);
      updateDifficultCount();
    }
    lastLoggedIn = !!(st && st.logged_in);
  }catch(e){
    // silent
  }
}

function moveLearning(step) {
  learningIndex = (learningIndex + step + LETTERS.length) % LETTERS.length;
  const current = LETTERS[learningIndex];
  syncLearningView(current, `${learningIndex + 1}/${LETTERS.length}`);
}

function startPolling(){
  if(pollTimer) return;
  pollTimer = setInterval(poll, 220);
  poll();
  syncLearningView(LETTERS[learningIndex], `${learningIndex + 1}/${LETTERS.length}`);
}

// Auth
$("btnLogin").onclick = async () => {
  loginError.textContent = "";
  const u = $("loginUser").value.trim();
  const p = $("loginPass").value;
  const res = await window.pywebview.api.login(u, p, currentLearningLanguage);
  if(!res.ok){
    loginError.textContent = res.msg || tr("genericError");
    return;
  }
  accessibilitySettingsDirty = false;
  const state = await window.pywebview.api.get_state();
  if(state && state.logged_in){
    applyAccessibilityPreferences(
      state.color_blind_mode,
      state.accessible_reading_mode,
      state.night_mode,
      state.dyslexia_spacing_mode,
      state.reading_font_size,
    );
    renderLearningLanguage(state.learning_language);
  }
};

// ===== Idioma de aprendizaje =====
let learningLanguageSaving = false;
let menuUsername = "";

function menuGreetingText(){
  return menuUsername ? tr("greetingName", menuUsername) : tr("greeting");
}

// Usado por el indicador de racha (script en index.html).
window.formatStudyStreak = (n) => tr("streak", n);

// Aplica los textos del idioma activo a toda la interfaz.
function applyLanguage(){
  document.documentElement.lang = languagePack.ui_locale || currentLearningLanguage;
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = tr(el.dataset.i18n); });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = tr(el.dataset.i18nPlaceholder); });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => { el.title = tr(el.dataset.i18nTitle); });
  document.querySelectorAll("[data-i18n-aria]").forEach((el) => { el.setAttribute("aria-label", tr(el.dataset.i18nAria)); });
  $("menuLanguageCaption").textContent = tr("caption");
  $("menuGreeting").textContent = menuGreetingText();
  const streak = $("studyStreak");
  const days = parseInt(streak.textContent.replace(/\D+/g, ""), 10) || 0;
  streak.textContent = tr("streak", days);
  updateDifficultCount();
  if(learningCounter) learningCounter.textContent = tr("correctCount", learningCorrectCount);
  updateRepasoUnstarButton();
  updateVoiceLanguage();
  updateRecButton();
  renderChat();
  if(ttsError) ttsError.textContent = "";
}

function renderLearningLanguage(language){
  const code = I18N[language] ? language : "es";
  const input = document.querySelector(`input[name="menuLearningLanguage"][value="${code}"]`);
  if(input && !input.checked) input.checked = true;
  const regInput = document.querySelector(`input[name="regLearningLanguage"][value="${code}"]`);
  if(regInput && !regInput.checked) regInput.checked = true;
  if(code === currentLearningLanguage && document.body.dataset.lang === code) return;
  currentLearningLanguage = code;
  document.body.dataset.lang = code;
  viewMenu.dataset.lang = code;
  viewMenu.lang = code;
  storeUiLanguage(code);
  TTS.cancel();
  showTtsMessage("");
  languagePack = languagePacks[code] || LANGUAGE_FALLBACK[code];
  recognizableLetters = null;
  applyLanguage();
  applySignAlphabet();
  loadActiveLanguagePack();
}

// El perfil completo (instrucciones de cada seña) viene del backend. Se pide
// otra vez si todavía no estaba disponible (p. ej. antes de "pywebviewready").
function loadActiveLanguagePack(){
  const code = currentLearningLanguage;
  if(languagePacks[code] && languagePack === languagePacks[code]) return;
  ensureLanguagePack(code).then((pack) => {
    if(!pack || currentLearningLanguage !== code || languagePack === pack) return;
    languagePack = pack;
    applyLanguage();
    applySignAlphabet();
  });
}
window.addEventListener("pywebviewready", loadActiveLanguagePack);

// Cambia el abecedario, las imágenes y las instrucciones al del idioma elegido
// y descarta el estado que pertenecía al idioma anterior.
function applySignAlphabet(){
  LETTERS = languagePack.learning_alphabet || LANGUAGE_FALLBACK.es.learning_alphabet;
  viewMenu.querySelectorAll(".menu-word-tile").forEach((tile) => {
    const img = tile.querySelector("img");
    const letter = tile.querySelector("b").textContent.trim();
    if(!img) return;
    img.style.visibility = "";
    img.onerror = () => { img.style.visibility = "hidden"; };
    img.src = letterImageSrc(letter);
  });
  if(learningIndex >= LETTERS.length) learningIndex = 0;
  const idx = LETTERS.indexOf(learningTargetLetter);
  if(idx >= 0) learningIndex = idx;
  learningAnalysis = null;
  if(learningAssistantCard) learningAssistantCard.classList.add("hidden");
  syncLearningView(LETTERS[learningIndex], `${learningIndex + 1}/${LETTERS.length}`);
  // Repaso: los favoritos y el historial de 5 intentos son propios de cada idioma.
  repasoIndex = 0;
  repasoTargetLetter = null;
  startRepasoRound();
  resetRepasoFeedback();
  if(lastLoggedIn){
    resetReviewSession();
    refreshFavoriteLetters();
  }
  if(currentView() === "repaso") syncRepasoView();
}

document.querySelectorAll('input[name="menuLearningLanguage"]').forEach((input) => {
  input.addEventListener("change", async () => {
    if(!input.checked) return;
    const switcher = document.querySelector(".lang-switch");
    learningLanguageSaving = true;
    switcher.classList.add("saving");
    try{
      const res = await window.pywebview.api.set_learning_language(input.value);
      if(res && res.ok && res.language_pack) languagePacks[res.learning_language] = res.language_pack;
      renderLearningLanguage(res && res.ok ? res.learning_language : currentLearningLanguage);
    }catch(e){
      renderLearningLanguage(currentLearningLanguage);
    }finally{
      learningLanguageSaving = false;
      switcher.classList.remove("saving");
    }
  });
});

// Registro: al elegir el idioma de aprendizaje, la interfaz cambia de inmediato.
document.querySelectorAll('input[name="regLearningLanguage"]').forEach((input) => {
  input.addEventListener("change", () => {
    if(input.checked) renderLearningLanguage(input.value);
  });
});

$("btnGoRegister").onclick = () => { loginError.textContent=""; setView("register"); };
$("btnGoLogin").onclick = () => { regError.textContent=""; setView("login"); };
$("btnContinueRegister").onclick = () => {
  regError.textContent = "";
  const username = $("regUser").value.trim();
  const password = $("regPass").value;
  const confirmation = $("regPass2").value;
  if(!username || !password || !confirmation){
    regError.textContent = tr("fillAllFields");
    return;
  }
  setView("register_language");
};
$("btnBackLanguage").onclick = () => setView("register");
$("btnContinueLanguage").onclick = () => setView("register_accessibility");
$("btnBackRegister").onclick = () => {
  $("regAccessibilityError").textContent = "";
  setView("register_language");
};
$("btnRegister").onclick = async () => {
  regError.textContent = "";
  $("regAccessibilityError").textContent = "";
  const u = $("regUser").value.trim();
  const p = $("regPass").value;
  const p2 = $("regPass2").value;
  const colorBlindMode = $("regColorBlindMode").checked;
  const accessibleReadingMode = $("regAccessibleReadingMode").checked;
  const dyslexiaSpacingMode = $("regDyslexiaSpacingMode").checked;
  const readingFontSize = regReadingFontSize.value;
  const learningLanguage = document.querySelector('input[name="regLearningLanguage"]:checked')?.value || "es";
  const res = await window.pywebview.api.register(u, p, p2, colorBlindMode, accessibleReadingMode, dyslexiaSpacingMode, readingFontSize, learningLanguage);
  if(!res.ok) {
    $("regAccessibilityError").textContent = res.msg || tr("genericError");
  }
  else{
    // limpiar por seguridad
    $("regPass").value = "";
    $("regPass2").value = "";
    $("regColorBlindMode").checked = false;
    $("regAccessibleReadingMode").checked = false;
    $("regDyslexiaSpacingMode").checked = false;
    regReadingFontSize.value = "medium";
    setView("login");
  }
};

async function logoutAndReset(){
  await window.pywebview.api.logout();
  clearChat();
  TTS.cancel();
  favoriteLetters = new Set();
  favoriteUsername = null;
  setView("login");
}

$("btnLogout").onclick = async () => {
  await logoutAndReset();
  $("loginUser").value = "";
  $("loginPass").value = "";
};

$("btnLogoutMenu").onclick = logoutAndReset;

$("btnOpenSettings").onclick = () => {
  settingsError.textContent = "";
  accessibilitySettingsDirty = false;
  setView("settings");
};
$("btnBackSettings").onclick = () => {
  accessibilitySettingsDirty = false;
  setView("menu");
};
settingsColorBlindMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyColorBlindMode(settingsColorBlindMode.checked, false);
};
settingsAccessibleReadingMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyAccessibleReadingMode(settingsAccessibleReadingMode.checked, settingsReadingFontSize.value, false);
};
settingsReadingFontSize.onchange = () => {
  accessibilitySettingsDirty = true;
  applyAccessibleReadingMode(settingsAccessibleReadingMode.checked, settingsReadingFontSize.value, false);
};
settingsDyslexiaSpacingMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyDyslexiaSpacingMode(settingsDyslexiaSpacingMode.checked, false);
};
settingsNightMode.onchange = () => {
  accessibilitySettingsDirty = true;
  applyNightMode(settingsNightMode.checked, false);
};
btnSaveSettings.onclick = async () => {
  settingsError.textContent = "";
  btnSaveSettings.disabled = true;
  const result = await window.pywebview.api.set_accessibility_preferences(
    settingsColorBlindMode.checked,
    settingsAccessibleReadingMode.checked,
    settingsNightMode.checked,
    settingsDyslexiaSpacingMode.checked,
    settingsReadingFontSize.value,
  );
  btnSaveSettings.disabled = false;
  if(!result || !result.ok){
    settingsError.textContent = result?.msg || tr("saveError");
    btnSaveSettings.disabled = false;
    return;
  }
  accessibilitySettingsDirty = false;
  applyAccessibilityPreferences(result.color_blind_mode, result.accessible_reading_mode, result.night_mode, result.dyslexia_spacing_mode, result.reading_font_size);
  btnSaveSettings.disabled = false;
  setView("menu");
};

$("btnOpenInteraction").onclick = () => {
  updateVoiceLanguage();
  if(ttsError) ttsError.textContent = "";
  setView("interaction");
};
$("btnOpenAprendizaje").onclick = () => {
  learningIndex = 0;
  learningCorrectCount = 0;
  if(learningCounter){
    learningCounter.textContent = tr("correctCount", 0);
  }
  updateDifficultCount();
  syncLearningView(LETTERS[learningIndex], `${learningIndex + 1}/${LETTERS.length}`);
  setView("aprendizaje");
};
// Abrir configuración de Modo Evaluación
$("btnOpenEvaluacion").onclick = () => {
  // reset UI
  const radios = document.getElementsByName('evalDuration');
  for(const r of radios) r.checked = (r.value === '30');
  setView('evaluacion_config');
};

$("btnLearningRestart").onclick = () => {
  learningIndex = 0;
  learningCorrectCount = 0;
  if(learningCounter) learningCounter.textContent = tr("correctCount", 0);
  syncLearningView(LETTERS[0], `1/${LETTERS.length}`);
};
$("btnRepasoRestart").onclick = () => {
  startRepasoRound();
  repasoIndex = 0;
  syncRepasoView();
};
$("btnPrevAprendizaje").onclick = () => moveLearning(-1);
$("btnNextAprendizaje").onclick = () => moveLearning(1);
if(btnStarLetter){
  btnStarLetter.onclick = () => toggleFavoriteLetter(learningTargetLetter);
}
if(btnAssistantFavorite){
  btnAssistantFavorite.onclick = () => toggleFavoriteLetter(learningTargetLetter);
}
if(btnPracticeNow){
  btnPracticeNow.onclick = () => openRepasoForLetter(learningAnalysis && learningAnalysis.letter || learningTargetLetter);
}
$("btnOpenLearningAssistant").onclick = () => learningAssistantCard.classList.toggle("hidden");
$("btnCloseLearningAssistant").onclick = () => learningAssistantCard.classList.add("hidden");

// Repaso
if($("btnOpenRepaso")){
  $("btnOpenRepaso").onclick = () => {
    repasoInitialLetter = null;
    repasoIndex = 0;
    startRepasoRound();
    refreshFavoriteLetters().then(() => syncRepasoView());
    setView("repaso");
  };
}
if($("btnBackRepaso")){
  $("btnBackRepaso").onclick = () => {
    resetReviewSession();
    resetRepasoFeedback();
    repasoTargetLetter = null;
    setView("menu");
  };
}
if($("btnPrevRepaso")){
  $("btnPrevRepaso").onclick = () => moveRepaso(-1);
}
if($("btnNextRepaso")){
  $("btnNextRepaso").onclick = () => moveRepaso(1);
}
if(btnUnstarRepaso){
  btnUnstarRepaso.onclick = async () => {
    if(!repasoTargetLetter) return;
    await toggleFavoriteLetter(repasoTargetLetter);
    // Si la letra actual se quitó de la lista, ajusta el índice antes de re-sincronizar
    if(repasoIndex >= repasoList.length - 1){
      repasoIndex = 0;
    }
    syncRepasoView();
  };
}
if($("btnOpenRepasoAssistant")){
  $("btnOpenRepasoAssistant").onclick = () => repasoAssistantCard.classList.toggle("hidden");
}
if($("btnCloseRepasoAssistant")){
  $("btnCloseRepasoAssistant").onclick = () => repasoAssistantCard.classList.add("hidden");
}

$("btnBackInteraction").onclick = () => {
  if(recording) return;
  TTS.cancel();
  setView("menu");
};
$("btnBackAprendizaje").onclick = () => setView("menu");
$("btnBackEvaluacionRun").onclick = () => {
  requestEvaluationExit();
};

// Evaluación state
let evalTimerId = null;
let evalFeedbackTimeoutId = null;
let evaluationStopPending = false;
let evalLastHits = 0;
let evalLastErrors = 0;
const EVAL_FEEDBACK_DURATION_MS = 1200; // cuánto dura el borde/overlay verde o rojo // frames seguidos iguales para confirmar

function formatTimeSec(s){
  const mm = Math.floor(s/60).toString().padStart(2,'0');
  const ss = (s%60).toString().padStart(2,'0');
  return `${mm}:${ss}`;
}

function clearEvalFeedback(){
  if(evalFeedbackTimeoutId){
    clearTimeout(evalFeedbackTimeoutId);
    evalFeedbackTimeoutId = null;
  }
  if(evalVideoWrap){
    evalVideoWrap.classList.remove("learning-correct", "learning-incorrect");
  }
  if(evalOverlay){
    evalOverlay.classList.remove("learning-overlay-correct", "learning-overlay-incorrect");
    evalOverlay.textContent = "";
  }
}

function showEvalFeedback(isCorrect){
  if(evalFeedbackTimeoutId){
    clearTimeout(evalFeedbackTimeoutId);
  }
  if(evalVideoWrap){
    evalVideoWrap.classList.toggle("learning-correct", isCorrect);
    evalVideoWrap.classList.toggle("learning-incorrect", !isCorrect);
  }
  if(evalOverlay){
    evalOverlay.classList.toggle("learning-overlay-correct", isCorrect);
    evalOverlay.classList.toggle("learning-overlay-incorrect", !isCorrect);
    evalOverlay.textContent = isCorrect ? tr("evalCorrectFeedback") : tr("evalIncorrectFeedback");
  }
  evalFeedbackTimeoutId = setTimeout(clearEvalFeedback, EVAL_FEEDBACK_DURATION_MS);
}

async function startEvaluationWithDuration(seconds){
  const result = await window.pywebview.api.eval_start(seconds);
  if(!result || !result.ok) return;
  evaluationStopPending = false;
  clearEvalFeedback();
  evalRequestedLetter.textContent = result.target_letter || "-";
  evalDetectedLetter.textContent = "-";
  evalTime.textContent = tr("time", formatTimeSec(seconds));
  evalScore.textContent = tr("score", 0);
  evalHits.textContent = tr("hitsLabel", 0);
  evalErrors.textContent = tr("errorsLabel", 0);
  evalLastHits = 0;
  evalLastErrors = 0;
  setView("evaluacion_run");
}

function requestEvaluationExit(){
  if(evalExitConfirm) evalExitConfirm.classList.remove("hidden");
}

function closeEvaluationExitConfirm(){
  if(evalExitConfirm) evalExitConfirm.classList.add("hidden");
}

async function stopEvaluation(showResults = true){
  if(evaluationStopPending) return;
  evaluationStopPending = true;
  let response;
  try{
    response = await window.pywebview.api.eval_stop();
  }catch(e){
    evaluationStopPending = false;
    return;
  }
  if(!response || !response.ok){
    evaluationStopPending = false;
    return;
  }
  if(!showResults){
    evaluationStopPending = false;
    setView("menu");
    return;
  }
  const results = response.results || {};
  saveEvaluationSession(results);
  evalResultScore.textContent = results.score || 0;
  evalResultHits.textContent = results.hits || 0;
  evalResultErrors.textContent = results.errors || 0;
  evalResultDuration.textContent = formatTimeSec(results.elapsed_seconds || results.duration_seconds || 0);
  renderEvaluationLetters(evalResultHitLetters, results.hit_letters, tr("noHits"));
  renderEvaluationLetters(evalResultErrorLetters, results.error_letters, tr("noErrors"));
  evalRequestedLetter.textContent = '-';
  evalDetectedLetter.textContent = '-';
  clearEvalFeedback();
  evaluationStopPending = false;
  setView("evaluacion_resultados");
}

function renderEvaluationLetters(container, letters, emptyText){
  container.innerHTML = "";
  if(!Array.isArray(letters) || letters.length === 0){
    container.textContent = emptyText;
    return;
  }
  letters.forEach((letter) => {
    const pill = document.createElement("span");
    pill.className = "evaluation-letter-pill";
    pill.textContent = letter;
    container.appendChild(pill);
  });
}

function evaluationHistoryKey(){
  const user = favoriteUsername || "guest";
  return `traductor.evaluationHistory.${user}`;
}

function loadAllEvaluationHistory(){
  try{
    const history = JSON.parse(localStorage.getItem(evaluationHistoryKey()) || "[]");
    return Array.isArray(history) ? history : [];
  }catch(e){
    return [];
  }
}

// El historial se muestra por idioma (las sesiones antiguas sin idioma son de LSC).
function loadEvaluationHistory(){
  return loadAllEvaluationHistory().filter((session) => (session.language || "es") === currentLearningLanguage);
}

function saveEvaluationSession(results){
  const session = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
    date: new Date().toISOString(),
    language: currentLearningLanguage,
    duration_seconds: Number(results.duration_seconds || 0),
    score: Number(results.score || 0),
    hits: Number(results.hits || 0),
    errors: Number(results.errors || 0),
    hit_letters: Array.isArray(results.hit_letters) ? results.hit_letters.slice() : [],
    error_letters: Array.isArray(results.error_letters) ? results.error_letters.slice() : []
  };
  const history = [session, ...loadAllEvaluationHistory()];
  try{
    localStorage.setItem(evaluationHistoryKey(), JSON.stringify(history));
  }catch(e){
    // La evaluación y sus resultados siguen disponibles aunque el navegador no permita persistir.
  }
  return session;
}

function formatEvaluationDate(isoDate){
  const date = new Date(isoDate);
  if(Number.isNaN(date.getTime())) return tr("unknownDate");
  return date.toLocaleDateString(languagePack.ui_locale, {day:"2-digit", month:"2-digit", year:"numeric"});
}

function formatEvaluationDateTime(isoDate){
  const date = new Date(isoDate);
  if(Number.isNaN(date.getTime())) return tr("unknownDate");
  return date.toLocaleString(languagePack.ui_locale, {day:"2-digit", month:"2-digit", year:"numeric", hour:"2-digit", minute:"2-digit"});
}

function formatEvaluationDuration(seconds){
  const total = Math.max(0, Number(seconds) || 0);
  if(total < 60) return tr("durationSeconds", total);
  const minutes = Math.floor(total / 60);
  const rest = total % 60;
  return rest ? tr("durationMinSec", minutes, rest) : tr("durationMinutes", minutes);
}

function showEvaluationHistorySession(session){
  if(!session) return;
  evaluationHistoryEmpty.classList.add("hidden");
  evaluationHistorySummary.classList.remove("hidden");
  evaluationHistoryMeta.textContent = `${formatEvaluationDateTime(session.date)} — ${tr("sessionLine", formatEvaluationDuration(session.duration_seconds), session.score, session.hits, session.errors)}`;
  renderEvaluationLetters(historyHitLetters, session.hit_letters, tr("noHits"));
  renderEvaluationLetters(historyErrorLetters, session.error_letters, tr("noErrors"));
  document.querySelectorAll(".evaluation-history-item").forEach((item) => {
    item.classList.toggle("selected", item.dataset.sessionId === session.id);
  });
}

function renderEvaluationHistory(){
  const history = loadEvaluationHistory();
  evaluationHistoryList.innerHTML = "";
  if(history.length === 0){
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = tr("noHistory");
    evaluationHistoryList.appendChild(empty);
    evaluationHistoryEmpty.classList.remove("hidden");
    evaluationHistorySummary.classList.add("hidden");
  }else{
    history.forEach((session) => {
      const item = document.createElement("button");
      item.type = "button";
      item.className = "evaluation-history-item";
      item.dataset.sessionId = session.id;
      const strong = document.createElement("strong");
      strong.textContent = formatEvaluationDate(session.date);
      const span = document.createElement("span");
      span.textContent = tr("sessionLine", formatEvaluationDuration(session.duration_seconds), session.score, session.hits, session.errors);
      item.appendChild(strong);
      item.appendChild(span);
      item.onclick = () => showEvaluationHistorySession(session);
      evaluationHistoryList.appendChild(item);
    });
    showEvaluationHistorySession(history[0]);
  }

  evaluationScoreProgress.innerHTML = "";
  if(history.length === 0){
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = tr("noHistoryProgress");
    evaluationScoreProgress.appendChild(empty);
    return;
  }
  const maxMagnitude = Math.max(1, ...history.map((session) => Math.abs(Number(session.score) || 0)));
  history.slice(0, 12).reverse().forEach((session, index) => {
    const row = document.createElement("div");
    row.className = "evaluation-score-row";
    const width = Math.max(4, Math.round(Math.abs(session.score || 0) / maxMagnitude * 100));
    row.innerHTML = `<span>#${index + 1}</span><div class="evaluation-score-track"><i class="${session.score < 0 ? "negative" : ""}" style="width:${width}%"></i></div><strong>${Number(session.score) || 0}</strong>`;
    evaluationScoreProgress.appendChild(row);
  });
}

// Handlers for evaluation controls
$("btnCancelEvaluation").onclick = () => setView('menu');
$("btnStopEvaluation").onclick = requestEvaluationExit;
btnContinueEvaluation.onclick = closeEvaluationExitConfirm;
btnExitEvaluation.onclick = () => {
  closeEvaluationExitConfirm();
  stopEvaluation(false);
};
$("btnRetryEvaluation").onclick = () => setView("evaluacion_config");
$("btnResultsMenu").onclick = () => setView("menu");
$("btnOpenEvaluacionHistorial").onclick = () => {
  renderEvaluationHistory();
  setView("evaluacion_historial");
};
$("btnBackEvaluacionHistorial").onclick = () => setView("menu");
$("btnStartEvaluation").onclick = () => {
  const radios = document.getElementsByName('evalDuration');
  let val = 30;
  for(const r of radios){ if(r.checked) val = parseInt(r.value); }
  startEvaluationWithDuration(val);
};

// Reto: deletrea tu nombre o una palabra del idioma activo
const retoPrompt = createErrorPrompt("reto", {
  onKeep: async () => {
    await window.pywebview.api.challenge_keep_practicing();
    retoPrompt.hide();
  },
  onNext: async () => {
    await window.pywebview.api.challenge_next_letter();
    retoPrompt.hide();
    const st = await window.pywebview.api.get_state(false);
    if(st && st.logged_in) renderReto(st);
  },
});

async function startReto(mode){
  retoMode = mode === "word" ? "word" : "name";
  retoAiHint.classList.add("hidden");
  await window.pywebview.api.challenge_start(retoMode);
  const st = await window.pywebview.api.get_state(false);
  if(st && st.logged_in) renderReto(st);
}
$("btnOpenReto").onclick = async () => {
  await startReto("name");
  setView("reto");
};
$("btnRetoName").onclick = () => startReto("name");
$("btnRetoWord").onclick = () => startReto("word");
$("btnRetoBack").onclick = async () => {
  await window.pywebview.api.challenge_stop();
  setView("menu");
};
$("btnRetoRetry").onclick = () => startReto(retoMode);
$("btnRetoMenu").onclick = async () => {
  await window.pywebview.api.challenge_stop();
  setView("menu");
};

// Interaction actions
$("btnAccept").onclick = () => window.pywebview.api.sign_accept();
$("btnSpace").onclick = () => window.pywebview.api.sign_space();
$("btnBackspace").onclick = () => window.pywebview.api.sign_backspace();
$("btnClear").onclick = () => window.pywebview.api.sign_clear();
$("btnSendSigns").onclick = () => window.pywebview.api.sign_send();
$("btnSpeakSignText").onclick = () => speakText(signText.value);

$("btnRec").onclick = async () => {
  voiceError.textContent = "";
  if(!recording){
    recording = true;
    updateRecButton();
    await window.pywebview.api.voice_start();
  }else{
    $("btnRec").disabled = true;
    await window.pywebview.api.voice_stop();
    // UI se reactivará cuando backend marque status
    setTimeout(() => {
      $("btnRec").disabled = false;
      recording = false;
      updateRecButton();
    }, 1200);
  }
};

applyNightMode(false);
document.body.dataset.lang = "";
renderLearningLanguage(currentLearningLanguage);
startPolling();
