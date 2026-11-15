# Farm Case

Farm Case is a crop-rotation detective game for NASA Space Apps. You pin a farm, collect the climate and satellite clues, and get a three-year rotation. A fixed score chooses the crops. The language model only restyles the paragraph that explains that score.

Play it at [farm-case-web.onrender.com](https://farm-case-web.onrender.com). The API is [farm-case-api.onrender.com](https://farm-case-api.onrender.com). The one-page story is in [Summary](Summary).

## How we rank crops

The ranker tries every sequence of three crops from a fixed list of 15. That is 3,375 rotations. Each crop receives four scores, each from 0 to 100. With no priority checked, the weights are:

| Factor | Weight | What the number is |
| --- | --- | --- |
| Water | 40 | Seasonal water need against the year's rain, plus an irrigation allowance |
| Heat | 25 | Summer crops: an EcoCrop trapezoid on the hottest month. Winter crops: a 1–5 scale on the annual mean |
| Soil | 20 | 100 when the soil matches, 70 when the farmer is not sure, 45 when it misses |
| Salinity | 15 | How salty we treat the water source, against the crop's salt class |

A checked priority adds to one or two weights, and the four are divided again so they still sum to 1.

- Save water adds 20 to water.
- Lower cost adds 10 to water. The irrigation bill is the cost this table can see.
- Increase yield adds 15 to heat and 10 to soil.
- Improve soil adds 10 to soil.

The rotation score is the average of the three crop scores, plus a few rotation rules:

- A nitrogen crop after a cereal is +10, or +15 when improve soil is checked.
- A deep-rooted crop is +5 when improve soil is checked.
- The same family in a row is −15.
- Repeating the farmer's previous crop is −10.

The screen prints that total capped between 0 and 100. Two plans can both show 100. The order uses the total before the cap, then the plan with more distinct crop names, then A to Z.

## Data sources

| Source | What we take from it |
| --- | --- |
| [NASA POWER](https://power.larc.nasa.gov/) climatology, AG community | The 25-year monthly and annual climatology, January 2001–December 2025. Temperature (`T2M`, `T2M_MAX`), rain (`PRECTOTCORR`), and root-zone wetness (`GWETROOT`). |
| [NASA GIBS](https://gibs.earthdata.nasa.gov/) | Pictures only: GPM IMERG precipitation, SMAP soil moisture, and MODIS/Terra NDVI (8-day). Landsat and VIIRS are named and not downloaded. |
| [FAO Training manual no. 3, Table 5](https://www.fao.org/4/s2022e/s2022e02.htm) | Seasonal water need, the midpoint of the published range. Chickpea and lentil use the bean row. Faba bean uses the pea row. |
| [FAO Irrigation and Drainage Paper 24](https://www.fao.org/4/s8376e/s8376e.pdf) | Sesame uses the oil-seed range, because the table has no sesame row. |
| FAO Irrigation and Drainage Paper 29 | Salt class, stored as 1–5. |
| [FAO EcoCrop, via the OpenCLIM snapshot](https://github.com/OpenCLIM/ecocrop) | Temperature limits and soil pH. The code cites this as 'FAO EcoCrop (via openclim/ecocrop)'. |

The wetness number beside the plan is POWER `GWETROOT`. The SMAP layer is the picture next to it, not the source of that number.

## Validation

### The model may only repeat the case

After Gemini writes, every crop name and every number in the reply has to appear in the case JSON. `corn` counts as maize. A mismatch, or a call that fails, is replaced by the template.

On 15 Nov 2026 the results paragraph was rewritten 10 times for each demo farm, using the saved POWER fixtures and `gemini-3.5-flash-lite` at temperature 0. The calls were two seconds apart. Temperature 0 sends the same request again, so each farm's ten replies are repeats, not ten different phrasings. Every repeat stayed inside the case.

| Farm | Grounded replies |
| --- | --- |
| Iowa | 10/10 |
| Punjab | 10/10 |
| Andalusia | 10/10 |
| All three | 30/30 |

Punjab and Andalusia were the real check. Their template says limited water lowers crops that need 700 mm, and 700 is not a measurement in those cases. The rewrite dropped that sentence and kept the crops, the rain, and the temperatures.

### Confidence

The same farm is scored four more times: both temperatures +1°C, both −1°C, rain +10%, and rain −10%. Summer uses the hottest month and winter uses the annual mean, so the one-degree nudge moves both. The top rotation changing in none of the four is High, in one is Medium, and in more than one is Low.

On the three demo farms, with the soil and water the game fills in for each pin:

| Farm | Top rotation | Confidence |
| --- | --- | --- |
| Ames, Iowa | barley, faba bean, onion | High |
| Ludhiana, Punjab | barley, faba bean, wheat | High |
| Córdoba, Andalusia | onion, wheat, faba bean | High |

High means the winner did not move. It does not mean a summer crop would thrive there. The hottest month on these farms sits past the summer crops' EcoCrop optimum, so a winter-led plan stays in front, and a one-degree nudge is too small to change that.

## Limits

- The search is 15 crops. The EcoCrop file has 2,568 crops. The loader keeps the 2,063 rows with a complete temperature and rain range, and the ranker still does not search them.
- Summer heat uses POWER `T2M_MAX`, the hottest month's extreme, not the average daily high. That is why summer crops lose on the demo farms.
- Winter heat is still the 1–5 scale on the annual mean. A winter grain's EcoCrop maximum is the temperature that stops it in summer, so scoring it on the hottest month would zero it.
- A crop's water need is for one season. The score compares it with the whole year's rain. The irrigation added on top (600 mm, 250 mm, or none) is a game assumption. POWER does not report water rights.
- Soil preference is ordinary agronomy, not a NASA product. Soil pH changes the score only when a pH value is passed in.
- Salt stress by water source is our 1–5 stand-in for the FAO classes.
- The satellite pictures do not pick the rotation. The NDVI image is shown and not read.
- Several plans can print 100 because the displayed score is capped. The order underneath is not.
- The assistant cannot add a crop or a measurement. When it tries, the player sees the template instead.

## Phase 2

These are the next measurements, not results we have.

- Search the full EcoCrop table, all 2,568 crops, with a rain and temperature window for each crop's growing months, instead of one yearly total and one hottest month.
- Rank the same pin on a shifted climate and on the 2001–2020 climatology, and show where the rotation changes.
- Check the recommended crops against [CropHarvest](https://github.com/nasaharvest/cropharvest) labels for that place.
- Use Prithvi-EO to classify the crop in the satellite picture, instead of only displaying the NDVI image.

## Run it locally

The API is Python 3.12. From `api/`:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The site is Vite. From `web/`:

```bash
npm install
npm run dev
```

The site calls `http://127.0.0.1:8000` unless `VITE_API_URL` is set. Tests run from `api/` with `pytest`.
