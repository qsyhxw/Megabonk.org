import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const APP_ID = 3405340;
const DATA_PATH = path.resolve("data/player-count.json");
const STEAM_API = `https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=${APP_ID}`;
const STEAM_CHARTS = `https://steamcharts.com/app/${APP_ID}`;

function toNumber(value) {
  if (value === null || typeof value === "undefined" || value === "" || value === "-") return null;
  const parsed = Number(String(value).replace(/[,%+]/g, "").trim());
  return Number.isFinite(parsed) ? parsed : null;
}

function decode(value) {
  return value
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/&#(\d+);/g, (_, code) => String.fromCharCode(Number(code)))
    .replace(/<[^>]*>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

async function getText(url) {
  const response = await fetch(url, {
    headers: {
      "user-agent": "Mozilla/5.0 (compatible; MegabonkPlayerCountBot/1.0; +https://megabonk.org/player-count/)",
      "accept": "text/html,application/json;q=0.9,*/*;q=0.8"
    },
    signal: AbortSignal.timeout(25000)
  });
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.text();
}

export function parseHeadline(html, label) {
  const escaped = label.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const before = new RegExp(`<span[^>]*class=["'][^"']*num[^"']*["'][^>]*>([\\d,]+)<\\/span>(?:\\s|<br[^>]*>)*${escaped}`, "i");
  const after = new RegExp(`${escaped}[\\s\\S]{0,180}?<span[^>]*class=["'][^"']*num[^"']*["'][^>]*>([\\d,]+)<\\/span>`, "i");
  const match = html.match(before) || html.match(after);
  return match ? toNumber(match[1]) : null;
}

export function parseHistory(html) {
  const rows = [];
  for (const match of html.matchAll(/<tr\b[^>]*>([\s\S]*?)<\/tr>/gi)) {
    const cells = [...match[1].matchAll(/<td\b[^>]*>([\s\S]*?)<\/td>/gi)].map((cell) => decode(cell[1]));
    if (cells.length < 5 || !/^(Last 30 Days|[A-Z][a-z]+ \d{4})$/.test(cells[0])) continue;
    const row = {
      period: cells[0],
      average: toNumber(cells[1]),
      gain: toNumber(cells[2]),
      gainPercent: toNumber(cells[3]),
      peak: toNumber(cells[4])
    };
    if (row.average !== null && row.peak !== null) rows.push(row);
  }
  if (rows.length < 3) throw new Error(`Steam Charts history parser found only ${rows.length} valid rows`);
  return rows;
}

async function main() {
  const previous = JSON.parse(await fs.readFile(DATA_PATH, "utf8"));
  const now = new Date().toISOString();

  const steamPayload = JSON.parse(await getText(STEAM_API));
  const currentPlayers = toNumber(steamPayload?.response?.player_count);
  if (!currentPlayers || steamPayload?.response?.result !== 1) throw new Error("Steam API returned an invalid player count");

  let steamCharts = previous.steamCharts;
  try {
    const html = await getText(STEAM_CHARTS);
    const current = parseHeadline(html, "playing");
    const peak24h = parseHeadline(html, "24-hour peak");
    const allTimePeak = parseHeadline(html, "all-time peak");
    const history = parseHistory(html);
    if (!peak24h || !allTimePeak) throw new Error("Steam Charts headline parser returned an invalid peak");
    steamCharts = {
      source: "Steam Charts",
      sourceUrl: STEAM_CHARTS,
      updatedAt: now,
      currentPlayers: current,
      peak24h,
      allTimePeak,
      history
    };
  } catch (error) {
    console.warn(`Steam Charts refresh skipped: ${error.message}`);
  }

  const next = {
    schemaVersion: 1,
    appId: APP_ID,
    updatedAt: now,
    official: {
      source: "Steam Web API",
      sourceUrl: STEAM_API,
      updatedAt: now,
      currentPlayers
    },
    steamCharts
  };
  await fs.writeFile(DATA_PATH, `${JSON.stringify(next, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({
    currentPlayers,
    peak24h: steamCharts.peak24h,
    allTimePeak: steamCharts.allTimePeak,
    historyRows: steamCharts.history.length,
    updatedAt: now
  }));
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
