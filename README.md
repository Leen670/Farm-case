# Farm-case🧑‍🌾🔍
🌱 FARM CASE — Every Clue Leads to a Better Harvest.  Step into the farmer’s world, explore the farm, and collect clues along the way. Use NASA data and AI-powered analysis to discover the most suitable and sustainable crop rotation strategy for the farm.

## Crop table

Seasonal water needs are the midpoint of the range in [FAO Irrigation Water Management, Training manual no. 3, Table 5](https://www.fao.org/4/s2022e/s2022e02.htm). Chickpea and lentil use that table's bean range, faba bean uses the pea range, and sesame uses the oil-seed range in [FAO Irrigation and Drainage Paper 24](https://www.fao.org/4/s8376e/s8376e.pdf). Salt classes follow FAO Irrigation and Drainage Paper 29.

📄 [Read Project Summary](Summary)

## Grounded answers

After Gemini writes, the API checks the reply against the case JSON. Every crop name and every number in the text has to appear there. `corn` counts as maize. A crop or a number that is not in the case, or a call that fails, is thrown away and the template is shown instead.

On 15 Nov 2026 the results paragraph was rewritten 10 times for each demo farm (Iowa, Punjab, Andalusia), using the saved POWER fixtures and `gemini-3.5-flash-lite` at temperature 0. The calls were two seconds apart so a rate limit was not counted as a wrong answer. Temperature 0 repeats the same request, and every repeat stayed inside the case.

| Farm | Grounded |
| --- | --- |
| Iowa | 10/10 |
| Punjab | 10/10 |
| Andalusia | 10/10 |
| All three | 30/30 |

Punjab and Andalusia were the real test. Their template says limited water lowers crops that need 700 mm, and 700 is not a number in those cases. The rewrite left that sentence out and kept the crops, the rain, and the temperatures.
