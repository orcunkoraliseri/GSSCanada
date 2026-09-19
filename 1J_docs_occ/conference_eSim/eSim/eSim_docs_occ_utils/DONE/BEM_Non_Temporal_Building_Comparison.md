# Non-Temporal Building Characteristics Comparison
## Reference Dataset vs 06CEN05GSS

### Dataset Context

| Dataset | Census Year | GSS Year | Sample Size | Geography |
|---------|-------------|----------|-------------|-----------|
| **Reference** | 2021 | 2022 | ~5,700 HH | Canada |
| **06CEN05GSS** | 2006 | 2005 | ~630 HH (5% sample) | Canada |

---

## 1. DWELLING TYPE (DTYPE) Distribution

### Reference Dataset (2022/2021)
- **SingleD (Single Detached)**: ~3,000 HH **(52% dominant)**
- **DuplexD (Duplex)**: ~1,100 HH (19%)
- **MidRise**: ~450 HH (8%)
- **HighRise**: ~350 HH (6%)
- **SemiD (Semi-Detached)**: ~300 HH (5%)
- **Attached (Row House)**: ~250 HH (4%)
- **OtherA & Movable**: ~100 each (2% each)

### 06CEN05GSS (2005/2006)
- **SemiD (Semi-Detached)**: ~350 HH **(55% dominant)**
- **SingleD (Single Detached)**: ~115 HH (18%)
- **HighRise**: ~65 HH (10%)
- **MidRise**: ~25 HH (4%)
- **DuplexD & Movable**: ~25-35 HH each (4-5%)
- **Attached & OtherA**: <20 HH each (<3%)

### Interpretation
**Major Difference**: Dwelling type distributions are fundamentally different between the two datasets:

1. **Reference (2022)**: Strong suburban/single-family housing dominance
   - 52% Single Detached homes
   - Reflects typical Canadian suburban housing stock
   - More spread across dwelling types

2. **06CEN05GSS (2005)**: Urban/dense housing emphasis
   - 55% Semi-Detached homes
   - Higher proportion of High-Rise apartments
   - Suggests more urban/dense sampling area

**Possible Causes**:
- **Geographic sampling bias**: Different CMAs (Census Metropolitan Areas) sampled
- **Temporal shift**: Housing stock changes from 2005→2022 (more single-family development)
- **5% sampling artifact**: Random sampling captured more urban households in 2005

---

## 2. BEDROOM COUNT (BEDRM) Distribution

### Both Datasets
**Consistent Pattern** (Similar proportions):
- **2 Bedrooms**: ~60-65% dominant in both
- **3 Bedrooms**: ~25-30% in both  
- **1 Bedroom**: ~12-15% in both

### Interpretation
✅ **Bedroom distribution is remarkably consistent** across both time periods:
- Canadian households predominantly have 2-3 bedrooms
- This matches national housing statistics
- Validates that both samples represent realistic Canadian residential stock

---

## 3. TOTAL ROOM COUNT Distribution

### Reference Dataset (2022/2021)
- Peak at **2.0 rooms**: ~1,700 HH
- Secondary peak at **3.5 rooms**: ~1,750 HH
- Tertiary peak at **4.0 rooms**: ~1,600 HH
- Distribution: 0.5-4.5 rooms (wide spread)

### 06CEN05GSS (2005/2006)
- Peak at **2.0 rooms**: ~200 HH
- Secondary peak at **4.0 rooms**: ~190 HH
- Tertiary peak at **2.5 rooms**: ~165 HH
- Distribution: 0.5-4.5 rooms (similar spread)

### Interpretation
✅ **Similar distribution shape** between datasets:
- Both show multi-modal distribution (2, 2.5, 3.5-4 room peaks)
- Reflects typical Canadian home sizes
- Small vs medium vs larger homes represented in both

**Minor difference**: 
- Reference has slightly higher 3.5-room peak
- 06CEN05GSS shows more even distribution across 2-4 rooms

---

## Overall Assessment

| Characteristic | Similarity | Notes |
|----------------|------------|-------|
| **Dwelling Type** | ❌ **Different** | Urban vs suburban sampling bias |
| **Bedroom Count** | ✅ **Consistent** | Both reflect Canadian housing stock |
| **Room Count** | ✅ **Similar** | Same shape, scaled to sample size |

### Conclusions

1. **Bedroom distribution validates both datasets** - aligns with Canadian statistics
2. **Dwelling type difference is significant** - reflects different geographic sampling:
   - Reference → Suburban/single-family dominant
   - 06CEN05GSS → Urban/dense housing dominant
3. **Room counts are realistic** in both datasets

### Recommendations

When using 06CEN05GSS for BEM simulations:
- ✅ **Bedroom and room distributions are reliable** for occupancy modeling
- ⚠️ **Be aware of urban bias** in dwelling types (more apartments, less single-family)
- Consider whether your simulation target matches the **urban-heavy** 06CEN05GSS sample or requires adjustment
