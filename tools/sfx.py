# Synthesises the reel's sound-design track (whooshes, hits, glitches, counters, riser, pulse bed),
# cue-synced to reel.html's timeline.  Usage: python -I sfx.py out.wav
import sys, wave
import numpy as np

SR, DUR = 48000, 48.5
N = int(SR * DUR)
out = np.zeros((N, 2))
rng = np.random.default_rng(11)


def tt(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))


def place(sig, t, gain=1.0, pan=0.0):
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1) * np.sqrt(2)
    i = int(t * SR)
    n = min(len(sig), N - i)
    if n > 0:
        out[i:i + n] += sig[:n] * gain


def filt(x, lo=None, hi=None):
    X = np.fft.rfft(x)
    f = np.maximum(np.fft.rfftfreq(len(x), 1 / SR), 1)
    m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / f) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def sweep_sine(f, amp=1.0):
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * amp


def kick(d=0.45, f0=140, f1=42):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t * 28)) / SR
    return np.sin(ph) * np.exp(-t * 7) + 0.15 * np.sin(ph * 2) * np.exp(-t * 20)


def crack(d=0.12): return filt(noise(d), lo=1500) * np.exp(-tt(d) * 40)


def hit(big=False):
    k = kick(0.9 if big else 0.6, 170, 36)
    c = crack(0.2 if big else 0.12)
    k[:len(c)] += c * (0.7 if big else 0.5)
    return k


def boom(d=2.4):
    t = tt(d)
    sub = sweep_sine(30 + 45 * np.exp(-t * 5)) * np.exp(-t * 1.6)
    return sub + filt(noise(d), hi=380) * np.exp(-t * 3.5) * 0.7


def whoosh(d=0.6, up=True, lo=250, hi=7000):
    t = tt(d); x = t / d; n = noise(d)
    a, b = filt(n, lo=lo, hi=lo * 5), filt(n, lo=hi / 5, hi=hi)
    mix = x if up else 1 - x
    return (a * (1 - mix) + b * mix) * np.sin(np.pi * x) ** 2 * 1.3


def riser(d=2.0):
    t = tt(d); x = t / d
    hiss = filt(noise(d), lo=900) * x ** 2 * 0.5
    tone = sweep_sine(170 * 2 ** (x * 3), 0.28) * x ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * (4 + 22 * x) * t))
    return hiss + tone


def blip(f=1200, d=0.08, harm=0.3):
    t = tt(d); s = np.sin(2 * np.pi * f * t)
    return (s + harm * np.sign(s)) * np.exp(-t * 45) * 0.55


def ticks(d, rate, gain=1.0):
    sig = np.zeros(int(d * SR)); tk = crack(0.02) * 0.6
    for k in range(int(d * rate)):
        i = int(k / rate * SR); n = min(len(tk), len(sig) - i)
        sig[i:i + n] += tk[:n] * (0.7 + 0.3 * rng.random())
    return sig * gain


def glitch(d=0.3):
    sig = np.zeros(int(d * SR)); i = 0
    while i < len(sig):
        seg = int(SR * rng.uniform(0.008, 0.03))
        f = rng.choice([200, 400, 800, 1600, 3200]) * rng.uniform(0.9, 1.1)
        s = np.sign(np.sin(2 * np.pi * f * np.arange(seg) / SR)) * rng.uniform(0.2, 0.7) * (rng.random() > 0.3)
        n = min(seg, len(sig) - i); sig[i:i + n] = s[:n]; i += seg
    return filt(sig, hi=7000) * 0.5


def chime(base=880, d=2.2):
    t = tt(d); s = np.zeros_like(t)
    for k, (m, a) in enumerate([(1, 1), (1.5, 0.6), (2, 0.5), (3, 0.3), (4.02, 0.2)]):
        s += a * np.sin(2 * np.pi * base * m * t + k) * np.exp(-t * (2.0 + k * 0.6))
    return s * 0.35


def rewind(d=0.9):
    t = tt(d)
    ph = 2 * np.pi * np.cumsum(1300 * np.exp(-t * 2.6) + 80) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1) - 1
    trem = 0.6 + 0.4 * np.sign(np.sin(2 * np.pi * (32 - 20 * t / d) * t))
    return filt(saw * trem, hi=5000) * 0.35 * np.minimum(1, (d - t) * 8)


def buzz(d=0.3): t = tt(d); return filt(np.sign(np.sin(2 * np.pi * 92 * t)), hi=2500) * 0.4 * np.exp(-t * 6)


def confirm():
    s = np.zeros(int(0.3 * SR)); a, b = blip(880, 0.09), blip(1320, 0.16)
    s[:len(a)] += a; i = int(0.08 * SR); s[i:i + len(b)] += b
    return s


def hum(d, f=110):
    t = tt(d)
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * f * 2.01 * t)
    return s * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t)) * np.minimum(1, t * 6) * np.minimum(1, (d - t) * 6) * 0.22


def pad(d, freqs, att=0.8, rel=1.2):
    t = tt(d)
    s = sum(np.sin(2 * np.pi * f * t + i) / (1 + i * 0.4) for i, f in enumerate(freqs))
    return s * np.minimum(1, t / att) * np.clip((d - t) / rel, 0, 1) * 0.12


def heartbeat():
    s = np.zeros(int(0.5 * SR)); a, b = kick(0.3, 90, 40) * 0.8, kick(0.3, 80, 38) * 0.6
    s[:len(a)] += a; i = int(0.18 * SR); s[i:i + len(b)] += b
    return s


def hat(): return filt(noise(0.05), lo=7000) * np.exp(-tt(0.05) * 90) * 0.5
def clap(): return filt(noise(0.16), lo=900, hi=5000) * np.exp(-tt(0.16) * 28) * 0.8
def typing(t0, t1, gain=0.5): place(ticks(t1 - t0, 26), t0, gain)
def wh(tc, d=0.6, gain=0.8, up=True): place(whoosh(d, up), tc - d / 2, gain)   # centred on a cut


# No music bed and no pinging "pop" beeps (user feedback on draft v1) — only whooshes, hits,
# glitches, typing/counter ticks and a few textures. The Loan Route and everything from the
# Ballon d'Or ranking onwards stay silent (see SILENT below).
SILENT = [(11.6, 14.45), (38.5, DUR)]

# ── hook ──
place(sweep_sine(np.linspace(80, 900, int(0.32 * SR)), 0.25) * np.linspace(0, 1, int(0.32 * SR)), 0.0)
wh(0.45, 0.6, 0.9)
typing(0.6, 1.2, 0.35)
place(hit(), 0.88, 0.85); place(chime(660), 0.9, 0.45)
place(glitch(0.4), 1.35, 0.35)
place(riser(1.3), 2.2, 0.55)

# ── 01 player scan ──
place(glitch(0.35), 3.35, 0.7); place(hit(True), 3.5, 0.9); place(boom(1.6), 3.5, 0.45)
place(hum(1.5), 3.7); wh(4.4, 1.4, 0.35)
typing(5.1, 5.45, 0.35); wh(5.2, 0.4, 0.4)
wh(6.85, 0.5, 0.4); typing(7.3, 8.2, 0.3)

# ── 02 origins ──
place(glitch(0.3), 8.85, 0.6); place(rewind(0.95), 9.0, 0.8); place(hit(), 9.0, 0.6)
place(hit(), 10.0, 0.7); typing(10.15, 10.7, 0.3)
place(buzz(), 10.35, 0.7)

# ── 03 tottenham ──
place(whoosh(0.5), 14.45, 0.9); place(hit(True), 14.5, 0.75)
typing(14.75, 15.3, 0.3); wh(14.9, 0.4, 0.35)
place(ticks(0.65, 30), 15.35, 0.4)
place(ticks(0.4, 60), 16.4, 0.4); wh(16.6, 0.5, 0.5)
place(ticks(1.2, 30), 16.8, 0.45); place(hit(), 18.0, 0.75)

# ── 04 three lions ──
wh(20.5, 0.6, 0.85); place(hit(True), 20.5, 0.7)
typing(20.7, 21.3, 0.3); place(ticks(0.9, 12), 20.8, 0.6)
place(hit(), 21.6, 0.7); place(chime(880), 21.7, 0.5)
wh(22.6, 0.55, 0.7); typing(22.8, 23.4, 0.25)
place(ticks(1.1, 30), 22.9, 0.45); place(hit(), 24.0, 0.75)

# ── 05 bayern ──
wh(26.5, 0.8, 1.0); place(boom(1.8), 26.5, 0.5); place(hit(True), 26.55, 0.6)
typing(26.7, 27.2, 0.3)
place(hit(True), 27.45, 0.85); typing(27.65, 28.1, 0.3)
place(ticks(0.4, 60), 28.2, 0.4); wh(28.4, 0.5, 0.5)
for tc in [28.6, 28.9, 29.2, 29.5]: place(ticks(0.3, 30), tc, 0.25)

# ── 06 the 73-goal season ──
place(glitch(0.4), 32.3, 0.7); place(hit(True), 32.5, 0.95); place(boom(2.0), 32.5, 0.6)
place(ticks(1.1, 32), 32.7, 0.5); place(hit(True), 33.8, 0.8)
wh(35.5, 0.55, 0.7)
place(hit(), 36.6, 0.7); typing(36.9, 37.4, 0.3)

for a0, a1 in SILENT:
    i0, i1, f = int(a0 * SR), min(N, int(a1 * SR)), int(0.06 * SR)
    out[i0 - f:i0] *= np.linspace(1, 0, f)[:, None]
    out[i0:i1] = 0

# ── master ──
out = np.tanh(out * 1.1)
out *= 0.63 / np.max(np.abs(out))  # ~-4 dBFS: AAC overshoots ~2.4 dB on the glitch/hit transients
pcm = (out * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', sys.argv[1], f'{DUR}s')
