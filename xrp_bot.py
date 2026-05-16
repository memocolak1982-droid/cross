"""XRP-Trading-Bot: ruft Marktdaten von KuCoin ab und erzeugt Buy/Sell-Signale.

Der Bot nutzt ausschliesslich die oeffentliche KuCoin-Markt-API (keine API-Keys
noetig) und berechnet technische Indikatoren selbst, damit ausser ``requests``
keine weiteren Abhaengigkeiten benoetigt werden.

WICHTIG: Dies ist ein Analyse-Werkzeug, kein Finanzberater. Die erzeugten
Signale sind keine Anlageempfehlung. Es werden keine echten Orders platziert.
"""

from __future__ import annotations

import argparse
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


@dataclass
class SignalResult:
    """Ergebnis der Signalauswertung fuer die jeweils letzte Kerze."""

    decision: str  # "BUY", "SELL" oder "HOLD"
    score: int
    price: float
    reasons: list[str]
    indicators: dict[str, float]


def generate_signal(candles: list[Candle]) -> SignalResult:
    """Wertet RSI, MACD, gleitende Durchschnitte und Bollinger-Baender aus.

    Jeder Indikator vergibt eine Stimme (+1 bullisch, -1 baerisch). Die Summe
    ergibt einen Score; ab +2 lautet die Entscheidung BUY, ab -2 SELL.
    """
    closes = [c.close for c in candles]
    if len(closes) < 35:
        raise ValueError(
            f"Zu wenige Kerzen ({len(closes)}) fuer eine verlaessliche Analyse; "
            "mindestens 35 erforderlich."
        )

    rsi_values = rsi(closes, 14)
    macd_line, signal_line, histogram = macd(closes)
    ema_fast = ema(closes, 12)
    ema_slow = ema(closes, 26)
    upper, middle, lower = bollinger_bands(closes, 20, 2.0)

    price = closes[-1]
    score = 0
    reasons: list[str] = []

    last_rsi = rsi_values[-1]
    if last_rsi is not None:
        if last_rsi < 30:
            score += 1
            reasons.append(f"RSI {last_rsi:.1f} < 30 (ueberverkauft) -> bullisch")
        elif last_rsi > 70:
            score -= 1
            reasons.append(f"RSI {last_rsi:.1f} > 70 (ueberkauft) -> baerisch")
        else:
            reasons.append(f"RSI {last_rsi:.1f} neutral")

    if histogram[-1] is not None and histogram[-2] is not None:
        if histogram[-2] <= 0 < histogram[-1]:
            score += 1
            reasons.append("MACD kreuzt Signallinie aufwaerts -> bullisch")
        elif histogram[-2] >= 0 > histogram[-1]:
            score -= 1
            reasons.append("MACD kreuzt Signallinie abwaerts -> baerisch")
        elif histogram[-1] > 0:
            reasons.append("MACD ueber Signallinie (Momentum positiv)")
        else:
            reasons.append("MACD unter Signallinie (Momentum negativ)")

    if ema_fast[-1] is not None and ema_slow[-1] is not None:
        if ema_fast[-1] > ema_slow[-1]:
            score += 1
            reasons.append("EMA12 > EMA26 (Aufwaertstrend) -> bullisch")
        else:
            score -= 1
            reasons.append("EMA12 < EMA26 (Abwaertstrend) -> baerisch")

    if upper[-1] is not None and lower[-1] is not None:
        if price <= lower[-1]:
            score += 1
            reasons.append("Kurs am/unter unterem Bollinger-Band -> bullisch")
        elif price >= upper[-1]:
            score -= 1
            reasons.append("Kurs am/ueber oberem Bollinger-Band -> baerisch")
        else:
            reasons.append("Kurs innerhalb der Bollinger-Baender")

    if score >= 2:
        decision = "BUY"
    elif score <= -2:
        decision = "SELL"
    else:
        decision = "HOLD"

    indicators = {
        "rsi": last_rsi if last_rsi is not None else float("nan"),
        "macd": macd_line[-1] if macd_line[-1] is not None else float("nan"),
        "macd_signal": signal_line[-1] if signal_line[-1] is not None else float("nan"),
        "ema_fast": ema_fast[-1] if ema_fast[-1] is not None else float("nan"),
        "ema_slow": ema_slow[-1] if ema_slow[-1] is not None else float("nan"),
        "bb_upper": upper[-1] if upper[-1] is not None else float("nan"),
        "bb_middle": middle[-1] if middle[-1] is not None else float("nan"),
        "bb_lower": lower[-1] if lower[-1] is not None else float("nan"),
    }
    return SignalResult(decision, score, price, reasons, indicators)


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
    print(f"  SCORE        : {result.score:+d}")
    print(f"  >>> SIGNAL   : {result.decision}")
    print("=" * 56)
    print("  Hinweis: keine Anlageberatung. Es werden keine Orders platziert.")


def run_once(symbol: str, candle_type: str, limit: int) -> SignalResult:
    """Fuehrt einen einzelnen Abruf-/Analysezyklus aus."""
    candles = fetch_candles(symbol=symbol, candle_type=candle_type, limit=limit)
    result = generate_signal(candles)
    print_report(symbol, candle_type, result)
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
    args = parser.parse_args()

    if args.watch:
        print(f"Dauerbetrieb aktiv (alle {args.watch}s). Abbruch mit STRG+C.\n")
        try:
            while True:
                run_once(args.symbol, args.interval, args.limit)
                time.sleep(args.watch)
        except KeyboardInterrupt:
            print("\nBeendet.")
    else:
        run_once(args.symbol, args.interval, args.limit)


if __name__ == "__main__":
    main()
