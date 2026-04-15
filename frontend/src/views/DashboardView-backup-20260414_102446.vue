<template>
  <div class="dashboard">
    <!-- 欢迎区 -->
    <div class="welcome-card card">
      <div class="welcome-left">
        <div class="welcome-title">{{ greeting }}，{{ username }} 👋</div>
        <div class="welcome-sub">今天是 {{ todayStr }}，一切就绪，开始测试吧。</div>
      </div>
      <div class="welcome-badge">⚡ 鱼小七测试平台</div>
    </div>

    <!-- 核心功能介绍 -->
    <div class="section-title">核心功能</div>
    <div class="feature-grid">
      <div class="feature-card card" @click="$router.push('/endpoints')">
        <div class="fc-icon">🔗</div>
        <div class="fc-body">
          <div class="fc-name">接口管理</div>
          <div class="fc-desc">统一维护项目下的 HTTP 接口，支持 GET / POST / PUT / DELETE 等方法，配置请求头、参数、Body，一处定义，全局复用。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>

      <div class="feature-card card" @click="$router.push('/cases')">
        <div class="fc-icon">📝</div>
        <div class="fc-body">
          <div class="fc-name">用例管理</div>
          <div class="fc-desc">基于接口创建测试用例，配置前后置脚本、动态变量提取与多维度断言规则，精准验证接口响应。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>

      <div class="feature-card card" @click="$router.push('/suites')">
        <div class="fc-icon">📦</div>
        <div class="fc-body">
          <div class="fc-name">套件管理</div>
          <div class="fc-desc">将多个用例编排成测试套件，按角色分组、顺序执行，支持跨用例变量传递，一键运行完整业务流。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>

      <div class="feature-card card" @click="$router.push('/environments')">
        <div class="fc-icon">🌐</div>
        <div class="fc-body">
          <div class="fc-name">环境管理</div>
          <div class="fc-desc">配置测试 / 生产等多套环境，管理服务域名映射、全局变量和请求头，切换环境无需修改用例。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>

      <div class="feature-card card" @click="$router.push('/results')">
        <div class="fc-icon">📊</div>
        <div class="fc-body">
          <div class="fc-name">执行结果</div>
          <div class="fc-desc">查看每次套件执行的详细报告，包含用例通过率、断言明细、错误日志，定位问题一目了然。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>

      <div class="feature-card card" @click="$router.push('/projects')">
        <div class="fc-icon">📁</div>
        <div class="fc-body">
          <div class="fc-name">项目管理</div>
          <div class="fc-desc">按项目隔离接口与用例，支持多项目并行，成员权限精细控制，适配团队协作测试场景。</div>
        </div>
        <div class="fc-arrow">→</div>
      </div>
    </div>

    <!-- 使用说明 -->
    <div class="section-title">快速上手</div>
    <div class="guide-card card">
      <div class="guide-steps">
        <div v-for="(step, i) in steps" :key="i" class="guide-step">
          <div class="step-num">{{ i + 1 }}</div>
          <div class="step-title">{{ step.title }}</div>
          <div class="step-desc">{{ step.desc }}</div>
          <div v-if="i < steps.length - 1" class="step-chevron">❯</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const username = computed(() => {
  const u = userStore.userInfo
  return u?.nickname || u?.username || u?.userInfo?.username || '测试员'
})

const now = new Date()
const h = now.getHours()
const greeting = h < 6 ? '凌晨好' : h < 12 ? '早上好' : h < 14 ? '中午好' : h < 18 ? '下午好' : '晚上好'
const todayStr = now.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' })

const steps = [
  { title: '创建项目', desc: '在「项目管理」中新建项目，邀请团队成员' },
  { title: '定义接口', desc: '在「接口管理」中录入接口 URL、方法与默认参数' },
  { title: '编写用例', desc: '基于接口创建用例，配置断言与变量提取规则' },
  { title: '组装套件', desc: '将用例加入套件，编排执行顺序与角色分组' },
  { title: '配置环境', desc: '在「环境管理」中配置域名与全局变量' },
  { title: '运行查看', desc: '选择环境一键运行套件，在「执行结果」查看报告' },
]
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4xl);  /* 从3xl增加到4xl，增加呼吸感 */
  padding: var(--space-2xl);  /* 从xl增加到2xl */
}

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

.welcome-left {
  flex: 1;
}

.welcome-title {
  font-family: var(--font-family-heading);
  font-size: var(--font-size-subheading);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-sm);  /* 从xs增加到sm */
  line-height: var(--line-height-normal);  /* 从tight增加到normal */
}

.welcome-sub {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body);
  color: var(--color-text-primary);
  opacity: 0.85;
  line-height: var(--line-height-body-relaxed);
  margin: 0;
}

.welcome-badge {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-caption);
  font-weight: var(--font-weight-semibold);
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 9999px;
  padding: var(--space-xs) var(--space-lg);
  white-space: nowrap;
  letter-spacing: var(--letter-spacing-wide);
  backdrop-filter: blur(10px);
}

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

.fc-body {
  flex: 1;
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

/* ===== 指南卡片 ===== */
.guide-card {
  padding: var(--space-4xl);
  border-radius: var(--radius-very-rounded);
  background-color: var(--color-dark-surface);
  border: 1px solid var(--color-dark-border);
  box-shadow: var(--shadow-level-1);
}

.guide-steps {
  display: flex;
  align-items: flex-start;
  gap: 0;
  position: relative;
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

.guide-step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  position: relative;
  padding: 0 var(--space-md);
  z-index: 1;
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

.step-title {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-lg);  /* 从body增加到body-lg */
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--space-sm);  /* 从xs增加到sm */
  line-height: var(--line-height-body-relaxed);  /* 从body增加到body-relaxed */
}

.step-desc {
  font-family: var(--font-family-ui);
  font-size: var(--font-size-body-sm);
  color: var(--color-text-secondary);
  line-height: var(--line-height-body-relaxed);
  margin: 0;
}

.step-chevron {
  position: absolute;
  right: -8px;
  top: 10px;
  font-size: 20px;
  color: var(--color-accent-orange);
  font-weight: 300;
  z-index: 2;
  background: var(--color-dark-surface);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* ===== 响应式设计 ===== */
@media (max-width: 991px) {
  .dashboard {
    padding: var(--space-lg);
    gap: var(--space-2xl);
    background-color: var(--color-near-black);
  }

  .feature-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .welcome-card {
    padding: var(--space-2xl);
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-lg);
  }

  .welcome-badge {
    align-self: flex-start;
  }

  .guide-steps {
    flex-wrap: wrap;
    gap: var(--space-xl);
  }

  .guide-steps::before {
    display: none;
  }

  .guide-step {
    flex: 0 0 calc(50% - var(--space-xl));
    padding: 0;
  }

  .step-chevron {
    display: none;
  }
}

@media (max-width: 767px) {
  .dashboard {
    padding: var(--space-md);
    gap: var(--space-xl);
    background-color: var(--color-near-black);
  }

  .feature-grid {
    grid-template-columns: 1fr;
  }

  .welcome-card {
    padding: var(--space-xl);
    border-radius: var(--radius-generous);
  }

  .welcome-title {
    font-size: var(--font-size-feature-title);
  }

  .welcome-sub {
    font-size: var(--font-size-body-sm);
  }

  .section-title {
    font-size: var(--font-size-feature-title);
    margin-bottom: var(--space-md);
  }

  .feature-card {
    padding: var(--space-xl);
    border-radius: var(--radius-generous);
  }

  .fc-icon {
    font-size: 28px;
    width: 36px;
    height: 36px;
  }

  .fc-name {
    font-size: var(--font-size-body-lg);
  }

  .guide-card {
    padding: var(--space-xl);
    border-radius: var(--radius-generous);
  }

  .guide-step {
    flex: 0 0 100%;
    margin-bottom: var(--space-lg);
  }

  .guide-step:last-child {
    margin-bottom: 0;
  }
}

@media (max-width: 479px) {
  .dashboard {
    padding: var(--space-sm);
    gap: var(--space-lg);
  }

  .welcome-card {
    padding: var(--space-lg);
  }

  .feature-card {
    padding: var(--space-lg);
    flex-direction: column;
    gap: var(--space-md);
  }

  .fc-icon {
    align-self: flex-start;
  }

  .fc-arrow {
    align-self: flex-end;
    margin-top: var(--space-sm);
  }
}
</style>
