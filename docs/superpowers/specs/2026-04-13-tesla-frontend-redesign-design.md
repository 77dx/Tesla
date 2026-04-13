---
title: Tesla前端重新设计 - 基于DESIGN.md的深色主题系统
date: 2026-04-13
status: approved
---

# Tesla前端重新设计设计方案

## 项目概述

基于Tesla项目的DESIGN.md设计规范，将当前温暖的羊皮纸色调设计系统（浅色主题）重构为基于Sanity的深色技术主题系统。

## 设计原则

1. **完全遵循DESIGN.md**：严格遵循DESIGN.md中的设计规范
2. **深色主题优先**：以#0b0b0b近黑色为背景，创建技术感强的界面
3. **精确排版**：使用Inter字体，应用负字间距，确保文本清晰可读
4. **纯中性灰度**：使用纯中性灰度调色板，避免暖色调
5. **鲜艳强调色**：使用鲜艳的强调色（如#ff6b35橙色）突出重点元素

## 色彩系统重构

### 当前系统（将被替换）
- 主背景：--color-parchment: #f5f4ed（羊皮纸色）
- 温暖色调：--color-warm-sand, --color-border-cream等

### 新系统（基于DESIGN.md）
```css
/* 核心色彩 */
--color-near-black: #0b0b0b;          /* 近黑色背景 */
--color-dark-surface: #1a1a1a;        /* 深色表面 */
--color-dark-border: #2a2a2a;         /* 深色边框 */

/* 中性灰度 */
--color-pure-white: #ffffff;          /* 纯白色文本 */
--color-text-primary: #f0f0f0;        /* 主要文本 */
--color-text-secondary: #b0b0b0;      /* 次要文本 */
--color-text-tertiary: #808080;       /* 三级文本 */

/* 强调色 */
--color-accent-orange: #ff6b35;       /* 橙色强调色 */
--color-accent-orange-light: #ff8c42; /* 浅橙色 */
--color-accent-blue: #3a86ff;         /* 蓝色强调色 */
--color-accent-green: #38b000;        /* 绿色强调色 */
--color-accent-red: #e63946;          /* 红色强调色 */

/* 状态色 */
--color-success: #38b000;
--color-warning: #ff9e00;
--color-error: #e63946;
--color-info: #3a86ff;
```

## 排版系统更新

### 字体系统
```css
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

## 间距系统（8px基准）

```css
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

## 圆角系统

```css
/* 圆角 */
--radius-none: 0;
--radius-subtle: 0.25rem;     /* 4px */
--radius-comfortable: 0.5rem; /* 8px */
--radius-generous: 0.75rem;   /* 12px */
--radius-very-rounded: 1rem;  /* 16px */
--radius-pill: 9999px;        /* 药丸形 */
```

## 阴影系统

```css
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

## 组件设计规范

### 1. 按钮组件
```css
/* 主按钮 */
.btn-primary {
  background: linear-gradient(135deg, var(--color-accent-orange), var(--color-accent-orange-light));
  color: var(--color-pure-white);
  border: none;
  border-radius: var(--radius-pill);
  padding: var(--space-xs) var(--space-lg);
  font-weight: var(--font-weight-medium);
  letter-spacing: var(--letter-spacing-wide);
  transition: all 0.2s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-level-2);
}

/* 次要按钮 */
.btn-secondary {
  background: transparent;
  color: var(--color-text-primary);
  border: 2px solid var(--color-dark-border);
  border-radius: var(--radius-pill);
  padding: calc(var(--space-xs) - 2px) var(--space-lg);
}

/* 文本按钮 */
.btn-text {
  background: transparent;
  color: var(--color-text-secondary);
  border: none;
  padding: var(--space-xs) var(--space-sm);
}

.btn-text:hover {
  color: var(--color-accent-orange);
}
```

### 2. 卡片组件
```css
.card {
  background-color: var(--color-dark-surface);
  border: 1px solid var(--color-dark-border);
  border-radius: var(--radius-generous);
  padding: var(--space-lg);
  transition: all 0.25s ease;
}

.card:hover {
  border-color: var(--color-accent-orange);
  box-shadow: var(--shadow-level-2);
  transform: translateY(-4px);
}

/* 带强调边框的卡片 */
.card-accent {
  border-top: 3px solid var(--color-accent-orange);
}
```

### 3. 输入框组件
```css
.input {
  background-color: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--color-dark-border);
  border-radius: var(--radius-comfortable);
  color: var(--color-text-primary);
  padding: var(--space-sm) var(--space-md);
  font-family: var(--font-family-ui);
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--color-accent-orange);
  box-shadow: var(--shadow-ring-warm);
}
```

### 4. 导航组件
```css
/* 侧边栏导航 */
.sidebar {
  background-color: var(--color-near-black);
  border-right: 1px solid var(--color-dark-border);
}

.nav-item {
  color: var(--color-text-secondary);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-comfortable);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background-color: var(--color-dark-surface);
  color: var(--color-text-primary);
}

.nav-item.active {
  background-color: var(--color-dark-surface);
  color: var(--color-accent-orange);
  border-left: 3px solid var(--color-accent-orange);
}
```

### 5. 表格组件
```css
.table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

.table th {
  background-color: var(--color-dark-surface);
  color: var(--color-text-primary);
  font-weight: var(--font-weight-semibold);
  padding: var(--space-md);
  text-align: left;
  border-bottom: 2px solid var(--color-dark-border);
}

.table td {
  padding: var(--space-md);
  border-bottom: 1px solid var(--color-dark-border);
  color: var(--color-text-secondary);
}

.table tr:hover td {
  background-color: rgba(255, 107, 53, 0.05);
}
```

## 布局系统

### 1. 主布局结构
```css
.layout {
  display: flex;
  min-height: 100vh;
  background-color: var(--color-near-black);
}

/* 侧边栏固定宽度 */
.sidebar {
  width: 260px;
  position: fixed;
  height: 100vh;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  margin-left: 260px;
  min-height: 100vh;
}

/* 顶部导航栏 */
.header {
  background-color: var(--color-dark-surface);
  border-bottom: 1px solid var(--color-dark-border);
  padding: var(--space-lg) var(--space-xl);
  position: sticky;
  top: 0;
  z-index: 100;
}
```

### 2. 网格系统
```css
/* 功能网格（如仪表板） */
.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-xl);
}

/* 响应式网格 */
@media (max-width: 991px) {
  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 767px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
}
```

## 实施计划

### 阶段1：基础系统重构
1. 创建新的CSS变量系统文件
2. 替换现有的design-system.css
3. 更新main.css导入
4. 验证基础色彩和排版

### 阶段2：核心组件重构
1. 按钮组件重设计
2. 卡片组件重设计
3. 输入框组件重设计
4. 导航组件重设计

### 阶段3：页面级重构
1. 仪表板页面（DashboardView.vue）
2. 布局组件（LayoutView.vue）
3. 其他关键页面

### 阶段4：细节优化和测试
1. 响应式设计调整
2. 交互状态优化
3. 跨浏览器测试
4. 性能优化

## 技术约束

1. **兼容性**：确保与现有Vue 3组件兼容
2. **性能**：CSS变量使用需考虑性能影响
3. **维护性**：保持CSS变量命名一致性
4. **可扩展性**：设计系统应易于扩展

## 成功标准

1. 完全遵循DESIGN.md设计规范
2. 所有页面成功迁移到深色主题
3. 保持现有功能完整性
4. 用户体验提升（视觉一致性、可读性）
5. 代码维护性提升（统一的CSS变量系统）

## 风险缓解

1. **现有组件兼容性**：逐步迁移，保持向后兼容
2. **用户接受度**：提供视觉对比，确保用户理解改进
3. **开发时间**：分阶段实施，优先核心页面
4. **测试覆盖**：确保关键路径测试通过

---

*设计已批准：2026-04-13*  
*批准人：用户*  
*实施状态：待开始*