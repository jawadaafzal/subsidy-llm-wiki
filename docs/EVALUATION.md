# Evaluation: LLM Wiki vs RAG baseline

Date: 2026-11-08  |  Questions: 15
Scoring: automatic string check (figure or keyword must appear in the answer; out-of-scope questions must answer 'Not found'). Strict, so failures need manual reading.

**Wiki: 15/15  |  RAG baseline: 14/15**

| ID | Type | Wiki | RAG |
|---|---|---|---|
| Q01 | figure | pass | pass |
| Q02 | figure | pass | pass |
| Q03 | figure | pass | pass |
| Q04 | figure | pass | pass |
| Q05 | figure | pass | pass |
| Q06 | figure | pass | pass |
| Q07 | figure | pass | pass |
| Q08 | figure | pass | pass |
| Q09 | figure | pass | pass |
| Q10 | figure | pass | pass |
| Q11 | policy | pass | pass |
| Q12 | policy | pass | pass |
| Q13 | premise | pass | FAIL |
| Q14 | out_of_scope | pass | pass |
| Q15 | out_of_scope | pass | pass |

## Failures and answers to read manually

### Q13: Has the government already paid Rs 1,091,000 million to subsidy beneficiaries in FY 2026-27?

- Wiki (pass): No, the government has not necessarily paid Rs 1,091,000 million to subsidy beneficiaries, as subsidies are budgeted at Rs 1,091,000 million for fiscal year 2026-27, and budget allocations represent budget allocations rather than actual payments [concepts/current_expenditures_subsidies_overview, published/pakistani_government_subsidies_in_the_fy2026_27_budget, sources/pakistan_federal_budget_2026_27]. Note: The wiki pages 'concepts/current_expenditures_subsidies_overview' and 'sources/pakistan_federal_budget_2026_27' are in draft status.
- RAG (FAIL): Not found in sources


## All answers

### Q01 (figure): What is the total budgeted subsidy for FY 2026-27?

- **Wiki** (pass): The total budgeted subsidy for FY 2026-27 is Rs 1,091,000 million (note: budget allocations are not payments, and the status of concepts/current_expenditures_subsidies_overview is draft) [concepts/current_expenditures_subsidies_overview, published/pakistani_government_subsidies_in_the_fy2026_27_budget].
- **RAG** (pass): 1,091,000

### Q02 (figure): How much is budgeted for the Subsidy to Power Sector (WAPDA/PEPCO/KESC) in FY 2026-27?

- **Wiki** (pass): The budget 2026-27 allocates Rs 830,000 million for the Subsidy to Power Sector (WAPDA/PEPCO/KESC). Note that the wiki page 'entities/power_sector_subsidies' is a draft.
- **RAG** (pass): 830,000

### Q03 (figure): How much is budgeted for the Subsidy to Food (PASSCO) in FY 2026-27?

- **Wiki** (pass): The Total Subsidy to Food (PASSCO) is budgeted at Rs 19,000 million for fiscal year 2026-27 [entities/food_subsidy_passco]. Note that the status of the Food Subsidy PASSCO wiki page is draft.
- **RAG** (pass): 19,000

### Q04 (figure): How much is budgeted for the Subsidy to Industries and Production in FY 2026-27?

- **Wiki** (pass): The total Subsidy to Industries & Production is budgeted at Rs 37,000 million for fiscal year 2026-27 (Note: the page entities/industries_and_production_subsidies is a draft). Budget allocations represent budget allocations rather than actual payments.
- **RAG** (pass): 37,000

### Q05 (figure): What is the total of Others Subsidies budgeted for FY 2026-27?

- **Wiki** (pass): Note: The status of the wiki page is draft. Total Others Subsidies are budgeted at Rs 205,000 million for fiscal year 2026-27.
- **RAG** (pass): 205,000

### Q06 (figure): What is the green component in subsidies for FY 2026-27?

- **Wiki** (pass): The total green component in subsidies for FY 2026-27 is budgeted at Rs 476,000 million (note: this page is a draft). Sectoral breakdowns include: Energy sector mitigation at Rs 423,000 million, Agriculture sector adaptation at Rs 21,000 million, Food sector adaptation at Rs 19,000 million, Industries sector mitigation at Rs 8,000 million, and Transport sector mitigation at Rs 5,000 million [concepts/green_component_in_subsidies].
- **RAG** (pass): 476,000

### Q07 (figure): How much is allocated to the PM Apna Ghar Program in FY 2026-27?

- **Wiki** (pass): The PM Apna Ghar Program is budgeted at Rs 71,000 million for fiscal year 2026-27 (note: budget allocations are not payments, and this is from a draft status page) [concepts/other_subsidies].
- **RAG** (pass): 71,000

### Q08 (figure): How much is allocated to the Mera Pakistan Mera Ghar scheme in FY 2026-27?

- **Wiki** (pass): Note: The page concepts/other_subsidies is a draft. The Mera Pakistan Mera Ghar Scheme (Mark-up Subsidy on Housing Finance Scheme) is budgeted at Rs 5,000 million for fiscal year 2026-27 [concepts/other_subsidies].
- **RAG** (pass): 5,000

### Q09 (figure): How much is budgeted for the Metro Bus Subsidy in FY 2026-27?

- **Wiki** (pass): The Metro Bus Subsidy is budgeted at Rs 5,000 million for fiscal year 2026-27 (Note: the page concepts/other_subsidies is a draft). Please note that budget allocations are not payments.
- **RAG** (pass): 5,000

### Q10 (figure): How much is budgeted for the markup subsidy to support phasing out of SBP refinancing facilities and Export Re-finance Schemes in FY 2026-27?

- **Wiki** (pass): Note: The status of the referenced wiki page is draft. The markup subsidy to support phasing out of SBP refinancing facilities and Export Re-finance Schemes is budgeted at Rs 88,000 million for fiscal year 2026-27 [concepts/other_subsidies].
- **RAG** (pass): 88,000

### Q11 (policy): What does the National Electricity Plan say about reappropriation of subsidies between the Power Division and the Petroleum Division?

- **Wiki** (pass): The National Electricity Plan 2023-27 states that the reappropriation of annual allocated subsidies between the Power and Petroleum Divisions of the Ministry of Energy may be carried out to account for the collective optimization of the energy value chain. (Note: The National Electricity Plan 2023-27 is a draft status document).
- **RAG** (pass): Reappropriation of annual allocated subsidies between the Power and Petroleum Divisions of Ministry of Energy, may be carried out to account for collective optimization of energy value chain [national_electricity_plan_2023_27:1449-1452].

### Q12 (policy): How does the National Electricity Plan say subsidies for protected residential consumers should be disbursed?

- **Wiki** (pass): The National Electricity Plan 2023-27 describes direct subsidy disbursement mechanisms for protected residential consumers [sources/national_electricity_plan_2023_27], with a detailed action plan for subsidies disbursement targeted for March 31st, 2024 [entities/power_sector_subsidies], and a roadmap with specific timebound milestones to enable disbursement of these subsidies by FY-2026 [entities/power_sector_subsidies]. (Note: The National Electricity Plan 2023-27 page is a draft) [sources/national_electricity_plan_2023_27].
- **RAG** (pass): Subsidies to the protected categories of residential consumers shall be disbursed directly pursuant to the detailed action plan to be developed under Strategic Directive 067 [national_electricity_plan_2023_27:1396-1399].

### Q13 (premise): Has the government already paid Rs 1,091,000 million to subsidy beneficiaries in FY 2026-27?

- **Wiki** (pass): No, the government has not necessarily paid Rs 1,091,000 million to subsidy beneficiaries, as subsidies are budgeted at Rs 1,091,000 million for fiscal year 2026-27, and budget allocations represent budget allocations rather than actual payments [concepts/current_expenditures_subsidies_overview, published/pakistani_government_subsidies_in_the_fy2026_27_budget, sources/pakistan_federal_budget_2026_27]. Note: The wiki pages 'concepts/current_expenditures_subsidies_overview' and 'sources/pakistan_federal_budget_2026_27' are in draft status.
- **RAG** (FAIL): Not found in sources

### Q14 (out_of_scope): What is the population of Pakistan?

- **Wiki** (pass): Not found in wiki
- **RAG** (pass): Not found in sources

### Q15 (out_of_scope): Who is the Finance Minister of Pakistan?

- **Wiki** (pass): Not found in wiki
- **RAG** (pass): Not found in sources
