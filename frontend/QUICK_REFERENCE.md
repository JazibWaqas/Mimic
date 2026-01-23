# 🚀 Quick Reference - Frontend Structure

## 📁 Where Things Go

| What | Where | Example |
|------|-------|---------|
| **Page Logic** | `src/pages/` | `StudioPage.tsx` |
| **Page Styles** | `src/styles/` | `StudioPage.module.css` |
| **Routes** | `app/` | `page.tsx` (imports from src/pages) |
| **Components** | `src/components/` | `Header/Header.tsx` |
| **Utilities** | `src/lib/` | `utils.ts`, `api.ts` |
| **Types** | `src/types/` | `index.ts` |
| **Global Styles** | `app/` | `globals.css` |

## ✏️ Common Tasks

### **Create a New Page**
```bash
# 1. Create page component
touch src/pages/NewPage.tsx

# 2. Create styles
touch src/styles/NewPage.module.css

# 3. Create route
mkdir app/new-page
touch app/new-page/page.tsx
```

### **Edit Existing Page**
```bash
# Edit logic:
code src/pages/StudioPage.tsx

# Edit styles:
code src/styles/StudioPage.module.css
```

### **Create a Component**
```bash
# Create folder
mkdir src/components/MyComponent

# Create files
touch src/components/MyComponent/MyComponent.tsx
touch src/components/MyComponent/MyComponent.module.css
touch src/components/MyComponent/index.ts
```

## 📝 Code Templates

### **Page Component Template**
```tsx
// src/pages/MyPage.tsx
"use client";

import { useState } from "react";
import styles from "@/src/styles/MyPage.module.css";

export default function MyPage() {
  const [state, setState] = useState();

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>My Page</h1>
    </div>
  );
}
```

### **CSS Module Template**
```css
/* src/styles/MyPage.module.css */

.container {
  min-height: 100vh;
  padding: 2rem;
}

.title {
  font-size: 2rem;
  font-weight: bold;
}
```

### **Route Template**
```tsx
// app/my-page/page.tsx
import MyPage from "@/src/pages/MyPage";
export default MyPage;
```

### **Component Template**
```tsx
// src/components/MyComponent/MyComponent.tsx
import styles from "./MyComponent.module.css";

interface MyComponentProps {
  title: string;
}

export default function MyComponent({ title }: MyComponentProps) {
  return (
    <div className={styles.container}>
      <h2 className={styles.title}>{title}</h2>
    </div>
  );
}
```

```tsx
// src/components/MyComponent/index.ts
export { default } from "./MyComponent";
```

## 🎨 Styling Patterns

### **Basic Styling**
```tsx
<div className={styles.container}>
```

### **Conditional Styling**
```tsx
<div className={`${styles.card} ${isActive ? styles.cardActive : ""}`}>
```

### **Multiple Classes**
```tsx
<div className={`${styles.container} ${styles.dark} ${styles.large}`}>
```

### **With Tailwind Utilities** (for spacing/colors only)
```tsx
<div className={`${styles.container} p-4 bg-black/5`}>
```

## 🔍 Finding Things

| I want to... | Look in... |
|--------------|-----------|
| Change page layout | `src/styles/[PageName].module.css` |
| Add new feature | `src/pages/[PageName].tsx` |
| Fix a bug | `src/pages/[PageName].tsx` |
| Change colors/theme | `app/globals.css` |
| Add API call | `src/lib/api.ts` |
| Create type | `src/types/index.ts` |
| Reuse component | `src/components/` |

## 🐛 Debugging

### **Styles Not Applying?**
1. Check import: `import styles from "@/src/styles/MyPage.module.css"`
2. Check class name: `className={styles.myClass}` (not `className="myClass"`)
3. Check CSS file has `.myClass { ... }`
4. Restart dev server: `npm run dev`

### **Module Not Found?**
1. Check path starts with `@/src/`
2. Check file exists
3. Check file extension (`.tsx` vs `.ts`)

### **Hot Reload Not Working?**
1. Save both `.tsx` and `.module.css` files
2. Check terminal for errors
3. Restart dev server

## 📚 Import Patterns

```tsx
// Pages
import StudioPage from "@/src/pages/StudioPage";

// Styles
import styles from "@/src/styles/StudioPage.module.css";

// Components
import Header from "@/src/components/Header";

// Utilities
import { cn } from "@/src/lib/utils";
import { api } from "@/src/lib/api";

// Types
import type { Result, Reference } from "@/src/types";

// UI Components (existing)
import { Button } from "@/components/ui/button";
```

## 🎯 Best Practices

### **DO** ✅
- Separate logic from styling
- Use semantic class names (`.heroSection`, not `.blueBox`)
- Group related styles together
- Comment complex CSS
- Extract reusable patterns to components

### **DON'T** ❌
- Mix Tailwind classes for layout (use CSS modules)
- Put styles in TSX files
- Use generic class names (`.container1`, `.box`)
- Duplicate styles across files
- Hardcode values (use CSS variables)

## 🔗 Quick Links

- **Architecture Guide**: `ARCHITECTURE.md`
- **Migration Summary**: `REFACTORING_SUMMARY.md`
- **Structure Guide**: `STRUCTURE_GUIDE.md`
- **This File**: `QUICK_REFERENCE.md`

---

**Print this and keep it handy! 📌**
