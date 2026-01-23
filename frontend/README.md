# 🎯 MIMIC Frontend - Final Structure

## ✅ What We Have

A **clean, pragmatic frontend** that's easy to work with for both humans and AI.

---

## 📁 Structure

```
frontend/
├── app/                        # Pages (Next.js App Router)
│   ├── page.tsx               # Studio (home)
│   ├── gallery/page.tsx       # Assets library
│   ├── vault/page.tsx         # Projects archive
│   ├── layout.tsx             # Root layout + Header
│   └── globals.css            # Global styles + reusable classes
│
├── lib/                        # Utilities
│   ├── api.ts                 # ✅ Centralized API client
│   ├── types.ts               # ✅ TypeScript types
│   └── utils.ts               # Helper functions
│
└── components/                 # UI Components
    ├── Header.tsx             # Navigation
    └── ui/                    # Shadcn components
```

---

## 🎯 Key Principles

### **1. Pages in `app/`**
- Use Tailwind inline for fast iteration
- Keep logic and JSX together
- Extract to components when used 3+ times

### **2. API Calls in `lib/api.ts`**
- **Never** duplicate fetch calls
- All backend communication centralized
- Easy to change endpoints

### **3. Types in `lib/types.ts`**
- Type safety across the app
- Shared interfaces

### **4. Reusable Styles in `globals.css`**
- Use `.module`, `.module-active-indigo`, etc.
- Avoid repeating complex patterns

---

## 📝 How to Add a Feature

### **Example: Add a new page**

```tsx
// app/new-page/page.tsx
"use client";

import { useState, useEffect } from "react";
import { api } from "@/lib/api";
import type { SomeType } from "@/lib/types";

export default function NewPage() {
  const [data, setData] = useState<SomeType[]>([]);

  useEffect(() => {
    api.fetchSomething().then(res => setData(res.data));
  }, []);

  return (
    <div className="min-h-screen p-8">
      <h1 className="text-4xl font-black mb-8">New Page</h1>
      {/* Your content */}
    </div>
  );
}
```

### **Example: Add an API call**

```typescript
// lib/api.ts
export const api = {
  // ... existing calls
  
  fetchSomething: async () => {
    const res = await fetch(`${API_BASE}/api/something`);
    if (!res.ok) throw new Error("Failed");
    return res.json();
  },
};
```

### **Example: Add a type**

```typescript
// lib/types.ts
export interface SomeType {
  id: string;
  name: string;
  // ...
}
```

---

## 🚀 Benefits

✅ **Fast Iteration** - Change Tailwind classes, see results immediately
✅ **No Duplication** - API calls centralized
✅ **Type Safe** - TypeScript everywhere
✅ **Simple** - No complex folder structure
✅ **Scalable** - Easy to add features

---

## 🔍 Current Pages

| Page | Route | Purpose |
|------|-------|---------|
| **Studio** | `/` | Upload reference & clips, start synthesis |
| **Assets** | `/gallery` | Browse/manage uploaded clips |
| **Projects** | `/vault` | View synthesized videos |

---

## 💡 Notes

- **Lint warnings about `@apply`**: Ignore them - they're just CSS editor warnings, Tailwind works fine
- **Inline Tailwind**: Yes, it's intentional - faster for prototyping
- **API centralization**: This is the most important part - never duplicate fetch calls

---

**Status**: ✅ Working
**Last Updated**: January 23, 2026
**Ready for**: Hackathon development 🚀
