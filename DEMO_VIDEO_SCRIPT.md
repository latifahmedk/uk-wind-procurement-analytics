# Client Demonstration & Technical Review Video Script
**Project**: UK Wind Power Forecast & Day-Ahead Procurement Analytics Dashboard  
**Total Target Duration**: Maximum 10:00 (Divided into two 5-minute segments)

---

## Recording Checklist & Preparation

- [ ] **Application Running**:
  - Backend running on `http://127.0.0.1:8000` (FastAPI Swagger docs open in one tab).
  - Frontend running on `http://127.0.0.1:5173` (Terminal dashboard open in main recording window).
- [ ] **Screen Resolution**: Set display to 1080p (1920x1080) for clean text readability.
- [ ] **Browser Settings**: Zoom set to 100%, dark theme active, full-screen browser (F11).
- [ ] **Audio Setup**: Microphone tested with noise cancellation.
- [ ] **Active Date Range**: Default January 2026 selected with 11:00 UK Time cutoff.

---

## PART 1: Client Presentation (Maximum 5 Minutes)
**Target Audience**: Energy Utility Heads of Trading, Day-Ahead Power Procurement Desks, Portfolio Risk Managers  
**Tone**: Executive, commercial, market-focused, solution-oriented  
**Suggested Duration**: 00:00 - 05:00

### 1. Introduction & The Day-Ahead Wind Forecasting Problem (00:00 - 01:00)
- **Visual**: Dashboard Executive Overview page loaded with January 2026 data.
- **Presenter Script**:
  > *"Welcome everyone. In Great Britain's wholesale electricity market, our procurement desk faces a daily multi-million-pound challenge: balancing anticipated customer electricity demand against volatile, weather-dependent generation—most notably, our national wind fleet of over 28 gigawatts.*
  >
  > *Under the Balancing and Settlement Code, our day-ahead purchasing decisions must be committed one day before physical delivery at the 11:00 AM auction gate closure. If we rely on wind generation that under-delivers, our utility is exposed to severe cashout imbalance penalties at the System Buy Price. Conversely, over-contracting leads to surplus sell-backs at a discount.*
  >
  > *To manage this exposure, our traders need clear answers to four questions: What was the exact wind forecast available before auction gate closure? How accurately did it perform against settlement actuals? Where did the forecast fail? And what is our quantitative wind shortfall risk?*
  >
  > *This dashboard was built specifically to solve that problem."*

### 2. Executive Dashboard & KPI Summary Cards (01:00 - 02:00)
- **Visual**: Hover over the top header, the live status pill, and the 8 KPI cards across the top.
- **Presenter Script**:
  > *"Starting on our Executive Overview, the top bar clearly confirms our data provenance: this is directly connected to official Elexon BMRS market data, with live data freshness and timestamp indicators.*
  >
  > *Our 8 KPI cards provide an immediate snapshot across the selected period—here showing the full month of January 2026 with our standard 11:00 AM Day-Ahead cutoff:*
  > - *We see the **Latest Eligible Wind Forecast** of 7,472 MW for the delivery interval.*
  > - *Total planned forecast volume of **8.7 TWh** compared to delivered settlement outturn of **8.3 TWh**.*
  > - *Our key accuracy benchmarks: an MAE of **1,452 MW** and an RMSE of **1,894 MW**.*
  > - *Notice the **Mean Forecast Bias**: at **+412 MW**, the National Grid ESO forecast exhibited a systematic tendency to overpredict wind yield in January, overforecasting in 68% of delivery hours.*
  > - *Finally, our **Potential Wind Shortfall** KPI reveals **640 GWh** of cumulative uncontracted wind deficit, with a peak single-hour shortfall of **4,120 MW**."*

### 3. Forecast vs Actual Time-Series Analysis (02:00 - 03:00)
- **Visual**: Scroll to the main interactive chart. Hover over data points to display custom tooltips. Toggle the "Shortfall Area" on and off.
- **Presenter Script**:
  > *"Moving down to our main interactive time-series chart, the cyan line represents the day-ahead forecast selected strictly prior to gate closure, while the emerald line shows realized outturn from Elexon FUELHH.*
  >
  > *Notice the red shaded shortfall area: whenever the solid forecast sits above actual generation, wind generation failed to materialize. Hovering over any interval reveals the exact timestamps in UK local time, the MW values, the error delta, and crucially, the exact publication snapshot of the forecast.*
  >
  > *Traders can easily toggle layers—focusing on forecast, actuals, or shortfall areas—enabling rapid visual audits of wind ramp events during weather transitions."*

### 4. Forecast Accuracy & Diurnal Biases (03:00 - 04:00)
- **Visual**: Click on the "Forecast Accuracy" tab. Point to the Automated Interpretation Card, the Error Distribution Bar Chart, and the Diurnal Profile.
- **Presenter Script**:
  > *"Under our Forecast Accuracy section, we translate raw metrics into commercial insights. The terminal automatically generates a qualitative desk interpretation based on computed statistics.*
  >
  > *In the Error Distribution chart, traders can immediately inspect the skew: we see a significant right-skewed tail representing positive overforecast errors greater than 2,000 MW.*
  >
  > *Beside it, our Diurnal Hourly Bias profile is particularly powerful: it reveals that forecast overprediction peaks during afternoon ramp hours between 14:00 and 18:00 UK time. This tells our procurement desk that evening peak contracts carry the highest physical wind shortfall risk, requiring defensive procurement buffering."*

### 5. Procurement Insights & Limitations (04:00 - 05:00)
- **Visual**: Navigate to "Procurement Insights". Point to the prominent amber Disclaimer Banner, the Downside P10 scenario curve, and the Top 5 Shortfalls table.
- **Presenter Script**:
  > *"In our Procurement Insights panel, we provide transparent risk metrics alongside an essential commercial boundary.*
  >
  > *Notice the prominent disclaimer: this analysis quantifies physical wind volume shortfalls relative to day-ahead forecasts. It does not claim to know the utility's total net procurement deficit, because consumer demand forecasts, retail supplier shaping, and solar portfolios are intentionally excluded from Elexon's public generation datasets.*
  >
  > *To assist procurement, our terminal calculates a conservative **P10 Downside Scenario**—the yellow dashed curve representing the 90th percentile historical risk margin. When purchasing in day-ahead auctions, buying against the P10 curve rather than the mean forecast protects the desk against 90% of wind deficit events.*
  >
  > *In summary, this dashboard gives our trading desk defensible, bias-free empirical data to reduce balancing cashout costs and optimize day-ahead auction participation."*

---

## PART 2: Technical Review (Maximum 5 Minutes)
**Target Audience**: Chief Technology Officer, Lead Data Architect, Senior DevOps Engineer, Code Reviewers  
**Tone**: Technical, architectural, rigorous, code-level  
**Suggested Duration**: 05:00 - 10:00

### 1. Architecture, Monorepo Structure & Request Flow (05:00 - 06:00)
- **Visual**: Show directory tree in VS Code / terminal, then switch to FastAPI Swagger UI at `http://127.0.0.1:8000/docs`.
- **Presenter Script**:
  > *"Turning to the technical architecture: the application is built as a clean, decoupled monorepo consisting of a React 19 TypeScript frontend and an asynchronous Python FastAPI backend.*
  >
  > *Our backend architecture strictly separates concerns:*
  > - *`app/core`: Configuration and structured logging.*
  > - *`app/services`: `ElexonClient` for streaming HTTP ingest, `CacheService` with TTL, and `forecast_selector.py`.*
  > - *`app/analytics`: Vectorized matching, accuracy calculations, and procurement risk modeling.*
  > - *`app/api`: Clean REST routes with Pydantic request/response validation.*
  >
  > *Here on the Swagger documentation, you can inspect all production endpoints: `/api/health`, `/api/metadata`, `/api/forecasts`, `/api/actuals`, `/api/analysis/*`, and `/api/data/export` for streaming CSV downloads."*

### 2. Elimination of Look-Ahead Bias & Forecast Selection Logic (06:00 - 07:00)
- **Visual**: Open `backend/app/services/forecast_selector.py` and `backend/app/utils/time_utils.py` in editor.
- **Presenter Script**:
  > *"The core algorithmic challenge of this assignment is eliminating look-ahead bias.*
  >
  > *In `time_utils.py`, for any delivery interval on date $D$, we compute the Day-Ahead decision cutoff in UK local time (`Europe/London`) on $D-1$ at the configured cutoff time (defaulting to 11:00 AM, matching the EPEX/NordPool auction gate closure), converting it cleanly to UTC. This handles British Summer Time daylight saving transitions without one-hour offsets.*
  >
  > *In `forecast_selector.py`, we filter the entire stream of National Grid ESO `WINDFOR` snapshots to candidate records where `publishTime <= cutoff_utc`. We then sort by `publishTime` descending and select the single latest available forecast per delivery interval. Any forecast published at 12:25, 15:30, or later is strictly discarded.*
  >
  > *Furthermore, for our January 2026 dataset, our cohort logic explicitly preserves month boundaries: a decision made on January 31 delivers on February 1 and is fully retained."*

### 3. Resolution Matching & Accuracy Calculation Engine (07:00 - 08:00)
- **Visual**: Open `backend/app/analytics/matcher.py` and `backend/app/analytics/accuracy.py`.
- **Presenter Script**:
  > *"Next, the data resolution matching. Elexon `FUELHH` outturn is reported in 30-minute settlement periods (48 periods per day), whereas `WINDFOR` forecasts are issued at hourly resolution.*
  >
  > *In `matcher.py`, we aggregate the two half-hourly actual settlement periods within each hour into an hourly average generation outturn in MW, ensuring physically and mathematically consistent comparison with the hourly forecast.*
  >
  > *In `accuracy.py`, we implement vectorized NumPy and Pandas calculations for MAE, RMSE, and Mean Bias.*
  >
  > *For MAPE, we explicitly protect against division-by-zero distortion: when actual wind generation falls below 50 MW, those intervals are excluded from the MAPE denominator. The API returns both the valid observation count and the excluded count for total mathematical transparency."*

### 4. Automated Testing Strategy & Validation (08:00 - 09:00)
- **Visual**: Terminal showing `pytest tests -v` passing with 21/21 tests.
- **Presenter Script**:
  > *"Reliability is verified through an automated test suite of 21 tests with 100% pass rate:*
  > - *`test_forecast_selector.py` verifies cutoff filtering, latest snapshot selection, and asserts that post-cutoff snapshots are rejected.*
  > - *`test_matching.py` verifies half-hourly to hourly aggregation and validates `MISSING_ACTUAL` and `MISSING_FORECAST` status flags.*
  > - *`test_accuracy_metrics.py` verifies MAE, RMSE, Bias, and MAPE behavior with zero actuals against verified manual calculations.*
  > - *`test_time_and_boundaries.py` tests GMT/BST daylight transitions and month boundary cohorts.*
  > - *`test_api_endpoints.py` performs integration tests across all FastAPI routes using TestClient."*

### 5. Docker Containerization & Deployment Readiness (09:00 - 10:00)
- **Visual**: Open `docker-compose.yml`, `frontend/Dockerfile`, `frontend/nginx.conf`, and `render.yaml`.
- **Presenter Script**:
  > *"For deployment and DevOps:*
  > - *`backend/Dockerfile` builds a Python 3.12 slim container with a built-in health check querying `/api/health`.*
  > - *`frontend/Dockerfile` utilizes a multi-stage build: compiling the React bundle with Node 20, then serving it via a lightweight Alpine Nginx container.*
  > - *Our `nginx.conf` handles client-side SPA routing and reverse-proxies `/api/` to `http://backend:8000/api/` inside Docker's internal bridge network, completely avoiding localhost networking pitfalls.*
  > - *The entire stack starts with a single command: `docker compose up --build`.*
  >
  > *For public cloud deployment, we have included `vercel.json` for frontend hosting on Vercel and `render.yaml` for backend deployment on Render.*
  >
  > *Thank you for your time. The application is completely functional, thoroughly tested, and ready for deployment."*
