# 🏗️ MIMIC Frontend Architecture Guide

## 📁 Folder Structure (Best Practices)

```
frontend/
├── src/
│   ├── pages/              # Page Components (Logic Only - No Styling)
│   │   ├── StudioPage.tsx
│   │   ├── AssetsPage.tsx
│   │   └── ProjectsPage.tsx
│   │
│   ├── styles/             # Page-Specific Styles (CSS Modules)
│   │   ├── StudioPage.module.css
│   │   ├── AssetsPage.module.css
│   │   └── ProjectsPage.module.css
│   │
│   ├── components/         # Reusable Components
│   │   ├── Header/
│   │   │   ├── Header.tsx
│   │   │   └── Header.module.css
│   │   ├── UploadZone/
│   │   │   ├── UploadZone.tsx
│   │   │   └── UploadZone.module.css
│   │   └── ui/             # Shadcn UI components
│   │
│   ├── lib/                # Utilities & Helpers
│   │   ├── utils.ts
│   │   └── api.ts          # API calls centralized
│   │
│   └── types/              # TypeScript Types
│       └── index.ts
│
├── app/                    # Next.js App Router (Routes Only)
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home route (imports StudioPage)
│   ├── assets/
│   │   └── page.tsx        # Assets route (imports AssetsPage)
│   ├── projects/
│   │   └── page.tsx        # Projects route (imports ProjectsPage)
│   └── globals.css         # Global styles only
│
└── public/                 # Static assets
```

## 🎯 Key Principles

### 1. **Separation of Concerns**
- **Pages** (`src/pages/`): Pure logic, state management, data fetching
- **Styles** (`src/styles/`): All visual styling in CSS modules
- **Routes** (`app/`): Thin wrappers that import from `src/pages/`

### 2. **CSS Modules Benefits**
```tsx
// ✅ GOOD: Clean, maintainable
import styles from '@/styles/StudioPage.module.css';

<div className={styles.container}>
  <h1 className={styles.title}>Studio</h1>
</div>
```

```tsx
// ❌ BAD: Hard to maintain
<div className="min-h-screen flex flex-col items-center p-6 md:p-12 pb-40">
  <h1 className="text-4xl md:text-5xl font-black tracking-tighter">Studio</h1>
</div>
```

### 3. **Component Structure**
Each component gets its own folder:
```
Header/
├── Header.tsx          # Component logic
├── Header.module.css   # Component styles
└── index.ts            # Export barrel
```

### 4. **API Centralization**
```typescript
// src/lib/api.ts
export const api = {
  uploadFiles: async (ref: File, clips: File[]) => { ... },
  fetchResults: async () => { ... },
  fetchReferences: async () => { ... }
}
```

## 🔄 Migration Strategy

1. Create page components in `src/pages/`
2. Extract styles to `src/styles/` CSS modules
3. Update `app/` routes to import from `src/pages/`
4. Move reusable components to `src/components/`
5. Centralize API calls in `src/lib/api.ts`

## 📝 Example: Before & After

### Before (Current)
```tsx
// app/page.tsx - 300 lines of mixed logic and styling
export default function Home() {
  const [refFile, setRefFile] = useState<File | null>(null);
  // ... 50 lines of logic
  
  return (
    <div className="min-h-screen bg-black/5 overflow-x-hidden p-6 md:p-12">
      <div className="w-full max-w-[1240px] space-y-12">
        {/* ... 200 lines of JSX with inline Tailwind */}
      </div>
    </div>
  );
}
```

### After (Refactored)
```tsx
// app/page.tsx - Clean route wrapper
import StudioPage from '@/pages/StudioPage';
export default StudioPage;
```

```tsx
// src/pages/StudioPage.tsx - Pure logic
import styles from '@/styles/StudioPage.module.css';
import { useStudioLogic } from '@/hooks/useStudioLogic';

export default function StudioPage() {
  const { refFile, materialFiles, handleUpload, startSynthesis } = useStudioLogic();
  
  return (
    <div className={styles.container}>
      <div className={styles.content}>
        {/* Clean JSX with semantic class names */}
      </div>
    </div>
  );
}
```

```css
/* src/styles/StudioPage.module.css - All styling here */
.container {
  min-height: 100vh;
  background: rgba(0, 0, 0, 0.05);
  overflow-x: hidden;
  padding: 1.5rem 3rem;
}

.content {
  width: 100%;
  max-width: 1240px;
  display: flex;
  flex-direction: column;
  gap: 3rem;
}
```

## 🎨 Styling Strategy

1. **Global Styles** (`app/globals.css`): Theme, animations, utilities
2. **Page Styles** (`src/styles/*.module.css`): Page-specific layouts
3. **Component Styles** (`src/components/*/**.module.css`): Component-specific
4. **Tailwind**: Only for utility classes (spacing, colors) - NOT layout

## 🚀 Benefits

✅ **Easier to Debug**: Find styles quickly in dedicated CSS files
✅ **Better Collaboration**: Designers can edit CSS without touching logic
✅ **Maintainability**: Change layout without risking breaking logic
✅ **Performance**: CSS modules are optimized and scoped
✅ **Scalability**: Clear structure as project grows
✅ **Type Safety**: Import styles as typed objects
