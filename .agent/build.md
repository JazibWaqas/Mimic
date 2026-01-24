# MIMIC Frontend Enhancement - Build Plan

**Version:** 3.0  
**Focus:** Add judge-focused features with vibrant, professional aesthetic  
**Reference:** AURA File Management project (`src/`)

---

## 🚨 **CRITICAL: This is a WEBSITE, NOT a Phone App**

### **Platform Context**
- ✅ **Desktop/Laptop web application** - Standard browser viewport
- ✅ **Website-scale sizing** - 1rem = 16px baseline
- ✅ **Mouse/keyboard interactions** - Hover states, click precision
- ✅ **Horizontal layout priority** - Wide screens, not tall/narrow
- ❌ **NOT a mobile app** - No touch gestures, no mobile-first design
- ❌ **NOT tablet-optimized** - Desktop is primary target

**Why This Matters:**
- Sizing should match **GitHub, Linear, Figma** (not Instagram, TikTok)
- Buttons can be **smaller** (40-48px, not 56px+ for touch)
- Text can be **denser** (14-16px body, not 18px+)
- Spacing can be **tighter** (8-24px gaps, not 32px+)
- Cards can be **compact** (show 6-8 at once, not 2-3)

---

## 🎯 **Design Philosophy & Context**

### **Who This Is For**
- **Primary Audience:** Everyday users who want easy video editing (NOT professional cinematographers)
- **Secondary Audience:** Hackathon judges (technical, design-savvy)
- **Goal:** Make editing feel like a professional is handling it for them

### **Core Design Principles**

#### 1. **Professional BUT Fun**
- **Problem:** Current design is too bland/faded - looks cinematic but dull
- **Solution:** Add vibrancy and "pop" while maintaining professionalism
- **Key:** Make it feel **lively and responsive**, not childish

**Specific Fixes:**
- ✅ **Vibrant buttons** - Execute Synthesis button should POP, not fade into background
- ✅ **Glow effects** - Use outer glows on active elements (Electric Cyan pulse when Gemini is thinking)
- ✅ **Gradient progress bars** - Transition from Indigo → Electric Cyan as synthesis progresses
- ✅ **Interactive hover states** - Cards lift/glow on hover, show "Vibe" tags with bounce
- ✅ **Glassmorphism** - Frosted glass effects for modals and status bars
- ❌ **Keep text contrast** - Current text on background looks nice and neat (don't change)

#### 2. **Information Density (7/10)**
- **Rule:** Users shouldn't scroll much to see all features
- **Goal:** Everything apparent "right then and there" for judges
- **Balance:** Spacing for relaxed/professional feel, but compact enough to show everything

**Current Status:**
- ✅ **Studio:** Best - good balance
- ⚠️ **Library:** Too spacious - cards should be smaller/denser
- ❌ **Vault:** Worst - symmetry off, 9:16 video way longer than right panel

**Specific Constraints:**
- Gap between cards: **1rem max**
- Card padding: **1.5rem max**
- Library grid: Show **6-8 clips at once** without scrolling

#### 3. **Typography**
- **Headers:** Current sizing is fine, keep **bold/heavy** weights
- **Body text:** Increase slightly for better readability (14-16px)
- **Technical data:** Use **JetBrains Mono** for logs, metrics, timestamps (signals "system output")

#### 4. **Color Palette - "Life & Contrast"**

**🚫 FORBIDDEN COLORS (NEVER USE):**
- ❌ **Yellow** (any shade)
- ❌ **Brown** (any shade)
- ❌ **Muddy Olive** (any shade)
- ❌ **Amber/Gold** (replace with Electric Purple for cache indicators)

**✅ PRIMARY PALETTE:**

1. **Electric Cyan** `#00d4ff`
   - **Use:** Primary action, "thinking" state, intelligence signals
   - **Why:** High-tech neon glow, best "AI is working" color
   - **Glow:** `0 0 20px rgba(0, 212, 255, 0.6)`

2. **Hot Pink** `#ff007f`
   - **Use:** Vibe tags, decorative accents, energy signals
   - **Why:** Adds life, breaks up technical look
   - **Glow:** `0 0 16px rgba(255, 0, 127, 0.5)`

3. **Electric Purple** `#bf00ff`
   - **Use:** Cache indicators, optimization badges, system logic
   - **Why:** Sophisticated moody glow (replaces yellow/amber)
   - **Glow:** `0 0 18px rgba(191, 0, 255, 0.5)`

4. **Electric Lime** `#ccff00`
   - **Use:** Success states, verified badges, completion
   - **Why:** High contrast glow, feels like a "win"
   - **Glow:** `0 0 16px rgba(204, 255, 0, 0.6)`

5. **Vibrant Orange** `#ff4500`
   - **Use:** Warnings, alerts, attention needed
   - **Why:** Saturated safety orange, stands out
   - **Glow:** `0 0 14px rgba(255, 69, 0, 0.5)`

**BASE COLORS:**
- **Background:** Deep indigo/black `#020306`
- **Text:** Crisp white `#ffffff` or light silver `#f8fafc`
- **Borders:** White with low opacity `rgba(255, 255, 255, 0.1)`

**SPECIAL EFFECTS:**

**Execute Synthesis Button:**
- **Gradient:** Cyan → Purple `linear-gradient(135deg, #00d4ff 0%, #bf00ff 100%)`
- **Effect:** Looks like it's "charging up" with energy
- **Glow:** `0 0 30px rgba(0, 212, 255, 0.4), 0 0 60px rgba(191, 0, 255, 0.3)`

**Glow Standard (REQUIRED):**
- Any element using accent colors **MUST** include `box-shadow` with blur radius
- Glows should pulse/animate on active states
- Minimum blur: 12px, Maximum blur: 30px

**Text Contrast Rule:**
- Primary text: Always crisp white `#ffffff`
- Secondary text: Light silver `#f8fafc` or slate `#cbd5e1`
- Never sacrifice readability for "fun" colors

---

## 🏗️ **Page-Specific Requirements**

### **Studio Page** ✅
**Status:** Good overall, minor improvements needed

**Changes:**
- Make "Execute Synthesis" button **vibrant** (not faded)
- Add **glow effect** to active processing states
- Keep current 2-column layout (dropzones left, telemetry right)

---

### **Library Page** ⚠️
**Status:** Too spacious, cards too big

**Required Changes:**
1. **Smaller, denser cards** - Show 6-8 clips at once without scrolling
2. **Tighter gaps** - 1rem between cards
3. **Reference:** Use AURA's compact card sizing (see `src/`)

**Card Design:**
- Compact like AURA "Recently Uploaded Files" cards
- View/Download buttons (already added ✅)
- Hover: Slight lift + glow + "Vibe" tag popup

---

### **Vault Page** ❌
**Status:** Needs major fixes - symmetry off, too spacious

**Layout Structure (Post-Mission Briefing):**

**Left Column (400px):**
- Video player (9:16 aspect, 400px wide) ✅ Already done
- **Add:** Electric Cyan glow border that pulses
- **Add:** EDL Color Strip below video (color-coded blocks by vibe)
  - Hover: "X-ray" window shows Gemini reasoning for that cut

**Right Column (Density 8/10):**
- **Top:** X-Ray Gauges (semi-circle gauges with Emerald→Cyan gradient)
  - Clip Diversity, Vibe Match, Energy Coherence
  - Show both: "94% (15/16 clips)"
- **Middle:** Monospace terminal that "typewrites" Gemini synthesis breakdown
- **Bottom:** Material Efficiency chart (how much of clips were used)

**Specific Fixes:**
- Remove or shrink "Synthesis Output" tab row (make it compact like browser tabs)
- Change Download button to smaller Electric Cyan button with glow hover
- Add "Stage Badges" to video (e.g., "Peak Edit", "Intro Montage")

---

## 🎯 **Judge-Focused Features (Priority Order)**

### **Tier 1: Non-Negotiable (MUST HAVE)**

#### 1. **Pipeline Visualization** (5-stage processing view)
**Why:** Proves this is a system, not a prompt wrapper
- Shows orchestration, sequencing, autonomy
- Judges instantly understand complexity

#### 2. **EDL Visualization** (edit decision list with reasoning)
**Why:** Absolute proof of intelligence
- Shows WHY each clip was chosen
- No other teams will have this level of detail

---

### **Tier 2: Very High Impact**

#### 3. **System Status Bar** (cache + Gemini status)
**Why:** Signals production-grade engineering
- Shows performance awareness
- Judges love cache optimization

#### 4. **X-Ray Metrics** (clip diversity, vibe match, energy coherence)
**Why:** Quantifies quality instead of claiming it
- Makes "AI taste" measurable
- Excellent for Vault comparisons

---

### **Tier 3: Nice-to-Have**

#### 5. **Performance Stats** (processing time, cache hits)
**Why:** Good engineering signal
- Keep concise, don't flood UI

#### 6. **Gemini Reasoning Panel** (AI's thinking)
**Why:** Easy to overdo - use summaries, not raw chains
- Judges distrust verbose "AI thoughts"
- Show high-level bullets only

---

## 📐 **Reference: AURA File Management**

**What to Replicate from `src/`:**

1. **Compact Data Cards**
   - AURA's "Patients Served" and "Expenses" cards
   - Use this exact scale for X-Ray Metrics in Vault

2. **Recent Activity List**
   - AURA's filename + date list
   - Perfect blueprint for EDL Visualization
   - Dense, readable, professional

3. **Card Sizing**
   - AURA "Recently Uploaded Files" cards
   - This is the target size for Library cards

---

## 🎨 **The "Fun" Balance**

**Key Principle:** Fun comes from **responsiveness**, not decoration

**Good "Fun":**
- ✅ Instant reactions to clicks (crisp animations)
- ✅ Color changes on interaction
- ✅ Glows and pulses on active states
- ✅ Smooth transitions
- ✅ Micro-animations (card lift, tag bounce)

**Bad "Fun":**
- ❌ Excessive whitespace
- ❌ Childish illustrations
- ❌ Slow, dramatic animations
- ❌ Distracting motion

**Judge Appeal:** Website feels like a "powerful, well-oiled machine"

---

## 📊 **Technical Display Standards**

### **Readability**
- **Default:** Human-readable with "tech-coded" feel
- **Option:** "View JSON" toggle for judges who want raw data

### **Metrics Format**
- **Use both:** "Clip Diversity: 94% (15/16 clips)"
- **Gauges:** Semi-circle fills with gradient (visual reward)

### **Timestamps**
- **Vault:** Absolute ("Jan 24, 2026") - feels like permanent archive
- **Logs:** Relative for recent activity

### **Monospace Usage**
- All technical data
- Telemetry logs
- Timestamps
- Metrics
- JSON/raw output

---

## ✅ **Implementation Checklist**

### Phase 1: Visual Vibrancy
- [ ] Make Execute Synthesis button vibrant (not faded)
- [ ] Add glow effects to active states
- [ ] Implement gradient progress bars
- [ ] Add interactive hover states (lift + glow)
- [ ] Add glassmorphism to modals

### Phase 2: Library Fixes
- [ ] Reduce card size (reference AURA)
- [ ] Tighten gaps to 1rem
- [ ] Show 6-8 clips without scrolling
- [ ] Add hover vibe tags

### Phase 3: Vault Overhaul
- [ ] Add Electric Cyan glow to video player
- [ ] Create EDL color strip below video
- [ ] Build X-Ray gauge components
- [ ] Add monospace terminal for breakdown
- [ ] Create material efficiency chart
- [ ] Shrink tab row
- [ ] Update download button

### Phase 4: Judge Features
- [ ] Pipeline visualization (Tier 1)
- [ ] EDL visualization (Tier 1)
- [ ] System status bar (Tier 2)
- [ ] X-Ray metrics (Tier 2)

---

**One-Sentence Rule:**  
> If a feature does not prove **autonomous decision-making over time**, it's secondary.

**Goal:** Look like a **video synthesis engine**, not a chat interface.

## 🚨 **CRITICAL ISSUE IDENTIFIED**

### The Problem
Current MIMIC frontend has **oversized elements** because it was designed like a mobile app instead of a professional website.

### The Solution
Use sizing from your previous file management project as the baseline:
- **Compact cards** (not huge boxes)
- **Smaller text** (0.9rem - 1.1rem for body, not 1.5rem+)
- **Tighter spacing** (1rem - 2rem gaps, not 3rem+)
- **Dense layouts** (grid with small gaps, not spread out)
- **Professional scale** (website-appropriate, not tablet-sized)

---

## 📏 **Sizing Reference (From Your Previous Project)**

### Typography Scale
```css
/* Headers */
h1: 2.5rem (40px)          /* Page titles */
h2: 1.5rem - 1.8rem        /* Section titles */
h3: 1.1rem - 1.3rem        /* Card titles */

/* Body Text */
body: 1rem (16px)          /* Standard text */
small: 0.9rem (14px)       /* Metadata */
tiny: 0.75rem (12px)       /* Labels */

/* Buttons */
button: 0.9rem - 1rem      /* Button text */
padding: 0.75rem 1rem      /* Button padding */
```

### Spacing Scale
```css
/* Gaps */
card-gap: 1rem             /* Between cards */
section-gap: 2rem          /* Between sections */
padding: 1rem - 2rem       /* Container padding */

/* Card Sizes */
card-padding: 1rem         /* Inside cards */
card-radius: 8px           /* Border radius */
```

### Component Sizes
```css
/* Search Bar */
height: auto (padding-based)
padding: 0.75rem 1rem
font-size: 1rem

/* Filter Buttons */
padding: 0.75rem 1rem
font-size: 0.9rem

/* File Cards */
padding: 1rem
gap: 0.5rem
```

---

## 🎯 **Phase 1: Fix Sizing Foundation (30 min)**

### 1.1 Reset Typography Scale
**File:** `frontend/app/globals.css`

**Replace oversized text with website-appropriate sizes:**

```css
/* Base Typography - WEBSITE SCALE */
html {
  font-size: 16px; /* Standard web baseline */
}

body {
  font-size: 1rem; /* 16px */
  line-height: 1.6;
}

/* Headings - Compact */
h1 {
  font-size: 2.5rem; /* 40px - Page titles */
  font-weight: 700;
  line-height: 1.2;
}

h2 {
  font-size: 1.75rem; /* 28px - Section titles */
  font-weight: 600;
  line-height: 1.3;
}

h3 {
  font-size: 1.25rem; /* 20px - Card titles */
  font-weight: 600;
  line-height: 1.4;
}

/* Text Sizes */
.text-xs { font-size: 0.75rem; }  /* 12px */
.text-sm { font-size: 0.875rem; } /* 14px */
.text-base { font-size: 1rem; }   /* 16px */
.text-lg { font-size: 1.125rem; } /* 18px */
.text-xl { font-size: 1.25rem; }  /* 20px */
.text-2xl { font-size: 1.5rem; }  /* 24px */
.text-3xl { font-size: 1.875rem; }/* 30px */
.text-4xl { font-size: 2.25rem; } /* 36px */
```

---

### 1.2 Fix Spacing Scale
**File:** `frontend/app/globals.css`

```css
/* Spacing - COMPACT WEBSITE SCALE */
.space-y-1 { margin-top: 0.25rem; }  /* 4px */
.space-y-2 { margin-top: 0.5rem; }   /* 8px */
.space-y-3 { margin-top: 0.75rem; }  /* 12px */
.space-y-4 { margin-top: 1rem; }     /* 16px */
.space-y-6 { margin-top: 1.5rem; }   /* 24px */
.space-y-8 { margin-top: 2rem; }     /* 32px */
.space-y-10 { margin-top: 2.5rem; }  /* 40px */
.space-y-12 { margin-top: 3rem; }    /* 48px */

/* Padding - COMPACT */
.p-4 { padding: 1rem; }      /* 16px */
.p-6 { padding: 1.5rem; }    /* 24px */
.p-8 { padding: 2rem; }      /* 32px */

/* Gaps - TIGHT */
.gap-2 { gap: 0.5rem; }      /* 8px */
.gap-3 { gap: 0.75rem; }     /* 12px */
.gap-4 { gap: 1rem; }        /* 16px */
.gap-6 { gap: 1.5rem; }      /* 24px */
```

---

### 1.3 Component Size Standards
**File:** `frontend/app/globals.css`

```css
/* Button Sizes - COMPACT */
.btn-sm {
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.btn-base {
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
}

.btn-lg {
  padding: 0.875rem 1.25rem;
  font-size: 1rem;
}

/* Input Sizes - STANDARD WEB */
input, select, textarea {
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border-radius: 6px;
}

/* Card Sizes - COMPACT */
.card {
  padding: 1rem;
  border-radius: 8px;
  gap: 0.75rem;
}

.card-lg {
  padding: 1.5rem;
  border-radius: 12px;
}
```

---

## 🏗️ **Phase 2: Fix Studio Page Sizing (40 min)**

### 2.1 Hero Section - Compact
**File:** `frontend/app/page.tsx`

**BEFORE (Current - Too Big):**
```tsx
<h1 className="text-4xl font-black">Studio</h1>
<p className="text-[12px] font-black">Integrated Gemini 3 Engine</p>
<h2 className="text-xl font-bold">Edit Videos by Reference</h2>
<p className="text-sm text-slate-400">...</p>
```

**AFTER (Compact - Website Scale):**
```tsx
<h1 className="text-3xl font-bold">Studio</h1>
<p className="text-xs font-semibold text-indigo-400 uppercase tracking-wide">
  Integrated Gemini 3 Engine
</p>
<h2 className="text-lg font-semibold">Edit Videos by Reference Using Gemini 3</h2>
<p className="text-sm text-slate-400 leading-relaxed">...</p>
```

---

### 2.2 Dropzone Cards - Smaller
**BEFORE (Current - Too Big):**
```tsx
<div className="h-[280px] rounded-[2rem] ...">
```

**AFTER (Compact):**
```tsx
<div className="h-[200px] rounded-xl border border-gray-200 ...">
  {/* Smaller icon */}
  <Plus className="h-6 w-6" />
  {/* Smaller text */}
  <p className="text-sm font-semibold">Bind Style Reference</p>
  <p className="text-xs text-gray-500">MP4 / MOV / AVI</p>
</div>
```

---

### 2.3 Telemetry Sidebar - Compact
**BEFORE (Current - Too Big):**
```tsx
<div className="rounded-[2rem] bg-white/[0.03] p-8 ...">
  <h3 className="text-[12px] font-black uppercase tracking-widest">
    System Telemetry
  </h3>
</div>
```

**AFTER (Compact):**
```tsx
<div className="rounded-lg bg-white/[0.03] border border-white/10 p-4">
  <h3 className="text-xs font-bold uppercase tracking-wide mb-3">
    System Telemetry
  </h3>
  <div className="space-y-2 text-xs font-mono">
    {/* Logs */}
  </div>
</div>
```

---

### 2.4 Execute Button - Standard Size
**BEFORE (Current - Too Big):**
```tsx
<button className="h-16 px-12 rounded-2xl text-[14px] ...">
  Execute Synthesis
</button>
```

**AFTER (Standard):**
```tsx
<button className="h-12 px-8 rounded-lg text-sm font-semibold ...">
  Execute Synthesis
</button>
```

---

## 📚 **Phase 3: Fix Library/Vault Sizing (30 min)**

### 3.1 Video Card Grid - Compact
**Reference your FileCard.jsx sizing:**

```tsx
/* Video Card - COMPACT LIKE FILE CARD */
<div className="rounded-lg border border-gray-200 bg-white p-4 hover:shadow-md transition-shadow">
  {/* Video thumbnail */}
  <div className="aspect-video rounded-md overflow-hidden mb-3">
    <video src={...} className="w-full h-full object-cover" />
  </div>
  
  {/* Info - COMPACT */}
  <div className="space-y-1">
    <h3 className="text-sm font-semibold truncate">{filename}</h3>
    <p className="text-xs text-gray-500">{size} MB</p>
  </div>
  
  {/* Actions - SMALL BUTTONS */}
  <div className="flex gap-2 mt-3">
    <button className="flex-1 px-3 py-1.5 text-xs font-medium rounded-md bg-indigo-600 text-white">
      <Eye className="h-3 w-3 inline mr-1" />
      View
    </button>
    <button className="px-3 py-1.5 text-xs font-medium rounded-md border border-gray-300">
      <Download className="h-3 w-3" />
    </button>
  </div>
</div>
```

---

### 3.2 Vault Metrics - Compact Cards
```tsx
<div className="grid grid-cols-2 gap-3">
  <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-3">
    <p className="text-xs font-medium text-emerald-600 mb-1">Clip Diversity</p>
    <p className="text-2xl font-bold text-emerald-700">94%</p>
  </div>
  {/* More metrics... */}
</div>
```

---

## 🎨 **Phase 4: Add Features (Judge-Focused) (40 min)**

Now that sizing is fixed, add features with **proper scale**:

### 4.1 System Status Bar - Compact
```tsx
<div className="w-full bg-gray-50 border-b border-gray-200 py-2 px-4">
  <div className="max-w-7xl mx-auto flex items-center justify-between">
    <div className="flex items-center gap-6">
      <StatusBadge label="System" value="Operational" color="green" />
      <StatusBadge label="Gemini" value="Active" color="indigo" />
      <StatusBadge label="Cache" value="36 clips" color="blue" />
    </div>
    <p className="text-xs text-gray-500">Pipeline v7.0</p>
  </div>
</div>

/* StatusBadge - SMALL */
function StatusBadge({ label, value, color }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`h-2 w-2 rounded-full bg-${color}-500`} />
      <span className="text-xs font-medium text-gray-700">
        {label}: <span className="font-semibold">{value}</span>
      </span>
    </div>
  );
}
```

---

### 4.2 Pipeline Modal - Compact
```tsx
<div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
  <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full p-6">
    {/* Header - COMPACT */}
    <div className="text-center mb-6">
      <div className="h-16 w-16 rounded-full bg-indigo-100 mx-auto mb-3 flex items-center justify-center">
        <Sparkles className="h-8 w-8 text-indigo-600" />
      </div>
      <h3 className="text-xl font-bold">{statusMsg}</h3>
    </div>

    {/* Pipeline Stages - COMPACT */}
    <div className="space-y-2 mb-6">
      <PipelineStage name="Validation" status="complete" time="0.2s" />
      <PipelineStage name="Reference Analysis" status="active" badge="GEMINI" />
      {/* ... */}
    </div>

    {/* Progress Bar - STANDARD */}
    <div className="mb-4">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-600">Progress</span>
        <span className="font-semibold">{Math.round(progress)}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div 
          className="h-full bg-indigo-600 transition-all"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  </div>
</div>

/* PipelineStage - COMPACT */
function PipelineStage({ name, status, badge, time }) {
  return (
    <div className="flex items-center gap-3 py-2 px-3 rounded-lg bg-gray-50">
      {status === 'complete' && <CheckCircle className="h-4 w-4 text-green-500" />}
      {status === 'active' && <Loader className="h-4 w-4 text-indigo-500 animate-spin" />}
      {status === 'pending' && <div className="h-4 w-4 rounded-full border-2 border-gray-300" />}
      
      <span className="text-sm font-medium flex-1">{name}</span>
      
      {badge && (
        <span className="text-xs font-semibold text-indigo-600 bg-indigo-100 px-2 py-0.5 rounded">
          {badge}
        </span>
      )}
      
      {time && <span className="text-xs text-gray-500 font-mono">{time}</span>}
    </div>
  );
}
```

---

### 4.3 X-Ray Metrics - Compact
```tsx
<div className="grid grid-cols-2 gap-3 mb-6">
  <MetricCard
    title="Clip Diversity"
    value="94%"
    status="excellent"
    icon={<Layers className="h-4 w-4" />}
  />
  {/* More metrics... */}
</div>

function MetricCard({ title, value, status, icon }) {
  const colors = {
    excellent: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    good: 'border-blue-200 bg-blue-50 text-blue-700',
    fair: 'border-amber-200 bg-amber-50 text-amber-700'
  };

  return (
    <div className={`rounded-lg border p-3 ${colors[status]}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium opacity-70">{title}</span>
        <div className="opacity-50">{icon}</div>
      </div>
      <p className="text-2xl font-bold">{value}</p>
    </div>
  );
}
```

---

### 4.4 EDL Visualization - Compact List
```tsx
<div className="space-y-2">
  {edl.decisions.slice(0, 6).map((decision, i) => (
    <div key={i} className="rounded-lg border border-gray-200 bg-white p-3">
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-indigo-600 bg-indigo-100 px-2 py-0.5 rounded">
            #{i + 1}
          </span>
          <span className="text-sm font-medium">{clipName}</span>
        </div>
        <span className="text-xs text-gray-500 font-mono">
          {decision.timeline_start.toFixed(1)}s - {decision.timeline_end.toFixed(1)}s
        </span>
      </div>
      
      {decision.reasoning && (
        <p className="text-xs text-gray-600 mt-2">{decision.reasoning}</p>
      )}
    </div>
  ))}
</div>
```

---

## 📋 **Revised Implementation Checklist**

### Phase 1: Fix Sizing (30 min) - CRITICAL
- [ ] Reset typography scale to website-appropriate sizes
- [ ] Fix spacing scale (compact, not spread out)
- [ ] Update component size standards
- [ ] Test across all pages

### Phase 2: Fix Studio Page (40 min)
- [ ] Compact hero section
- [ ] Smaller dropzone cards
- [ ] Compact telemetry sidebar
- [ ] Standard-sized execute button
- [ ] Test layout

### Phase 3: Fix Library/Vault (30 min)
- [ ] Compact video card grid (like FileCard)
- [ ] Smaller vault metrics
- [ ] Compact EDL list
- [ ] Test responsiveness

### Phase 4: Add Features (40 min)
- [ ] Compact system status bar
- [ ] Compact pipeline modal
- [ ] Compact X-Ray metrics
- [ ] Compact EDL visualization

### Phase 5: Backend (10 min)
- [ ] Add EDL to session data (1 line)
- [ ] (Optional) Add cache stats endpoint

### Phase 6: Polish (20 min)
- [ ] Consistent spacing across pages
- [ ] Smooth transitions
- [ ] Hover states
- [ ] Final testing

---

## ⏱️ **Revised Timeline**

| Phase | Duration | Priority |
|-------|----------|----------|
| Fix Sizing | 30 min | **CRITICAL** |
| Fix Studio | 40 min | High |
| Fix Library/Vault | 30 min | High |
| Add Features | 40 min | Medium |
| Backend | 10 min | Medium |
| Polish | 20 min | Low |
| **Total** | **170 min (2h 50min)** | - |

---

## 🎯 **Key Sizing Principles**

### DO ✅
- Use 1rem (16px) as body text baseline
- Keep buttons 0.75rem - 1rem padding
- Use 0.5rem - 1rem gaps between elements
- Keep cards compact (1rem padding)
- Use 8px - 12px border radius
- Make headers 1.5x - 2.5x body size

### DON'T ❌
- Don't use text-4xl for page titles (too big)
- Don't use 3rem+ spacing between sections
- Don't use 2rem+ padding in cards
- Don't use rounded-[2rem] (too rounded)
- Don't make buttons h-16 (too tall)
- Don't use tracking-[0.4em] everywhere (too spaced)

---

## 🚀 **Let's Start**

**I'll begin with Phase 1: Fix Sizing Foundation**

This is the most critical phase - once sizing is fixed, everything else will look professional.

**Ready to proceed?**
