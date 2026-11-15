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

`POST /api/windows` scores the EcoCrop table on each crop's own growing months. The 15-crop game is unchanged.

A crop cycle of 150 days is judged on a five-month window, slid around the year. Rain limits in EcoCrop are for a full year, so they are scaled down to the length of that window. The score is the worse of temperature and rain. Crops that tie are ordered by how close the window sits to the middle of the optimum.

The file has 2,568 species. This search keeps the ones EcoCrop marks as a cereal, pulse, vegetable, root, fruit, forage, or fibre. Forest, ornamentals, weeds, and medicinals stay in the file. The parent row for maize has a blank category, so the search uses `Zea mays ssp. mays`.

On the three demo farms the closest crop is the same in the 2001–2025 climatology and in the monthly average for 2001–2020:

| Farm | Closest crop | 2001–2020 leader changed |
| --- | --- | --- |
| Ames, Iowa | common bean | no |
| Ludhiana, Punjab | black-eyed pea | no |
| Córdoba, Andalusia | garden burnet | no |

Iowa's bean starts in May. The game's barley plan does not, because the game still scores summer crops on the hottest-month extreme. These are two different answers on purpose.

### CropHarvest labels

The [CropHarvest](https://github.com/nasaharvest/cropharvest) library pins Zenodo record 10251170. That record's `labels.geojson` is 85,689,847 bytes: 113,893 points, each a location, a crop name when one was collected, and a date. The satellite archive beside it, `eo_data.tar.gz`, is 26.7 GB and was not downloaded. A download that is not named `labels.geojson`, or is over 100 MB, is refused.

Within 50 km of each demo pin the points are from `geowiki-landcover-2017`. They say whether the land is cropland. They do not name the crop.

| Farm | Points within 50 km | Marked cropland | Nearest named crop |
| --- | --- | --- | --- |
| Ames, Iowa | 4 | 4 | oats, 722 km away, in the Canada set |
| Ludhiana, Punjab | 4 | 4 | alfalfa, 997 km away, in the Central Asia set |
| Córdoba, Andalusia | 8 | 6 | wheat, 1,199 km away |

A name that far away is a different landscape, so it is not used to check the rotation. The three pins are recorded as cropland. The dataset does not say which crop was growing there.

Of the 15 crops in the game, the labels file has a matching name for each except chickpea. Faba bean is stored as `fababeans` (48 points).

### Prithvi

[Prithvi-EO 1.0, the 100M crop-classification weights](https://huggingface.co/ibm-nasa-geospatial/Prithvi-EO-1.0-100M-multi-temporal-crop-classification), was fine-tuned on US crop images and needs a GPU plus HLS imagery. That classification is not run here. The paper is [arXiv:2310.18660](https://arxiv.org/pdf/2310.18660v1.pdf).

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
