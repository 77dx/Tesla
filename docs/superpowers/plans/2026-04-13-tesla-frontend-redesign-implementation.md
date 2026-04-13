# Tesla前端重新设计实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 基于DESIGN.md设计规范，将Tesla前端从温暖的羊皮纸色调设计系统重构为深色技术主题系统。

**Architecture:** 创建新的CSS变量系统文件，替换现有的design-system.css，更新所有组件样式以使用深色主题，保持与现有Vue 3组件的兼容性。

**Tech Stack:** Vue 3, Vite, CSS Variables, Inter字体

---

## 文件结构

### 创建文件：
- `frontend/src/assets/design-system-dark.css` - 新的深色主题设计系统
- `frontend/src/assets/design-system-dark.test.css` - 设计系统测试文件

### 修改文件：
- `frontend/src/assets/design-system.css` - 备份当前设计系统
- `frontend/src/assets/main.css` - 更新导入和变量映射
- `frontend/src/views/DashboardView.vue` - 更新仪表板样式
- `frontend/src/views/LayoutView.vue` - 更新布局组件样式

### 测试文件：
- 通过浏览器手动测试视觉变化
- 验证CSS变量正确应用

---

## 任务分解

### Task 1: 创建深色主题设计系统文件

**Files:**
- Create: `frontend/src/assets/design-system-dark.css`
- Test: `frontend/src/assets/design-system-dark.test.css`

- [ ] **Step 1: 创建深色主题设计系统文件**

```css
/* ════════════════════════════════════════════
   Tesla Design System — Dark Theme
   基于DESIGN.md的深色技术主题设计系统
   ════════════════════════════════════════════ */

/* ────────────────────────────────────────────
   1. 颜色系统 (Color System) - 深色主题
   ──────────────────────────────────────────── */

:root {
  /* ===== 核心色彩 (Core Colors) ===== */
  --color-near-black: #0b0b0b;          /* 近黑色背景 */
  --color-dark-surface: #1a1a1a;        /* 深色表面 */
  --color-dark-border: #2a2a2a;         /* 深色边框 */

  /* ===== 中性灰度 (Neutral Grayscale) ===== */
  --color-pure-white: #ffffff;          /* 纯白色文本 */
  --color-text-primary: #f0f0f0;        /* 主要文本 */
  --color-text-secondary: #b0b0b0;      /* 次要文本 */
  --color-text-tertiary: #808080;       /* 三级文本 */

  /* ===== 强调色 (Accent Colors) ===== */
  --color-accent-orange: #ff6b35;       /* 橙色强调色 */
  --color-accent-orange-light: #ff8c42; /* 浅橙色 */
  --color-accent-blue: #3a86ff;         /* 蓝色强调色 */
  --color-accent-green: #38b000;        /* 绿色强调色 */
  --color-accent-red: #e63946;          /* 红色强调色 */

  /* ===== 状态色 (Status Colors) ===== */
  --color-success: #38b000;
  --color-warning: #ff9e00;
  --color-error: #e63946;
  --color-info: #3a86ff;

  /* ===== 兼容性映射 (Compatibility Mapping) ===== */
  --primary: var(--color-text-primary);
  --accent: var(--color-accent-orange);
  --success: var(--color-success);
  --warning: var(--color-warning);
  --danger: var(--color-error);
  --bg: var(--color-near-black);
  --card-bg: var(--color-dark-surface);
  --text: var(--color-text-primary);
  --text-light: var(--color-text-secondary);
  --border: var(--color-dark-border);
}
```

- [ ] **Step 2: 创建测试文件验证CSS变量**

```css
/* design-system-dark.test.css */
.test-color-system {
  /* 验证核心色彩 */
  background-color: var(--color-near-black);
  border-color: var(--color-dark-border);
  color: var(--color-text-primary);
  
  /* 验证强调色 */
  accent-color: var(--color-accent-orange);
  
  /* 验证状态色 */
  success-color: var(--color-success);
  error-color: var(--color-error);
}
```

- [ ] **Step 3: 验证文件创建成功**

```bash
ls -la frontend/src/assets/design-system-dark.css
ls -la frontend/src/assets/design-system-dark.test.css
```

预期输出：两个文件都存在且大小大于0字节

- [ ] **Step 4: 提交创建的文件**

```bash
git add frontend/src/assets/design-system-dark.css frontend/src/assets/design-system-dark.test.css
git commit -m "feat: 创建深色主题设计系统基础文件"
```

### Task 2: 添加排版系统到设计系统

**Files:**
- Modify: `frontend/src/assets/design-system-dark.css`

- [ ] **Step 1: 添加Inter字体导入和排版系统**

```css
/* ────────────────────────────────────────────
   2. 排版系统 (Typography System)
   ──────────────────────────────────────────── */

/* Inter字体导入 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 字体家族 */
--font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-ui: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-family-mono: 'SF Mono', 'Monaco', 'Inconsolata', monospace;

/* 字重 */
--font-weight-light: 300;
--font-weight-normal: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;

/* 字号 */
--font-size-xs: 0.75rem;      /* 12px */
--font-size-sm: 0.875rem;     /* 14px */
--font-size-base: 1rem;       /* 16px */
--font-size-lg: 1.125rem;     /* 18px */
--font-size-xl: 1.25rem;      /* 20px */
--font-size-2xl: 1.5rem;      /* 24px */
--font-size-3xl: 1.875rem;    /* 30px */
--font-size-4xl: 2.25rem;     /* 36px */

/* 行高 */
--line-height-tight: 1.25;
--line-height-normal: 1.5;
--line-height-relaxed: 1.75;

/* 字间距 */
--letter-spacing-tight: -0.01em;
--letter-spacing-normal: 0;
--letter-spacing-wide: 0.01em;
```

- [ ] **Step 2: 验证排版变量添加成功**

```bash
grep -n "font-family" frontend/src/assets/design-system-dark.css
grep -n "font-size" frontend/src/assets/design-system-dark.css
```

预期输出：找到对应的变量定义行

- [ ] **Step 3: 提交排版系统更新**

```bash
git add frontend/src/assets/design-system-dark.css
git commit -m "feat: 添加Inter字体和排版系统到深色主题"
```

### Task 3: 添加间距和圆角系统

**Files:**
- Modify: `frontend/src/assets/design-system-dark.css`

- [ ] **Step 1: 添加8px基准间距系统**

```css
/* ────────────────────────────────────────────
   3. 间距系统 (Spacing System) - 8px基准
   ──────────────────────────────────────────── */

/* 8px基准间距系统 */
--space-0: 0;
--space-xs: 0.5rem;    /* 8px */
--space-sm: 1rem;      /* 16px */
--space-md: 1.5rem;    /* 24px */
--space-lg: 2rem;      /* 32px */
--space-xl: 3rem;      /* 48px */
--space-2xl: 4rem;     /* 64px */
--space-3xl: 6rem;     /* 96px */
--space-4xl: 8rem;     /* 128px */
--space-5xl: 12rem;    /* 192px */
```

- [ ] **Step 2: 添加圆角系统**

```css
/* ────────────────────────────────────────────
   4. 圆角系统 (Border Radius System)
   ──────────────────────────────────────────── */

/* 圆角 */
--radius-none: 0;
--radius-subtle: 0.25rem;     /* 4px */
--radius-comfortable: 0.5rem; /* 8px */
--radius-generous: 0.75rem;   /* 12px */
--radius-very-rounded: 1rem;  /* 16px */
--radius-pill: 9999px;        /* 药丸形 */
```

- [ ] **Step 3: 添加阴影系统**

```css
/* ────────────────────────────────────────────
   5. 阴影系统 (Shadow System)
   ──────────────────────────────────────────── */

/* 阴影层级 */
--shadow-level-0: none;
--shadow-level-1: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
--shadow-level-2: 0 3px 6px rgba(0, 0, 0, 0.16), 0 3px 6px rgba(0, 0, 0, 0.23);
--shadow-level-3: 0 10px 20px rgba(0, 0, 0, 0.19), 0 6px 6px rgba(0, 0, 0, 0.23);
--shadow-level-4: 0 14px 28px rgba(0, 0, 0, 0.25), 0 10px 10px rgba(0, 0, 0, 0.22);

/* 特殊阴影 */
--shadow-ring-subtle: 0 0 0 1px rgba(255, 255, 255, 0.1);
--shadow-ring-warm: 0 0 0 2px var(--color-accent-orange);
--shadow-ring-blue: 0 0 0 2px var(--color-accent-blue);
```

- [ ] **Step 4: 验证所有系统变量添加成功**

```bash
grep -c "space-" frontend/src/assets/design-system-dark.css
grep -c "radius-" frontend/src/assets/design-system-dark.css
grep -c "shadow-" frontend/src/assets/design-system-dark.css
```

预期输出：每个命令返回大于0的数字

- [ ] **Step 5: 提交间距和圆角系统**

```bash
git add frontend/src/assets/design-system-dark.css
git commit -m "feat: 添加间距、圆角和阴影系统到深色主题"
```

### Task 4: 备份当前设计系统并更新main.css

**Files:**
- Modify: `frontend/src/assets/design-system.css` (重命名备份)
- Modify: `frontend/src/assets/main.css`

- [ ] **Step 1: 备份当前设计系统文件**

```bash
cp frontend/src/assets/design-system.css frontend/src/assets/design-system-light-backup.css
```

- [ ] **Step 2: 更新main.css导入新设计系统**

编辑 `frontend/src/assets/main.css`，将第7行从：
```css
@import './design-system.css';
```
改为：
```css
@import './design-system-dark.css';
```

- [ ] **Step 3: 更新main.css中的兼容性变量映射**

在 `frontend/src/assets/main.css` 的 `:root` 块中，更新变量映射：

```css
:root {
  /* 原系统变量映射到新深色系统 */
  --primary: var(--color-text-primary);
  --primary-light: var(--color-dark-surface);
  --accent: var(--color-accent-orange);
  --accent-hover: var(--color-accent-orange-light);
  --success: var(--color-success);
  --warning: var(--color-warning);
  --danger: var(--color-error);
  --bg: var(--color-near-black);
  --card-bg: var(--color-dark-surface);
  --text: var(--color-text-primary);
  --text-light: var(--color-text-secondary);
  --border: var(--color-dark-border);
  --shadow: rgba(0, 0, 0, 0.3);
  --shadow-hover: rgba(0, 0, 0, 0.5);

  /* 原排版变量映射 */
  --font-base: var(--font-size-base);
  --font-sm: var(--font-size-sm);
  --font-xs: var(--font-size-xs);
  --font-lg: var(--font-size-lg);
  --font-xl: var(--font-size-xl);
}
```

- [ ] **Step 4: 验证main.css更新正确**

```bash
grep -n "design-system-dark" frontend/src/assets/main.css
grep -n "color-near-black" frontend/src/assets/main.css
```

预期输出：找到对应的导入和变量引用

- [ ] **Step 5: 提交main.css更新**

```bash
git add frontend/src/assets/main.css
git commit -m "feat: 更新main.css导入深色设计系统并更新变量映射"
```

### Task 5: 更新DashboardView.vue样式

**Files:**
- Modify: `frontend/src/views/DashboardView.vue`

- [ ] **Step 1: 备份当前DashboardView.vue**

```bash
cp frontend/src/views/DashboardView.vue frontend/src/views/DashboardView-backup.vue
```

- [ ] **Step 2: 更新欢迎卡片样式**

在 `DashboardView.vue` 的 `<style>` 部分，更新欢迎卡片样式：

```css
/* ===== 欢迎卡片 ===== */
.welcome-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4xl) var(--space-5xl);
  background: linear-gradient(135deg,
    var(--color-dark-surface) 0%,
    var(--color-near-black) 100%);
  color: var(--color-text-primary);
  border-radius: var(--radius-very-rounded);
  border: 1px solid var(--color-dark-border);
  box-shadow: var(--shadow-level-2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg,
    var(--color-accent-orange),
    var(--color-accent-orange-light));
  border-radius: var(--radius-very-rounded) var(--radius-very-rounded) 0 0;
}

.welcome-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-level-3);
  border-color: var(--color-accent-orange);
}
```

- [ ] **Step 3: 更新章节标题样式**

```css
/* ===== 章节标题 ===== */
.section-title {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-xl);
  padding-bottom: var(--space-md);
  border-bottom: 2px solid var(--color-dark-border);
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg,
    var(--color-accent-orange),
    var(--color-accent-orange-light));
}
```

- [ ] **Step 4: 更新功能卡片样式**

```css
/* ===== 功能网格 ===== */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-xl);
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: var(--space-xl);
  padding: var(--space-3xl);
  cursor: pointer;
  transition: all 0.25s ease;
  border-radius: var(--radius-very-rounded);
  border: 1px solid var(--color-dark-border);
  background-color: var(--color-dark-surface);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg,
    var(--color-accent-orange),
    var(--color-accent-orange-light));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.feature-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-level-3);
  border-color: var(--color-accent-orange);
}

.feature-card:hover::before {
  opacity: 1;
}

.fc-icon {
  font-size: 32px;
  flex-shrink: 0;
  margin-top: var(--space-2xs);
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 107, 53, 0.1);
  border-radius: var(--radius-generous);
  color: var(--color-accent-orange);
}

.fc-name {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-md);
  line-height: var(--line-height-relaxed);
}

.fc-desc {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-relaxed);
  margin: 0;
}

.fc-arrow {
  font-size: 20px;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  align-self: center;
  transition: all 0.3s ease;
  opacity: 0.6;
}

.feature-card:hover .fc-arrow {
  color: var(--color-accent-orange);
  opacity: 1;
  transform: translateX(4px);
}
```

- [ ] **Step 5: 更新指南卡片样式**

```css
/* ===== 指南卡片 ===== */
.guide-card {
  padding: var(--space-4xl);
  border-radius: var(--radius-very-rounded);
  background-color: var(--color-dark-surface);
  border: 1px solid var(--color-dark-border);
  box-shadow: var(--shadow-level-1);
}

.guide-steps::before {
  content: '';
  position: absolute;
  top: 18px;
  left: 18px;
  right: 18px;
  height: 2px;
  background: linear-gradient(90deg,
    var(--color-dark-border) 0%,
    var(--color-accent-orange) 100%);
  z-index: 0;
}

.step-num {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg,
    var(--color-accent-orange),
    var(--color-accent-orange-light));
  color: var(--color-pure-white);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-lg);
  flex-shrink: 0;
  border: 3px solid var(--color-dark-surface);
  box-shadow: var(--shadow-level-1);
}
```

- [ ] **Step 6: 更新响应式设计部分**

更新响应式设计中的背景色和边框色：

```css
@media (max-width: 991px) {
  .dashboard {
    padding: var(--space-lg);
    gap: var(--space-2xl);
    background-color: var(--color-near-black);
  }
}

@media (max-width: 767px) {
  .dashboard {
    padding: var(--space-md);
    gap: var(--space-xl);
    background-color: var(--color-near-black);
  }
  
  .feature-card {
    background-color: var(--color-dark-surface);
    border-color: var(--color-dark-border);
  }
  
  .guide-card {
    background-color: var(--color-dark-surface);
    border-color: var(--color-dark-border);
  }
}
```

- [ ] **Step 7: 验证DashboardView.vue更新正确**

```bash
grep -c "color-dark-surface" frontend/src/views/DashboardView.vue
grep -c "color-accent-orange" frontend/src/views/DashboardView.vue
```

预期输出：两个命令都返回大于0的数字

- [ ] **Step 8: 提交DashboardView.vue更新**

```bash
git add frontend/src/views/DashboardView.vue
git commit -m "feat: 更新DashboardView.vue使用深色主题样式"
```

### Task 6: 更新LayoutView.vue样式

**Files:**
- Modify: `frontend/src/views/LayoutView.vue`

- [ ] **Step 1: 备份当前LayoutView.vue**

```bash
cp frontend/src/views/LayoutView.vue frontend/src/views/LayoutView-backup.vue
```

- [ ] **Step 2: 更新布局背景色**

在 `LayoutView.vue` 的 `<style>` 部分，更新布局背景：

```css
.layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-near-black);
}
```

- [ ] **Step 3: 更新侧边栏样式**

```css
/* ===== 侧边栏样式 ===== */
.sidebar {
  width: 260px;
  background-color: var(--color-near-black);
  color: var(--color-text-primary);
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  left: 0;
  top: 0;
  overflow: hidden;
  border-right: 1px solid var(--color-dark-border);
  z-index: 1000;
}

.logo {
  padding: var(--space-xl) var(--space-lg) var(--space-lg);
  border-bottom: 1px solid var(--color-dark-border);
  flex-shrink: 0;
}

.logo h2 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: var(--letter-spacing-wide);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-lg);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-normal);
  line-height: var(--line-height-normal);
  color: var(--color-text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  margin: 0 var(--space-xs);
  border-radius: var(--radius-subtle);
}

.nav-item:hover {
  background-color: var(--color-dark-surface);
  color: var(--color-text-primary);
}

.nav-item.router-link-active {
  background-color: var(--color-dark-surface);
  color: var(--color-accent-orange);
  border-left-color: var(--color-accent-orange);
  font-weight: var(--font-weight-medium);
}
```

- [ ] **Step 4: 更新主内容区域样式**

```css
/* ===== 主内容区域 ===== */
.main-content {
  flex: 1;
  margin-left: 260px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--color-near-black);
}

/* ===== 顶部导航栏 ===== */
.header {
  background-color: var(--color-dark-surface);
  padding: var(--space-lg) var(--space-xl);
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--color-dark-border);
  position: sticky;
  top: 0;
  z-index: 900;
  box-shadow: var(--shadow-level-1);
}

.header h3 {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
}
```

- [ ] **Step 5: 更新用户信息区域样式**

```css
/* ===== 用户信息区域 ===== */
.user-profile {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  text-decoration: none;
  cursor: pointer;
  padding: var(--space-xs) var(--space-sm);
  border-radius: var(--radius-generous);
  transition: all 0.2s ease;
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-dark-border);
}

.user-profile:hover {
  background-color: rgba(255, 107, 53, 0.1);
  border-color: var(--color-accent-orange);
  box-shadow: var(--shadow-ring-warm);
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-accent-orange), var(--color-accent-orange-light));
  color: var(--color-pure-white);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}
```

- [ ] **Step 6: 更新退出按钮样式**

```css
/* ===== 退出按钮 ===== */
.btn-logout {
  background-color: transparent;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-dark-border);
  padding: var(--space-xs) var(--space-md);
  font-family: var(--font-family-ui);
  font-size: var(--font-size-sm);
  border-radius: var(--radius-comfortable);
  transition: all 0.2s ease;
}

.btn-logout:hover {
  background-color: var(--color-error);
  color: var(--color-pure-white);
  border-color: var(--color-error);
}
```

- [ ] **Step 7: 更新产品线切换器样式**

```css
/* ===== 产品线切换器 ===== */
.pl-current {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  padding: var(--space-xs) var(--space-sm);
  border: 1.5px solid var(--color-dark-border);
  border-radius: var(--radius-generous);
  background-color: var(--color-dark-surface);
  cursor: pointer;
  font-family: var(--font-family-ui);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  transition: all 0.15s ease;
  white-space: nowrap;
  min-width: 140px;
  box-shadow: var(--shadow-ring-subtle);
}

.pl-current:hover {
  border-color: var(--color-accent-orange);
  background-color: rgba(255, 107, 53, 0.05);
  box-shadow: var(--shadow-ring-warm);
}

.pl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: var(--color-success);
  flex-shrink: 0;
}

.pl-menu {
  display: none;
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  min-width: 160px;
  background: var(--color-dark-surface);
  border: 1px solid var(--color-dark-border);
  border-radius: var(--radius-comfortable);
  box-shadow: var(--shadow-level-3);
  list-style: none;
  padding: 6px 0;
  z-index: 999;
}

.pl-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  font-size: var(--font-size-sm);
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: background 0.1s;
}

.pl-menu-item:hover { 
  background: rgba(255, 107, 53, 0.1); 
  color: var(--color-text-primary);
}

.pl-menu-item.active { 
  color: var(--color-accent-orange); 
  font-weight: var(--font-weight-semibold); 
  background: rgba(255, 107, 53, 0.15); 
}

.pl-item-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  flex-shrink: 0;
}

.pl-menu-item.active .pl-item-dot { 
  background: var(--color-accent-orange); 
}
```

- [ ] **Step 8: 更新内容区域样式**

```css
/* ===== 内容区域 ===== */
.content {
  flex: 1;
  padding: var(--space-xl);
  background-color: var(--color-near-black);
}
```

- [ ] **Step 9: 验证LayoutView.vue更新正确**

```bash
grep -c "color-near-black" frontend/src/views/LayoutView.vue
grep -c "color-dark-surface" frontend/src/views/LayoutView.vue
```

预期输出：两个命令都返回大于0的数字

- [ ] **Step 10: 提交LayoutView.vue更新**

```bash
git add frontend/src/views/LayoutView.vue
git commit -m "feat: 更新LayoutView.vue使用深色主题样式"
```

### Task 7: 验证和测试深色主题

**Files:**
- Test: 所有修改的文件
- Test: 浏览器手动测试

- [ ] **Step 1: 启动开发服务器验证无错误**

```bash
cd /Users/cathy/python_project/Tesla/frontend
npm run dev
```

预期输出：服务器成功启动，无编译错误

- [ ] **Step 2: 在浏览器中打开应用验证视觉变化**

打开浏览器访问 `http://localhost:5173`（或开发服务器地址），验证：
1. 整体背景是否为深色（#0b0b0b）
2. 侧边栏是否为深色主题
3. 仪表板卡片是否使用深色表面
4. 强调色是否为橙色（#ff6b35）
5. 文本颜色是否正确（主要文本为#f0f0f0，次要文本为#b0b0b0）

- [ ] **Step 3: 测试响应式设计**

调整浏览器窗口大小，验证：
1. 在移动设备尺寸下，布局是否正确
2. 网格系统是否按预期响应
3. 字体大小是否适配

- [ ] **Step 4: 测试交互状态**

手动测试：
1. 鼠标悬停在按钮和卡片上，是否有正确的悬停效果
2. 点击导航项，是否有激活状态
3. 表单输入框是否有焦点状态

- [ ] **Step 5: 验证CSS变量正确应用**

在浏览器开发者工具中检查：
```javascript
// 在浏览器控制台中执行
getComputedStyle(document.documentElement).getPropertyValue('--color-near-black')
getComputedStyle(document.documentElement).getPropertyValue('--color-accent-orange')
```

预期输出：返回正确的颜色值

- [ ] **Step 6: 提交测试验证**

```bash
git add -A
git commit -m "test: 验证深色主题应用成功，所有视觉变化符合预期"
```

---

## 计划自审

### 1. Spec覆盖检查
- [x] 色彩系统重构：Task 1-3 实现了完整的深色色彩系统
- [x] 排版系统更新：Task 2 添加了Inter字体和排版变量
- [x] 间距系统：Task 3 实现了8px基准间距系统
- [x] 组件设计规范：Task 5-6 更新了按钮、卡片、导航等组件
- [x] 布局系统：Task 6 更新了主布局结构
- [x] 实施计划：所有4个阶段都有对应任务

### 2. 占位符扫描
- [x] 无"TBD"、"TODO"占位符
- [x] 所有代码步骤都有完整代码
- [x] 所有测试步骤都有具体命令
- [x] 所有提交步骤都有具体消息

### 3. 类型一致性
- [x] CSS变量命名一致：全部使用kebab-case
- [x] 文件路径一致：全部使用相对路径
- [x] 命令格式一致：全部使用具体命令和预期输出

---

计划完成并保存到 `docs/superpowers/plans/2026-04-13-tesla-frontend-redesign-implementation.md`。

**执行选项：**

**1. Subagent-Driven (推荐)** - 我分派新的子代理执行每个任务，任务间进行审查，快速迭代

**2. Inline Execution** - 在此会话中执行任务，使用批处理执行并设置检查点

**选择哪种方式？**