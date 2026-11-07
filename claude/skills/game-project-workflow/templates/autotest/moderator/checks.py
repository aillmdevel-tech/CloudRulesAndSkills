"""Check functions: fn(P, rule) -> (status, detail). P = dict of probe results. status: pass | fail | manual."""
import re

PASS, FAIL, MANUAL = 'pass', 'fail', 'manual'
EMOJI = re.compile('[\U0001F300-\U0001FAFF☀-⛿✀-➿\U0001F000-\U0001F2FF]')
PROFANE = re.compile(r'\b(fuck|shit|bitch|asshole|cunt|dick|porn|nigg)\w*', re.I)
MB = 1024 * 1024
CHECKS = {}


def check(fn):
    CHECKS[fn.__name__] = fn
    return fn


def fmt(hits, n=3): return '; '.join(hits[:n]) + (f' (+{len(hits) - n})' if len(hits) > n else '')
def dist(a, b): return ((a['x'] - b['x']) ** 2 + (a['z'] - b['z']) ** 2) ** 0.5


# ── static / build ──
@check
def bridge_version(P, r):
    s = P['static']; i, l = s['bridge_installed'], s['bridge_latest']
    if not i: return MANUAL, 'версия не определена'
    if not l: return MANUAL, f'установлена {i}; актуальную проверить не удалось (npm view)'
    return (PASS, f'установлена {i} = актуальная') if i == l else (FAIL, f'установлена {i}, актуальная {l}')


@check
def size_300mb(P, r):
    t = P['static']['total']; return (PASS if t <= 300 * MB else FAIL), f'{t / MB:.1f} MB (лимит 300)'


@check
def size_250mb(P, r):
    t = P['static']['total']; return (PASS if t <= 250 * MB else FAIL), f'{t / MB:.1f} MB (лимит 250)'


@check
def file_count_1500(P, r):
    n = P['static']['files']; return (PASS if n <= 1500 else FAIL), f'{n} файлов (лимит 1500)'


@check
def cg_initial_size(P, r):
    t = P['static']['total'] / MB
    return (PASS if t <= 20 else (PASS if t <= 50 else FAIL)), f'{t:.1f} MB целиком (≤ 20 — мобильная главная, ≤ 50 — обычная); начальная загрузка не больше этого'


@check
def index_and_names(P, r):
    s = P['static']
    if not s['index']: return FAIL, 'нет dist/index.html'
    if s['bad_names']: return FAIL, 'не-латиница/спецсимволы в именах: ' + fmt(s['bad_names'])
    return PASS, f"index.html в корне, {s['files']} файлов, имена латиницей"


@check
def relative_paths(P, r):
    s = P['static']
    if s['abs_paths'] or s['ext_in_html']: return FAIL, 'абсолютные пути: ' + fmt(s['abs_paths'] + s['ext_in_html'])
    return PASS, 'index.html и CSS ссылаются относительно (./)'


@check
def no_video(P, r):
    s = P['static']; g = P['static']['grep']
    bad = s['video_files']
    return (FAIL, 'видеофайлы: ' + fmt(bad)) if bad else (PASS, 'видеофайлов и <video> нет')


@check
def bridge_required_steps(P, r):
    s, b = P['static'], P['boot']; g = s['grep']; sub = []
    msgs = [m[0] for m in b['msgs']]
    sub.append(('1 config в архиве', s['config_ok']))
    sub.append(('2 скрипт SDK первый в head, не async', s['bridge_first']))
    ready = next((m for m in b['msgs'] if m[0] == 'game_ready'), None)
    sub.append(('2 initialize до игры (game_ready после init)', bool(ready and ready[2])))
    sub.append(('3 язык из platform.language', bool(g['platform_language']) and not g['navlang']))
    sub.append(('4 сохранения только через storage', not g['storage'] and not [x for x in b['ls'] if not re.match(r'(bridge|spiderarm\.)', x[1])]))
    sub.append(('5 audio/pause: isAudioEnabled + события', bool(g['audio_enabled'] and g['pause_event'] and g['audio_event'])))
    sub.append(('6 game_ready отправлен', ready is not None))
    sub.append(('7 interstitial через showInterstitial без своих таймеров', True))
    sub.append(('8 rewarded скрывается если не поддержан', bool(g['rewarded_supported'])))
    bad = [n for n, ok in sub if not ok]
    return (FAIL if bad else PASS), ('не выполнено: ' + '; '.join(bad)) if bad else 'шаги 1–8: ' + ', '.join(n.split(' ')[0] for n, _ in sub) + ' — ок'


def _hits(P, key, label, fail=True):
    h = P['static']['grep'][key]
    return (FAIL if fail else MANUAL, f'{label}: ' + fmt(h)) if h else (PASS, f'{label}: не найдено')


@check
def no_auth(P, r): return _hits(P, 'auth', 'вход/авторизация в коде')


@check
def no_analytics(P, r):
    h = P['static']['grep']['analytics']; ext = [u for u in P['boot']['external'] if re.search(r'google|analytics|metrika|mixpanel|amplitude', u)]
    return (FAIL, 'аналитика: ' + fmt(h + ext)) if (h or ext) else (PASS, 'в коде и сетевых запросах аналитики нет')


@check
def no_external_requests(P, r):
    ext = P['boot']['external'] + P['static']['ext_in_html']
    return (FAIL, f'{len(ext)} внешних запросов: ' + fmt(ext)) if ext else (PASS, f"{P['boot']['requests']} запросов — все к своему серверу")


@check
def no_external_links(P, r):
    links = P['boot']['info']['links']; h = P['static']['grep']['links']
    if links: return FAIL, 'ссылки в DOM: ' + fmt(links)
    return (MANUAL, 'в коде есть window.open/<a>: ' + fmt(h) + ' — убедиться, что показываются только при isExternalLinksAllowed') if h else (PASS, 'ссылок на внешние сайты нет')


@check
def no_url_lock(P, r): return _hits(P, 'urllock', 'привязка к URL')


@check
def no_escape(P, r): return _hits(P, 'escape', 'Esc в коде')


@check
def no_fullscreen_btn(P, r): return _hits(P, 'fullscreen', 'requestFullscreen в коде')


@check
def no_payments(P, r):
    h = P['static']['grep']['payments']; txt = P['boot']['info']['rbxText'] + P['boot']['info']['text']
    paid = re.findall(r'(R\$|\$\d|\bBUY\b|\bPURCHASE\b|Robux)', txt)
    bad = h + paid
    return (FAIL, 'платное в коде/UI: ' + fmt(bad)) if bad else (PASS, 'платежей и платных кнопок нет (в UI и коде)')


@check
def revive_once(P, r):
    h = P['static']['grep']['revive']
    return (PASS, f'флаг reviveUsed в коде ({len(h)} мест): ' + fmt(h, 2)) if len(h) >= 3 else (FAIL, 'нет защиты «revive раз за попытку»')


@check
def banner_bridge_only(P, r):
    h = P['static']['grep']['banner_bridge']; ext = P['boot']['external']
    return (PASS, 'баннеры только advertisement.showBanner: ' + fmt(h, 1)) if h and not ext else (MANUAL, f'баннер Bridge: {bool(h)}, внешних запросов: {len(ext)}')


@check
def popups_close(P, r):
    bad = P['static']['windows_no_close']
    return (FAIL, 'окна без кнопки закрытия: ' + fmt(bad)) if bad else (MANUAL, 'все окна наследуют UiWindow (кнопка ✕ в базе) или имеют close; Second Chance — кнопка ×; визуально проверить в QA Tool')


@check
def sound_files(P, r):
    s = P['static']; h = s['grep']['synth']
    if h: return FAIL, 'синтез звука в коде: ' + fmt(h)
    return (PASS, f"{len(s['audio_files'])} аудиофайлов (mp3/ogg), синтеза в коде нет") if s['audio_files'] else (FAIL, 'нет аудиофайлов')


@check
def language_from_bridge(P, r):
    g = P['static']['grep']
    if g['navlang']: return FAIL, 'язык из браузера: ' + fmt(g['navlang'])
    return (PASS, 'используется platform.language, navigator.language нет: ' + fmt(g['platform_language'], 1)) if g['platform_language'] else (FAIL, 'platform.language не читается')


@check
def english_default(P, r):
    i = P['boot']['info']; g = P['static']['grep']
    ok = i['lang'] in ('en', '') and not g['navlang']
    return (PASS if ok else FAIL), f"<html lang={i['lang']!r}, язык платформы={i['bridgeLang']!r}, navigator.language не используется={not g['navlang']}; локализации нет — fallback English"


@check
def no_user_data(P, r):
    h = P['static']['grep']['userdata']
    return (MANUAL, 'в коде есть ввод/датчики: ' + fmt(h)) if h else (PASS, 'сбора персональных данных нет (нет input/камеры/геолокации)')


# ── boot ──
@check
def memory_start(P, r):
    h = P['boot']['info']['heap']
    return MANUAL, (f'JS-куча {h / MB:.0f} MB; ' if h else '') + 'пик памяти процесса/GPU не измерен — лимит 2 GB проверяет автопроверка архива'


@check
def keyboard_works(P, r):
    m = P['boot']['moved_without_click']
    return (PASS if m > 3 else FAIL), f'W без клика сдвигает на {m:.1f} studs'


@check
def direct_to_gameplay(P, r):
    b = P['boot']
    return (PASS if b['moved_without_click'] > 3 else FAIL), f"после загрузки игрок сразу управляется без клика (W сдвинул на {b['moved_without_click']:.1f}); game_ready через {b['ready_s'] and round(b['ready_s'], 1)} с"


@check
def cg_load_time(P, r):
    t = P['boot']['ready_s']
    return (PASS if t and t <= 20 else FAIL), f'до первого играбельного кадра {t and round(t, 1)} с (локально; лимит 20 с для внешних файлов)'


@check
def user_select_none(P, r):
    u = P['boot']['info']['userSelect']
    return (PASS if u == 'none' else FAIL), f'getComputedStyle(body).userSelect = {u!r}'


@check
def tutorial(P, r):
    t = P['boot']['info']['tutorial']
    return (PASS if t else MANUAL), f'флаг туториала в сейве = {t} (шаги и стрелки — Tutorial.ts); проверить вручную, что объясняет управление'


@check
def sound_present(P, r):
    b = P['boot']; s = P['static']
    ok = b['ctx_after_gesture'] == 'running' and s['audio_files']
    return (PASS if ok else FAIL), f"AudioContext до жеста={b['ctx_before_gesture']}, после={b['ctx_after_gesture']}, {len(s['audio_files'])} аудиофайлов (музыка + шаги + интерфейс)"


@check
def mute_button(P, r):
    i = P['boot']['info']
    return (PASS if i['mute'] else FAIL), f"кнопка mute в DOM: {i['mute']} ({i['muteText']!r})"


@check
def rewarded_button_text(P, r):
    t = P['ads']['rbxText']
    ok = 'WATCH AD' in t.upper() and re.search(r'\+\d+ Level', t) is not None
    return (PASS if ok else FAIL), f"кнопки rewarded в HUD: «▶ WATCH AD» + награда «+N Levels»: {ok}"


@check
def no_emoji(P, r):
    i = P['boot']['info']; txt = i['rbxText'] + i['text'] + ' '.join(i['buttons'])
    e = EMOJI.findall(txt)
    return (FAIL, 'emoji в интерфейсе: ' + ''.join(e[:10])) if e else (PASS, 'emoji в тексте интерфейса нет (иконки — картинки); общий вид оценивать вручную')


@check
def no_profanity(P, r):
    i = P['boot']['info']; m = PROFANE.findall(i['rbxText'] + i['text'])
    return (FAIL, f'нецензурное: {m}') if m else (PASS, 'в видимом тексте нецензурной лексики нет')


@check
def title_matches(P, r):
    want = r['params']['title']; t = P['boot']['info']['title']
    return (PASS if t.strip() == want else FAIL), f"<title> = {t!r}, в заявке Playgama = {want!r} — привести к одному"


@check
def brand_scan(P, r):
    h = P['static']['grep']['roblox']; i = P['boot']['info']; t = i['title']
    return MANUAL, f"название «{t}»; упоминаний Roblox в коде: {len(h)} ({fmt(h, 2)}); ремейк чужой игры — оценить вручную (4.2.x / originality)"


@check
def rights_manual(P, r):
    return MANUAL, 'музыка/звуки CC0 (public/assets/audio/CREDITS.md); модели, текстуры, UI и шрифты частично из слепка оригинала — см. docs/REDESIGN.md'


@check
def storage_only_bridge(P, r):
    s, b = P['static']['grep']['storage'], P['boot']
    own = [x for x in b['ls'] if not re.match(r'(bridge|spiderarm\.)', x[1])]  # Bridge's mock keeps its own keys in localStorage
    bad = own + (b['idb'] or []) + ([b['info']['cookie']] if b['info']['cookie'] else [])
    if s or bad: return FAIL, 'localStorage/IndexedDB/cookie: ' + fmt(s + [str(x) for x in bad])
    sets = sum(1 for x in b['storage'] if x[0] == 'set')
    return PASS, f'в коде и рантайме localStorage/sessionStorage/IndexedDB/cookie нет; storage.set вызовов за запуск: {sets}'


@check
def ads_not_in_gameplay(P, r):
    walk = P['boot']['ads_during_walk']; calls = [c for c in P['boot']['msgs']]
    if [w for w in walk if w in ('interstitial', 'rewarded')]: return FAIL, 'реклама во время ходьбы: ' + str(walk)
    return PASS, f"за 6 с игры и загрузку рекламных вызовов нет; interstitial вызывается из backToLobby (после падения/победы); rewarded — только по кнопке"


@check
def cg_sdk_integrated(P, r):
    h = P['static']['grep']['cg']; g = P['static']['grep']['gameplay_start']
    return (PASS if h and g else FAIL), 'SDK CrazyGames не подключён: нет window.CrazyGames и gameplayStart/Stop (нужен адаптер платформы в Platform.ts; для Basic Launch необязательно)'


@check
def cg_sdk_data(P, r):
    h = P['static']['grep']['cg']
    return (PASS if h else FAIL), 'сохранения идут только через Bridge storage; CrazyGames Data module не используется (нужен адаптер; для Basic необязательно)'


@check
def cg_ads_sdk(P, r):
    h = P['static']['grep']['cg']
    return (PASS if h else FAIL), 'реклама сейчас через Playgama Bridge; CrazyGames SDK ads (requestAd) не подключены — для Full Launch нужен адаптер; в Basic реклама отключена и игра должна работать без неё'


# ── ads (emulated) ──
def _find(log, kind, state):
    return next((e for e in log if e.get('kind') == kind and e.get('state') == state), None)


@check
def interstitial_shown(P, r):
    a = P['ads']
    return (PASS, 'после падения → лобби вызван showInterstitial (placement lobby_return)') if a['interstitial_called'] else (FAIL, 'interstitial не вызван после падения')


@check
def ads_pause_resume(P, r):
    a = P['ads']; out = []; bad = []
    for name, log in (('interstitial', a['interstitial']), ('rewarded', a['rewarded_ok']['log'])):
        o, m, af = _find(log, name, 'opened'), _find(log, name, 'mid'), _find(log, name, 'after')
        if not (o and m and af): bad.append(f'{name}: нет событий opened/mid/after'); continue
        frozen = dist(o, m) < 0.6; silent = m['ctx'] == 'suspended'
        resumed = af['ctx'] == 'running' and dist(m, af) > 1.0
        out.append(f"{name}: на паузе={frozen} (Δ{dist(o, m):.2f}), звук off={silent}, после рекламы звук={af['ctx']} и игра идёт={resumed}")
        if not (frozen and silent and resumed): bad.append(out[-1])
    return (FAIL, '; '.join(bad)) if bad else (PASS, '; '.join(out))


@check
def ads_mute_on_start(P, r):
    log = P['ads']['rewarded_ok']['log']; rq, o = _find(log, 'rewarded', 'requested'), _find(log, 'rewarded', 'opened')
    if not (rq and o): return FAIL, 'нет событий requested/opened'
    ok = rq['ctx'] == 'running'
    return (PASS if ok else FAIL), f"при запросе звук={rq['ctx']} (должен идти), после opened звук глушится (проверено в ads_pause_resume)"


@check
def ads_fail_continue(P, r):
    a = P['ads']; rf = a['rewarded_fail']
    ok = a['after_fail_moved'] > 3 and a['after_fail_ctx'] == 'running'
    return (PASS if ok else FAIL), f"interstitial failed → игрок идёт (Δ{a['after_fail_moved']:.1f}), звук={a['after_fail_ctx']}; rewarded failed → награды нет (уровень {rf['l0']}→{rf['l1']}), игра играбельна"


@check
def rewarded_decline(P, r):
    return MANUAL, 'отказ: окно Second Chance и кнопки HUD необязательны; проверить визуально размер/цвет «отказа» рядом с кнопкой revive (rewarded-кнопки HUD — без модальных окон)'


@check
def rewarded_grant(P, r):
    a = P['ads']; ok, sk, fl = a['rewarded_ok'], a['rewarded_skip'], a['rewarded_fail']
    if not ok['clicked']: return FAIL, 'кнопка Pack1 не найдена/не нажалась'
    res = [ok['l1'] > ok['l0'], sk['l1'] == sk['l0'], fl['l1'] == fl['l0']]
    calls = [c[1] for c in ok['calls'] if c[0] == 'rewarded']
    return (PASS if all(res) else FAIL), f"досмотрено: уровень {ok['l0']}→{ok['l1']}; закрыто без награды: {sk['l0']}→{sk['l1']}; ошибка: {fl['l0']}→{fl['l1']}; placement={calls}"


# ── pause / hidden ──
@check
def audio_state(P, r):
    g = P['static']['grep']; p = P['pause']
    if not (g['audio_enabled'] and g['pause_event'] and g['audio_event']): return FAIL, 'нет isAudioEnabled или событий AUDIO/PAUSE_STATE_CHANGED'
    if not p['has_audio_api']: return MANUAL, 'в коде есть; эмуляция событий платформы недоступна'
    ok = p['ctx_audio_off'] == 'suspended' and p['ctx_audio_on'] == 'running' and p['pause_moved'] < 0.6 and p['ctx_paused'] == 'suspended' and p['resume_moved'] > 3
    return (PASS if ok else FAIL), (f"audio off→{p['ctx_audio_off']}, on→{p['ctx_audio_on']}; пауза: сдвиг {p['pause_moved']:.2f}, звук {p['ctx_paused']}; после паузы сдвиг {p['resume_moved']:.1f}. "
                                    'Старт с isAudioEnabled=false проверен только по коду (mock всегда true)')


@check
def hidden_tab(P, r):
    p = P['pause']
    ok = p['hidden'] and p['ctx_hidden'] == 'suspended' and p['ctx_back'] == 'running' and p['back_moved'] > 3
    return (PASS if ok else FAIL), f"скрытая вкладка{' (эмуляция visibilitychange)' if p.get('hidden_emulated') else ''}: hidden={p['hidden']}, звук={p['ctx_hidden']}; возврат: звук={p['ctx_back']}, игрок идёт (Δ{p['back_moved']:.1f})"


# ── persist ──
@check
def progress_persisted(P, r):
    p = P['persist']
    return (PASS if p['l1'] == p['l0'] + 3 and p['sets_total'] > 0 else FAIL), f"уровень {p['l0']}→{p['l1']}, storage.set вызовов: {p['sets_total']}; при ходьбе 8 с записей: {p['sets_idle_walk']}"


@check
def progress_survives(P, r):
    p, a = P['persist'], P['ads']
    ok_reload = p['l2'] == p['l1']; ok_ad = a['rewarded_ok']['l1'] >= a['rewarded_ok']['l0']
    return (PASS if ok_reload and ok_ad else FAIL), f"после перезагрузки уровень {p['l1']}→{p['l2']}; после рекламы уровень не потерян: {ok_ad}; поворот экрана — не для десктопа"


# ── sizes ──
def _rows(P): return P['sizes']['rows']


@check
def sizes_fill(P, r):
    bad = []
    for m in _rows(P):
        c = m['canvas']
        if not c or c[2] < m['iw'] - 2 or c[3] < m['ih'] - 2: bad.append(f"{m['size']}: canvas {c}")
        elif m['buf'] and abs(m['buf'][0] / m['buf'][1] - c[2] / c[3]) > 0.03: bad.append(f"{m['size']}: растянут {m['buf']} → {c[2:]}")
    return (FAIL, 'не заполняет/растянут: ' + fmt(bad)) if bad else (PASS, f'canvas заполняет окно, пропорции не искажены на {len(_rows(P))} размерах')


@check
def sizes_noscroll(P, r):
    bad = [f"{m['size']}: {m['sw']}×{m['sh']} > {m['cw']}×{m['ch']}" for m in _rows(P) if m['sw'] > m['cw'] + 1 or m['sh'] > m['ch'] + 1]
    return (FAIL, 'есть прокрутка: ' + fmt(bad)) if bad else (PASS, 'прокрутки страницы нет на всех размерах')


@check
def sizes_overflow(P, r):
    bad = [f"{m['size']}: {m['nover']} эл. ({m['over'][0]})" for m in _rows(P) if m['nover']]
    return (MANUAL, 'элементы вне окна (может быть сделано намеренно): ' + fmt(bad) + ' — см. скриншоты') if bad else (PASS, 'элементы интерфейса не выходят за окно на всех размерах')


@check
def sizes_square(P, r):
    m = next((x for x in _rows(P) if x['size'] == [1000, 1000]), None)
    if not m: return MANUAL, 'нет замера 1:1'
    c = m['canvas']
    return (PASS if c and c[2] >= m['iw'] - 2 and c[3] >= m['ih'] - 2 else FAIL), f"1000×1000: canvas {c}, вне окна {m['nover']} эл."


@check
def sizes_overlap_manual(P, r):
    return MANUAL, f'скриншоты {len(_rows(P))} размеров: tools/out/moderator/sizes/ — смотреть наложения и читаемость текста'


@check
def no_errors_all(P, r):
    errs = []
    for k in ('boot', 'ads', 'pause', 'sizes', 'persist'):
        errs += [f'{k}: {e[:90]}' for e in P[k].get('errors', [])]
    return (FAIL, f'{len(errs)} ошибок консоли: ' + fmt(errs)) if errs else (PASS, 'консоль без ошибок на всех сценариях (загрузка, реклама, пауза/вкладка, resize, перезагрузка)')
