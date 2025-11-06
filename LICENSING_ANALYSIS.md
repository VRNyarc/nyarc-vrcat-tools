# Licensing Analysis for NYARC VRCat Tools - Robust Transfer Module

**Date:** 2025-01-06
**Issue:** GPL-3.0 / MIT License Compatibility

---

## ⚠️ **CRITICAL LICENSE CONFLICT DETECTED**

### Current Situation:

**Your Project:**
- License: MIT (permissive)
- File: `LICENSE` in root directory

**Source Material:**
- Project: `sentfromspacevr/robust-weight-transfer`
- License: **GPL-3.0** (copyleft)
- URL: https://github.com/sentfromspacevr/robust-weight-transfer

### The Problem:

**GPL-3.0 is incompatible with MIT for derivative works.**

- ❌ **Cannot** take GPL-3.0 code and release under MIT
- ❌ **Cannot** distribute GPL-derived code with more permissive license
- ❌ Current setup violates GPL-3.0 terms

---

## 📋 **GPL-3.0 Requirements**

### What GPL-3.0 Requires:

1. **Source Code Disclosure**
   - ✅ Already doing this (open source repository)

2. **License Preservation**
   - ❌ NOT doing: Using MIT instead of GPL-3.0

3. **Copyleft ("Viral")**
   - Derivative works MUST also be GPL-3.0
   - Cannot relicense to MIT, Apache, BSD, etc.

4. **Attribution**
   - ✅ Partially doing: Credit in `robust/__init__.py`
   - Need: More prominent attribution

5. **Change Documentation**
   - ✅ Doing: Commit messages document changes
   - Need: Explicit statement of modifications

---

## 🔍 **What You're Using from GPL-3.0 Source**

### Files/Modules Derived from GPL-3.0:

```
nyarc_vrcat_tools/shapekey_transfer/robust/
├── __init__.py         ← Contains attribution
├── core.py             ← Adapted algorithm
├── correspondence.py   ← Geometric matching
├── inpainting.py       ← Harmonic inpainting (core GPL code)
├── mesh_data.py        ← Data structures
├── island_handling.py  ← Our addition (but derives from GPL work)
├── smoothing.py        ← Post-processing
└── debug.py            ← Visualization
```

**These files implement the algorithm from:**
- **Paper:** "Robust Skin Weights Transfer via Weight Inpainting"
- **Authors:** Abdrashitov, Raichstat, Monsen, Hill
- **Conference:** SIGGRAPH ASIA 2023
- **Reference Implementation:** GPL-3.0 licensed

---

## ✅ **SOLUTIONS (Choose One)**

### **Option 1: Change Entire Project to GPL-3.0** (Recommended)

**Pros:**
- ✅ Legally compliant
- ✅ Proper attribution to original authors
- ✅ Aligns with open-source spirit
- ✅ Can use original code freely

**Cons:**
- 🔄 All users must follow GPL-3.0 terms
- 🔄 Derivative works must also be GPL-3.0

**Action Items:**
1. Change `LICENSE` file from MIT to GPL-3.0
2. Add copyright notice to all files
3. Add prominent attribution to robust module
4. Update README with GPL-3.0 notice

---

### **Option 2: Dual License Approach**

**Structure:**
- Main addon: MIT license
- Robust module: GPL-3.0 license (separate LICENSE file)

**Pros:**
- ✅ Core addon remains MIT
- ✅ Robust module legally compliant
- ✅ Users can choose which parts to use

**Cons:**
- 🔄 Complex licensing structure
- 🔄 GPL "contaminates" linked code (debatable)
- 🔄 May still require entire addon to be GPL

**Action Items:**
1. Create `robust/LICENSE-GPL3` file
2. Clearly mark robust module as GPL-3.0
3. Document licensing split in README
4. Consult legal expert (GPL linking is complex)

---

### **Option 3: Remove Robust Module**

**Keep addon MIT-only, remove GPL code**

**Pros:**
- ✅ Clean MIT licensing
- ✅ Maximum freedom for users
- ✅ No GPL complications

**Cons:**
- ❌ Lose robust transfer feature
- ❌ Users miss out on better algorithm

---

### **Option 4: Rewrite from Academic Paper** (Not Recommended)

**Implement algorithm from paper independently**

**Pros:**
- ✅ Could stay MIT (if truly independent)
- ✅ Learning experience

**Cons:**
- ❌ Extremely time-consuming (weeks/months)
- ❌ Paper may have patents/additional restrictions
- ❌ Still need to cite academic work
- ❌ Risk of accidental code similarity

---

## 📝 **About "Robust Weight Transfer" Name**

### Can You Use This Name?

**"Robust Weight Transfer" is:**
- ✅ Descriptive term from academic paper
- ✅ Not a trademark (as far as visible)
- ✅ Can be used to describe your implementation

**However:**
- Should acknowledge original implementation
- Should clarify it's "adapted from" or "based on"
- Academic citation still required

**Recommended Naming:**
```
Current UI: "Use Robust Transfer (Harmonic Inpainting)"
Better: "Use Robust Transfer (based on Abdrashitov et al.)"
Or: "Use Harmonic Inpainting Transfer"
```

---

## 🎯 **RECOMMENDATION**

### **Change to GPL-3.0** (Option 1)

**Why:**
1. Legally correct
2. Respects original authors
3. Maintains open-source philosophy
4. Simple and clear
5. Most Blender addons are GPL anyway (Blender itself is GPL!)

**Implementation:**

1. **Update LICENSE file:**
```
GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) 2025 NYARC VRCat Tools Contributors

Portions of this software are based on "Robust Skin Weights Transfer
via Weight Inpainting" by Abdrashitov et al. (SIGGRAPH ASIA 2023),
implementation by sentfromspacevr (GPL-3.0):
https://github.com/sentfromspacevr/robust-weight-transfer

[Full GPL-3.0 text...]
```

2. **Add attribution in robust/__init__.py:**
```python
"""
Robust Shape Key Transfer Module

IMPORTANT: This module is based on GPL-3.0 licensed work:
- Original: https://github.com/sentfromspacevr/robust-weight-transfer
- Paper: "Robust Skin Weights Transfer via Weight Inpainting"
  Abdrashitov, Raichstat, Monsen, Hill (SIGGRAPH ASIA 2023)

When using for academic work, please cite the original paper.

Adapted for shape key transfer (3D vectors instead of scalar weights).
"""
```

3. **Update README.md:**
```markdown
## License

This project is licensed under GPL-3.0. See LICENSE file.

### Attribution

The Robust Transfer feature is adapted from:
- "Robust Skin Weights Transfer via Weight Inpainting"
- Abdrashitov, Raichstat, Monsen, Hill (SIGGRAPH ASIA 2023)
- Implementation: https://github.com/sentfromspacevr/robust-weight-transfer

When using this addon for academic work, please cite the original paper.
```

---

## 📚 **Additional Considerations**

### Academic Citation:

If users publish research using this tool, they should cite:

```bibtex
@inproceedings{Abdrashitov:2023:RSW,
  author = {Abdrashitov, Rinat and Raichstat, Kim and Monsen, Jared and Hill, David I.W.},
  title = {Robust Skin Weights Transfer via Weight Inpainting},
  booktitle = {SIGGRAPH Asia 2023 Technical Communications},
  year = {2023}
}
```

### Blender Ecosystem:

- **Blender itself is GPL-2.0+**
- Many Blender addons are GPL
- GPL is well-understood in Blender community
- Not a barrier to adoption

---

## ⚡ **IMMEDIATE ACTION REQUIRED**

**Current Status:** ❌ License violation
**Risk:** Low (small project, educational use)
**Legal Obligation:** Fix before major release

**Next Steps:**
1. Decide on licensing approach (recommend GPL-3.0)
2. Update LICENSE file
3. Add prominent attribution
4. Update README
5. Consider adding NOTICE file with credits

**Timeline:** Before public release/promotion

---

## 📞 **Questions?**

If you need to:
- Keep MIT license → Must remove robust module entirely
- Use robust module → Must adopt GPL-3.0 (or dual license with risks)
- Consult lawyer → Recommended for commercial use

**Note:** This is technical analysis, not legal advice. Consult a lawyer for formal legal guidance.
