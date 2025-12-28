# BA Analysis & Guidelines

## 1. Layout & UI Guidelines
**Style**: Modern Clean Minimalism (Enterprise SaaS)
Based on `doc/layout_guidelines_complete.md`.

### Core Principles
1.  **Clean & Airy**: High whitespace, subtle borders (1px #e5e7eb), soft shadows.
2.  **No Pure Black**: Use Neutral Grays (#1f2933, #111827) for text.
3.  **Card-Based**: Group data in cards with 8-12px radius.
4.  **Utility-First**: Use Tailwind classes, 8pt grid system.

### Responsive Breakpoints
- **Mobile**: < 768px (100% width)
- **Tablet**: 768px - 1023px
- **Desktop**: > 1024px (Max width ~1400px)

## 2. Security & Compliance

### Authentication
- **MISA Integration**: Currently uses Hardcoded Service Token/Secrets (Development Mode).
- **Recommendation**: Move secrets to Environment Variables (`.env`) immediately.
- **Frontend-Backend**: No Auth implemented yet for internal users (Open API). Needs to implement JWT/OAuth.

### Data Privacy
- Customer PII (Phone, Email) is stored in `Dim_Customers`. Ensure access control.
- **CORS**: Currently permissive (`allow_origins=["*"]` implicitly via broad debugging or specific localhosts). Should be restricted in Production.

## 3. Business Logic

### 3.1 Demand Forecasting
- **Smooth Demand**: Products with regular sales -> Use ARIMA / ETS.
- **Lumpy Demand**: Products with sporadic sales -> Use Croston / ADIDA.
- **Classification**: Based on ADI (Average Demand Interval) and CV2 (Coefficient of Variation).

### 3.2 Inventory Optimization
- **Safety Stock (SS)**:
  $$SS = Z \times \sqrt{LT \times \sigma_{error}^2}$$
  Where $Z$ is Service Level (e.g., 1.65 for 95%), $LT$ is Lead Time.
- **Reorder Point (ROP)**:
  $$ROP = (DailyForecast \times LT) + SS$$

### 3.3 Purchasing
- **Suggestion**: Create PO when `CurrentStock <= ROP`.
- **Quantity**: $EOQ$ or $TargetStock - CurrentStock$.
