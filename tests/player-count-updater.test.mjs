import test from "node:test";
import assert from "node:assert/strict";
import { parseHeadline, parseHistory } from "../scripts/update-player-count.mjs";

const steamChartsFixture = `
<div class="app-stat">
  <span class="num">3202</span>
  <br>playing <abbr class="timeago" title="2026-07-27T02:04:26Z"></abbr>
</div>
<div class="app-stat"><span class="num">4653</span><br>24-hour peak</div>
<div class="app-stat"><span class="num">116969</span><br>all-time peak</div>
<table><tbody>
  <tr class="odd">
    <td class="month-cell left italic">Last 30 Days</td>
    <td class="right num-f italic">3618.25</td>
    <td class="right num-p gainorloss italic">&#43;55.9</td>
    <td class="right num-p gainorloss italic">+1.57%</td>
    <td class="right num italic">6169</td>
  </tr>
  <tr>
    <td class="month-cell left">June 2026</td><td class="right num-f">3562.39</td>
    <td class="right num-p gainorloss">174.22</td><td class="right num-p gainorloss">+5.14%</td>
    <td class="right num">6452</td>
  </tr>
  <tr>
    <td class="month-cell left">May 2026</td><td class="right num-f">3388.17</td>
    <td class="right num-p gainorloss">-1118.51</td><td class="right num-p gainorloss">-24.82%</td>
    <td class="right num">5787</td>
  </tr>
</tbody></table>`;

test("parses Steam Charts headline metrics around br tags", () => {
  assert.equal(parseHeadline(steamChartsFixture, "playing"), 3202);
  assert.equal(parseHeadline(steamChartsFixture, "24-hour peak"), 4653);
  assert.equal(parseHeadline(steamChartsFixture, "all-time peak"), 116969);
});

test("parses Steam Charts monthly history and numeric entities", () => {
  const rows = parseHistory(steamChartsFixture);
  assert.equal(rows.length, 3);
  assert.deepEqual(rows[0], {
    period: "Last 30 Days",
    average: 3618.25,
    gain: 55.9,
    gainPercent: 1.57,
    peak: 6169
  });
  assert.equal(rows[2].gain, -1118.51);
});
