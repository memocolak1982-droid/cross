"""XRP-Trading-Bot: ruft Marktdaten von KuCoin ab und erzeugt Buy/Sell-Signale.

Der Bot nutzt ausschliesslich die oeffentliche KuCoin-Markt-API (keine API-Keys
noetig) und berechnet technische Indikatoren selbst, damit ausser ``requests``
keine weiteren Abhaengigkeiten benoetigt werden.

WICHTIG: Dies ist ein Analyse-Werkzeug, kein Finanzberater. Die erzeugten
Signale sind keine Anlageempfehlung. Es werden keine echten Orders platziert.
"""

from __future__ import annotations

import argparse
import math
import time
from dataclasses import dataclass

import requests

KUCOIN_API = "https://api.kucoin.com/api/v1/market/candles"

# KuCoin beantwortet Anfragen mit dem Standard-User-Agent von ``requests``
# haeufig mit HTTP 403; ein Browser-aehnlicher Header umgeht das.
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}

# Erlaubte KuCoin-Candle-Typen (Mapping auf eine ungefaehre Dauer in Sekunden).
CANDLE_TYPES: dict[str, int] = {
    "1min": 60,
    "5min": 300,
    "15min": 900,
    "30min": 1800,
    "1hour": 3600,
    "4hour": 14400,
    "1day": 86400,
    "1week": 604800,
}


@dataclass
class Candle:
    """Eine einzelne Kerze (OHLCV) zu einem Zeitpunkt."""

    time: int
    open: float
    close: float
    high: float
    low: float
    volume: float


def fetch_candles(
    symbol: str = "XRP-USDT",
    candle_type: str = "1hour",
    limit: int = 200,
    retries: int = 4,
) -> list[Candle]:
    """Laedt Kerzendaten von KuCoin und gibt sie chronologisch (alt -> neu) zurueck.

    KuCoin liefert maximal 1500 Kerzen und sortiert sie absteigend (neueste
    zuerst); wir drehen die Reihenfolge um, damit die Indikatorberechnung
    natuerlich von alt nach neu laeuft.
    """
    if candle_type not in CANDLE_TYPES:
        raise ValueError(
            f"Ungueltiger candle_type '{candle_type}'. "
            f"Erlaubt: {', '.join(CANDLE_TYPES)}"
        )

    params = {"type": candle_type, "symbol": symbol}
    last_error: Exception | None = None

    for attempt in range(retries):
        try:
            response = requests.get(
                KUCOIN_API, params=params, headers=HTTP_HEADERS, timeout=10
            )
            response.raise_for_status()
            payload = response.json()
            if payload.get("code") != "200000":
                raise RuntimeError(f"KuCoin-Fehler: {payload}")

            rows = payload.get("data") or []
            candles = [
                Candle(
                    time=int(row[0]),
                    open=float(row[1]),
                    close=float(row[2]),
                    high=float(row[3]),
                    low=float(row[4]),
                    volume=float(row[5]),
                )
                for row in rows
            ]
            candles.reverse()  # alt -> neu
            return candles[-limit:]
        except (requests.RequestException, ValueError, RuntimeError) as exc:
            last_error = exc
            if attempt < retries - 1:
                wait = 2 ** (attempt + 1)
                print(f"Abruf fehlgeschlagen ({exc}), neuer Versuch in {wait}s ...")
                time.sleep(wait)

    raise RuntimeError(f"KuCoin-Abruf endgueltig fehlgeschlagen: {last_error}")


def sma(values: list[float], period: int) -> list[float | None]:
    """Einfacher gleitender Durchschnitt; vor dem ersten gueltigen Wert ``None``."""
    result: list[float | None] = []
    window_sum = 0.0
    for i, value in enumerate(values):
        window_sum += value
        if i >= period:
            window_sum -= values[i - period]
        result.append(window_sum / period if i >= period - 1 else None)
    return result


def ema(values: list[float], period: int) -> list[float | None]:
    """Exponentiell gewichteter gleitender Durchschnitt."""
    result: list[float | None] = []
    multiplier = 2 / (period + 1)
    prev: float | None = None
    for i, value in enumerate(values):
        if i < period - 1:
            result.append(None)
        elif i == period - 1:
            prev = sum(values[: i + 1]) / period
            result.append(prev)
        else:
            assert prev is not None
            prev = (value - prev) * multiplier + prev
            result.append(prev)
    return result


def rsi(closes: list[float], period: int = 14) -> list[float | None]:
    """Relative Strength Index nach Wilders Glaettung."""
    result: list[float | None] = [None] * len(closes)
    if len(closes) <= period:
        return result

    gains = 0.0
    losses = 0.0
    for i in range(1, period + 1):
        change = closes[i] - closes[i - 1]
        gains += max(change, 0.0)
        losses += max(-change, 0.0)
    avg_gain = gains / period
    avg_loss = losses / period
    result[period] = _rsi_from(avg_gain, avg_loss)

    for i in range(period + 1, len(closes)):
        change = closes[i] - closes[i - 1]
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        result[i] = _rsi_from(avg_gain, avg_loss)

    return result


def _rsi_from(avg_gain: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def macd(
    closes: list[float],
    fast: int = 12,
    slow: int = 26,
    signal_period: int = 9,
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    """MACD-Linie, Signallinie und Histogramm."""
    fast_ema = ema(closes, fast)
    slow_ema = ema(closes, slow)

    macd_line: list[float | None] = [
        (f - s) if (f is not None and s is not None) else None
        for f, s in zip(fast_ema, slow_ema)
    ]

    valid = [v for v in macd_line if v is not None]
    signal_valid = ema(valid, signal_period)

    signal_line: list[float | None] = [None] * len(macd_line)
    j = 0
    for i, value in enumerate(macd_line):
        if value is not None:
            signal_line[i] = signal_valid[j]
            j += 1

    histogram: list[float | None] = [
        (m - s) if (m is not None and s is not None) else None
        for m, s in zip(macd_line, signal_line)
    ]
    return macd_line, signal_line, histogram


def bollinger_bands(
    closes: list[float],
    period: int = 20,
    num_std: float = 2.0,
) -> tuple[list[float | None], list[float | None], list[float | None]]:
    """Bollinger-Baender: oberes Band, Mittellinie (SMA), unteres Band."""
    middle = sma(closes, period)
    upper: list[float | None] = []
    lower: list[float | None] = []
    for i in range(len(closes)):
        if i < period - 1:
            upper.append(None)
            lower.append(None)
            continue
        window = closes[i - period + 1 : i + 1]
        mean = middle[i]
        assert mean is not None
        variance = sum((x - mean) ** 2 for x in window) / period
        std = variance ** 0.5
        upper.append(mean + num_std * std)
        lower.append(mean - num_std * std)
    return upper, middle, lower


# Mindestanzahl Kerzen fuer eine verlaessliche Analyse (laengster Indikator
# ist der MACD mit 26+9 Perioden).
MIN_CANDLES = 35

# Anzahl der stimmberechtigten Indikatoren -> maximaler Betrag des Scores.
MAX_SCORE = 4

# Steilheit der Logistik-Funktion, die den Score in eine Wahrscheinlichkeit
# uebersetzt. Score 0 -> 50 %, Score +-2 -> ~86 %, Score +-4 -> ~97 %.
PROB_STEEPNESS = 0.9


@dataclass
class Indicators:
    """Vollstaendige Indikator-Zeitreihen ueber alle Kerzen."""

    rsi: list[float | None]
    macd_line: list[float | None]
    macd_signal: list[float | None]
    histogram: list[float | None]
    ema_fast: list[float | None]
    ema_slow: list[float | None]
    bb_upper: list[float | None]
    bb_middle: list[float | None]
    bb_lower: list[float | None]


@dataclass
class SignalResult:
    """Ergebnis der Signalauswertung an einer bestimmten Kerze."""

    decision: str  # "BUY", "SELL" oder "HOLD"
    score: int
    price: float
    prob_up: float  # Wahrscheinlichkeit fuer steigende Tendenz (0..1)
    confidence: float  # Wahrscheinlichkeit der getroffenen Entscheidung (0..1)
    reasons: list[str]
    indicators: dict[str, float]


def compute_indicators(closes: list[float]) -> Indicators:
    """Berechnet alle Indikator-Zeitreihen einmalig fuer die Kursreihe."""
    macd_line, macd_signal, histogram = macd(closes)
    bb_upper, bb_middle, bb_lower = bollinger_bands(closes, 20, 2.0)
    return Indicators(
        rsi=rsi(closes, 14),
        macd_line=macd_line,
        macd_signal=macd_signal,
        histogram=histogram,
        ema_fast=ema(closes, 12),
        ema_slow=ema(closes, 26),
        bb_upper=bb_upper,
        bb_middle=bb_middle,
        bb_lower=bb_lower,
    )


def _probability(score: int) -> float:
    """Uebersetzt einen Score in eine Wahrscheinlichkeit fuer steigende Kurse.

    Dies ist eine heuristische Konfidenz aus der Uebereinstimmung der
    Indikatoren - KEINE statistische Vorhersage des Marktes.
    """
    return 1.0 / (1.0 + math.exp(-PROB_STEEPNESS * score))


def _score_at(closes: list[float], ind: Indicators, i: int) -> tuple[int, list[str]]:
    """Bewertet alle Indikatoren an Index ``i`` und gibt Score plus Begruendung.

    Alle vier Indikatoren sind bewusst trendfolgend ausgerichtet, damit sie
    sich nicht widersprechen: ein BUY entsteht nur, wenn Trend und Momentum
    gemeinsam nach oben zeigen - nicht beim Griff ins fallende Messer.
    """
    price = closes[i]
    score = 0
    reasons: list[str] = []

    # 1) Trend: EMA12 ueber/unter EMA26.
    ema_f, ema_s = ind.ema_fast[i], ind.ema_slow[i]
    if ema_f is not None and ema_s is not None:
        if ema_f > ema_s:
            score += 1
            reasons.append("EMA12 > EMA26 (Aufwaertstrend) -> bullisch")
        else:
            score -= 1
            reasons.append("EMA12 < EMA26 (Abwaertstrend) -> baerisch")

    # 2) Momentum: Vorzeichen des MACD-Histogramms.
    hist = ind.histogram[i]
    prev_hist = ind.histogram[i - 1] if i > 0 else None
    if hist is not None:
        crossed_up = prev_hist is not None and prev_hist <= 0 < hist
        crossed_down = prev_hist is not None and prev_hist >= 0 > hist
        if hist > 0:
            score += 1
            reasons.append(
                "MACD kreuzt Signallinie aufwaerts -> bullisch"
                if crossed_up
                else "MACD ueber Signallinie (Momentum positiv) -> bullisch"
            )
        else:
            score -= 1
            reasons.append(
                "MACD kreuzt Signallinie abwaerts -> baerisch"
                if crossed_down
                else "MACD unter Signallinie (Momentum negativ) -> baerisch"
            )

    # 3) Staerke: RSI gegen die 50er-Marke (Momentum-Lesart, nicht kontraer).
    last_rsi = ind.rsi[i]
    if last_rsi is not None:
        if last_rsi >= 55:
            score += 1
            extra = " (ueberkauft - Vorsicht)" if last_rsi > 70 else ""
            reasons.append(
                f"RSI {last_rsi:.1f} > 55 (Aufwaertsmomentum){extra} -> bullisch"
            )
        elif last_rsi <= 45:
            score -= 1
            extra = " (ueberverkauft)" if last_rsi < 30 else ""
            reasons.append(
                f"RSI {last_rsi:.1f} < 45 (Abwaertsmomentum){extra} -> baerisch"
            )
        else:
            reasons.append(f"RSI {last_rsi:.1f} neutral")

    # 4) Lage: Kurs ueber/unter der Bollinger-Mittellinie (SMA20).
    middle = ind.bb_middle[i]
    if middle is not None:
        if price > middle:
            score += 1
            reasons.append("Kurs ueber Bollinger-Mittellinie -> bullisch")
        else:
            score -= 1
            reasons.append("Kurs unter Bollinger-Mittellinie -> baerisch")

    return score, reasons


def _decision_from(score: int) -> str:
    if score >= 2:
        return "BUY"
    if score <= -2:
        return "SELL"
    return "HOLD"


def _result_at(closes: list[float], ind: Indicators, i: int) -> SignalResult:
    """Baut ein vollstaendiges ``SignalResult`` fuer Index ``i``."""
    score, reasons = _score_at(closes, ind, i)
    decision = _decision_from(score)
    prob_up = _probability(score)
    confidence = prob_up if decision == "BUY" else (
        1.0 - prob_up if decision == "SELL" else max(prob_up, 1.0 - prob_up)
    )

    def at(series: list[float | None]) -> float:
        value = series[i]
        return value if value is not None else float("nan")

    indicators = {
        "rsi": at(ind.rsi),
        "macd": at(ind.macd_line),
        "macd_signal": at(ind.macd_signal),
        "ema_fast": at(ind.ema_fast),
        "ema_slow": at(ind.ema_slow),
        "bb_upper": at(ind.bb_upper),
        "bb_middle": at(ind.bb_middle),
        "bb_lower": at(ind.bb_lower),
    }
    return SignalResult(
        decision=decision,
        score=score,
        price=closes[i],
        prob_up=prob_up,
        confidence=confidence,
        reasons=reasons,
        indicators=indicators,
    )


def generate_signal(candles: list[Candle]) -> SignalResult:
    """Wertet RSI, MACD, gleitende Durchschnitte und Bollinger-Baender aus.

    Jeder Indikator vergibt eine Stimme (+1 bullisch, -1 baerisch). Die Summe
    ergibt einen Score; ab +2 lautet die Entscheidung BUY, ab -2 SELL. Der
    Score wird zusaetzlich in eine Wahrscheinlichkeit uebersetzt.
    """
    closes = [c.close for c in candles]
    if len(closes) < MIN_CANDLES:
        raise ValueError(
            f"Zu wenige Kerzen ({len(closes)}) fuer eine verlaessliche Analyse; "
            f"mindestens {MIN_CANDLES} erforderlich."
        )
    ind = compute_indicators(closes)
    return _result_at(closes, ind, len(closes) - 1)


def signal_history(candles: list[Candle]) -> list[SignalResult]:
    """Berechnet das Signal an jeder Kerze (rollierende Auswertung).

    Das Ergebnis hat dieselbe Laenge wie ``candles``; vor genuegend Daten
    enthaelt es ``HOLD`` mit neutraler Wahrscheinlichkeit.
    """
    closes = [c.close for c in candles]
    ind = compute_indicators(closes)
    results: list[SignalResult] = []
    for i in range(len(closes)):
        if i < MIN_CANDLES - 1:
            results.append(
                SignalResult("HOLD", 0, closes[i], 0.5, 0.5, [], {})
            )
        else:
            results.append(_result_at(closes, ind, i))
    return results


# KuCoin-Spot-Handelsgebuehr fuer Standardnutzer (Taker, Stand 2024): 0,1 %.
KUCOIN_FEE_RATE = 0.001


@dataclass
class Trade:
    """Ein einzelner ausgefuehrter Ein- oder Ausstieg im Backtest."""

    index: int
    side: str  # "BUY" oder "SELL"
    price: float
    capital_after: float  # Portfoliowert (Bargeld + Position) nach dem Trade


@dataclass
class BacktestResult:
    """Ergebnis einer Strategiesimulation ueber historische Kerzen."""

    start_capital: float
    final_capital: float
    profit: float
    return_pct: float
    buy_and_hold_pct: float
    num_trades: int
    wins: int
    losses: int
    fee_rate: float
    fees_paid: float
    trades: list[Trade]


def backtest(
    candles: list[Candle],
    start_capital: float = 100.0,
    fee_rate: float = KUCOIN_FEE_RATE,
) -> BacktestResult:
    """Simuliert die Strategie: bei BUY voll einsteigen, bei SELL komplett raus.

    Pro Trade wird die Handelsgebuehr abgezogen. Eine offene Position am Ende
    wird zum letzten Kurs bewertet. Es findet KEIN echter Handel statt - dies
    ist eine Vergangenheitssimulation und keine Gewinnprognose.
    """
    history = signal_history(candles)
    closes = [c.close for c in candles]

    cash = start_capital
    coins = 0.0
    fees_paid = 0.0
    in_position = False
    entry_value = 0.0
    trades: list[Trade] = []
    wins = 0
    losses = 0

    for i, result in enumerate(history):
        price = closes[i]
        if result.decision == "BUY" and not in_position:
            fee = cash * fee_rate
            fees_paid += fee
            coins = (cash - fee) / price
            cash = 0.0
            in_position = True
            entry_value = coins * price
            trades.append(Trade(i, "BUY", price, coins * price))
        elif result.decision == "SELL" and in_position:
            gross = coins * price
            fee = gross * fee_rate
            fees_paid += fee
            cash = gross - fee
            coins = 0.0
            in_position = False
            if cash >= entry_value:
                wins += 1
            else:
                losses += 1
            trades.append(Trade(i, "SELL", price, cash))

    final_capital = cash + coins * closes[-1]
    profit = final_capital - start_capital
    return_pct = profit / start_capital * 100
    buy_and_hold_pct = (closes[-1] / closes[0] - 1) * 100

    return BacktestResult(
        start_capital=start_capital,
        final_capital=final_capital,
        profit=profit,
        return_pct=return_pct,
        buy_and_hold_pct=buy_and_hold_pct,
        num_trades=len(trades),
        wins=wins,
        losses=losses,
        fee_rate=fee_rate,
        fees_paid=fees_paid,
        trades=trades,
    )


def print_backtest(symbol: str, candle_type: str, result: BacktestResult) -> None:
    """Gibt das Backtest-Ergebnis als lesbare Tabelle aus."""
    print("=" * 56)
    print(f"  BACKTEST  {symbol}  |  Intervall: {candle_type}")
    print("=" * 56)
    print(f"  Startkapital     : {result.start_capital:.2f}")
    print(f"  Endkapital       : {result.final_capital:.2f}")
    print(f"  Gewinn / Verlust : {result.profit:+.2f}  ({result.return_pct:+.2f}%)")
    print(f"  Buy & Hold-Ref.  : {result.buy_and_hold_pct:+.2f}%")
    print(f"  Trades           : {result.num_trades} "
          f"(abgeschlossen: {result.wins} Gewinn / {result.losses} Verlust)")
    print(f"  Gebuehren gesamt : {result.fees_paid:.2f} "
          f"(bei {result.fee_rate * 100:.2f}% pro Trade)")
    print("=" * 56)
    print("  ACHTUNG: Simulation auf historischen/synthetischen Daten.")
    print("  Vergangene Ergebnisse sind KEINE Garantie fuer die Zukunft.")
    print("  Es gibt keinen sicheren Gewinn - Trading birgt Verlustrisiko.")


def print_report(symbol: str, candle_type: str, result: SignalResult) -> None:
    """Gibt eine lesbare Zusammenfassung der Analyse aus."""
    print("=" * 56)
    print(f"  {symbol}  |  Intervall: {candle_type}")
    print("=" * 56)
    print(f"  Letzter Kurs : {result.price:.4f} USDT")
    print(f"  RSI(14)      : {result.indicators['rsi']:.2f}")
    print(
        f"  MACD         : {result.indicators['macd']:.5f} "
        f"(Signal {result.indicators['macd_signal']:.5f})"
    )
    print(
        f"  EMA12/EMA26  : {result.indicators['ema_fast']:.4f} / "
        f"{result.indicators['ema_slow']:.4f}"
    )
    print(
        f"  Bollinger    : {result.indicators['bb_lower']:.4f} | "
        f"{result.indicators['bb_middle']:.4f} | "
        f"{result.indicators['bb_upper']:.4f}"
    )
    print("-" * 56)
    for reason in result.reasons:
        print(f"  - {reason}")
    print("-" * 56)
    print(f"  SCORE        : {result.score:+d} (von +-{MAX_SCORE})")
    print(
        f"  Tendenz      : {result.prob_up * 100:.1f}% steigend / "
        f"{(1 - result.prob_up) * 100:.1f}% fallend"
    )
    print(
        f"  >>> SIGNAL   : {result.decision}  "
        f"(Konfidenz {result.confidence * 100:.1f}%)"
    )
    print("=" * 56)
    print("  Hinweis: keine Anlageberatung. Es werden keine Orders platziert.")
    print("  Die Wahrscheinlichkeit ist eine Heuristik aus der Indikator-")
    print("  Uebereinstimmung, keine statistische Marktprognose.")


def _nan(series: list[float | None]) -> list[float]:
    """Ersetzt ``None`` durch ``NaN``, damit matplotlib Luecken sauber zeichnet."""
    return [v if v is not None else float("nan") for v in series]


def _signal_transitions(
    history: list[SignalResult],
) -> tuple[list[tuple[int, SignalResult]], list[tuple[int, SignalResult]]]:
    """Findet die Kerzen, an denen das Signal nach BUY bzw. SELL wechselt."""
    buys: list[tuple[int, SignalResult]] = []
    sells: list[tuple[int, SignalResult]] = []
    previous = "HOLD"
    for i, result in enumerate(history):
        if result.decision in ("BUY", "SELL"):
            if result.decision != previous:
                (buys if result.decision == "BUY" else sells).append((i, result))
            previous = result.decision
    return buys, sells


def plot_chart(
    symbol: str,
    candle_type: str,
    candles: list[Candle],
    output: str = "xrp_signals.png",
) -> str:
    """Zeichnet Kurs, Indikatoren und Buy/Sell-Signale und speichert ein PNG.

    Markiert werden Signalwechsel: ein gruener Pfeil, sobald die Auswertung
    auf BUY kippt, ein roter Pfeil beim Wechsel auf SELL - jeweils mit der
    Konfidenz (Wahrscheinlichkeit) der Entscheidung beschriftet.
    """
    from datetime import datetime

    import matplotlib

    matplotlib.use("Agg")  # kein Display noetig
    import matplotlib.pyplot as plt

    if len(candles) < MIN_CANDLES:
        raise ValueError(
            f"Zu wenige Kerzen ({len(candles)}) fuer einen Chart; "
            f"mindestens {MIN_CANDLES} erforderlich."
        )

    closes = [c.close for c in candles]
    times = [datetime.fromtimestamp(c.time) for c in candles]
    ind = compute_indicators(closes)
    history = signal_history(candles)
    buys, sells = _signal_transitions(history)

    fig, (ax_price, ax_rsi, ax_macd) = plt.subplots(
        3,
        1,
        figsize=(14, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1, 1]},
    )
    last = history[-1]
    fig.suptitle(
        f"{symbol}  -  Intervall {candle_type}  -  "
        f"aktuelles Signal: {last.decision} "
        f"({last.confidence * 100:.0f}% Konfidenz)",
        fontsize=14,
        fontweight="bold",
    )

    # --- Kurs, Bollinger-Baender, EMAs ---
    ax_price.fill_between(
        times,
        _nan(ind.bb_lower),
        _nan(ind.bb_upper),
        color="#b0bec5",
        alpha=0.35,
        label="Bollinger-Baender (20, 2s)",
    )
    ax_price.plot(times, closes, color="#1565c0", lw=1.4, label="Schlusskurs")
    ax_price.plot(
        times, _nan(ind.ema_fast), color="#fb8c00", lw=1.0, label="EMA 12"
    )
    ax_price.plot(
        times, _nan(ind.ema_slow), color="#6a1b9a", lw=1.0, label="EMA 26"
    )

    for i, result in buys:
        ax_price.scatter(
            times[i], closes[i], marker="^", s=170, color="#2e7d32", zorder=5
        )
        ax_price.annotate(
            f"BUY\n{result.confidence * 100:.0f}%",
            (times[i], closes[i]),
            textcoords="offset points",
            xytext=(0, -38),
            ha="center",
            fontsize=8,
            color="#2e7d32",
            fontweight="bold",
        )
    for i, result in sells:
        ax_price.scatter(
            times[i], closes[i], marker="v", s=170, color="#c62828", zorder=5
        )
        ax_price.annotate(
            f"SELL\n{result.confidence * 100:.0f}%",
            (times[i], closes[i]),
            textcoords="offset points",
            xytext=(0, 22),
            ha="center",
            fontsize=8,
            color="#c62828",
            fontweight="bold",
        )

    ax_price.set_ylabel("Preis (USDT)")
    ax_price.legend(loc="upper left", fontsize=8)
    ax_price.grid(alpha=0.3)

    # --- RSI ---
    ax_rsi.plot(times, _nan(ind.rsi), color="#00838f", lw=1.1)
    ax_rsi.axhline(70, color="#c62828", ls="--", lw=0.8)
    ax_rsi.axhline(30, color="#2e7d32", ls="--", lw=0.8)
    ax_rsi.fill_between(times, 70, 100, color="#c62828", alpha=0.08)
    ax_rsi.fill_between(times, 0, 30, color="#2e7d32", alpha=0.08)
    ax_rsi.set_ylabel("RSI (14)")
    ax_rsi.set_ylim(0, 100)
    ax_rsi.grid(alpha=0.3)

    # --- MACD ---
    hist = _nan(ind.histogram)
    colors = ["#2e7d32" if (h == h and h >= 0) else "#c62828" for h in hist]
    ax_macd.bar(times, hist, color=colors, width=0.8 * (
        (times[1] - times[0]) if len(times) > 1 else 1
    ), alpha=0.5)
    ax_macd.plot(times, _nan(ind.macd_line), color="#1565c0", lw=1.0, label="MACD")
    ax_macd.plot(
        times, _nan(ind.macd_signal), color="#fb8c00", lw=1.0, label="Signal"
    )
    ax_macd.axhline(0, color="#777777", lw=0.7)
    ax_macd.set_ylabel("MACD")
    ax_macd.legend(loc="upper left", fontsize=8)
    ax_macd.grid(alpha=0.3)

    fig.autofmt_xdate()
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    fig.savefig(output, dpi=110)
    plt.close(fig)
    return output


def synthetic_candles(count: int = 200, seed: int = 42) -> list[Candle]:
    """Erzeugt nachvollziehbare Pseudo-Kursdaten fuer Demo/Tests ohne Netzwerk."""
    import random

    rng = random.Random(seed)
    price = 2.30
    candles: list[Candle] = []
    now = int(time.time()) - count * 3600
    for i in range(count):
        # sanfter Trend ueberlagert mit Rauschen und einer Welle
        drift = 0.012 * math.sin(i / 18.0)
        price = max(0.05, price * (1 + drift + rng.uniform(-0.012, 0.012)))
        candles.append(
            Candle(
                time=now + i * 3600,
                open=price,
                close=price,
                high=price * 1.004,
                low=price * 0.996,
                volume=rng.uniform(1e6, 5e6),
            )
        )
    return candles


def run_once(
    symbol: str,
    candle_type: str,
    limit: int,
    chart: str | None = None,
    candles: list[Candle] | None = None,
    backtest_capital: float | None = None,
) -> SignalResult:
    """Fuehrt einen einzelnen Abruf-/Analysezyklus aus.

    Wird ``candles`` uebergeben, entfaellt der Netzwerkabruf (Demo-Modus).
    """
    if candles is None:
        candles = fetch_candles(symbol=symbol, candle_type=candle_type, limit=limit)
    result = generate_signal(candles)
    print_report(symbol, candle_type, result)
    if backtest_capital is not None:
        print()
        print_backtest(symbol, candle_type, backtest(candles, backtest_capital))
    if chart:
        path = plot_chart(symbol, candle_type, candles, chart)
        print(f"  Chart gespeichert: {path}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="XRP-Trading-Bot: KuCoin-Daten abrufen und Signale erzeugen."
    )
    parser.add_argument("--symbol", default="XRP-USDT", help="Handelspaar (KuCoin).")
    parser.add_argument(
        "--interval",
        default="1hour",
        choices=sorted(CANDLE_TYPES),
        help="Kerzenintervall.",
    )
    parser.add_argument(
        "--limit", type=int, default=200, help="Anzahl der Kerzen fuer die Analyse."
    )
    parser.add_argument(
        "--watch",
        type=int,
        metavar="SEKUNDEN",
        help="Dauerbetrieb: Analyse alle N Sekunden wiederholen.",
    )
    parser.add_argument(
        "--chart",
        nargs="?",
        const="xrp_signals.png",
        metavar="DATEI",
        help="Chart mit Buy/Sell-Signalen als PNG speichern.",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Synthetische Daten statt KuCoin-Abruf verwenden (ohne Netzwerk).",
    )
    parser.add_argument(
        "--backtest",
        nargs="?",
        type=float,
        const=100.0,
        metavar="KAPITAL",
        help="Strategie ueber die Kerzen simulieren (Standard-Startkapital 100).",
    )
    args = parser.parse_args()

    demo_candles = synthetic_candles(args.limit) if args.demo else None

    if args.watch:
        print(f"Dauerbetrieb aktiv (alle {args.watch}s). Abbruch mit STRG+C.\n")
        try:
            while True:
                run_once(
                    args.symbol, args.interval, args.limit, args.chart,
                    demo_candles, args.backtest,
                )
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nBeendet.")
    else:
        run_once(
            args.symbol, args.interval, args.limit, args.chart,
            demo_candles, args.backtest,
        )


if __name__ == "__main__":
    main()
