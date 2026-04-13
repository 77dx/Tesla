<template>
  <div class="ui-case-view card">
    <div class="page-header">
      <div>
        <h2>平台内 UI 用例</h2>
        <p>结构化步骤编排，支持在套件中与接口用例混编执行。</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-sm" @click="createSampleCase">创建测试示例</button>
        <button class="btn btn-primary" @click="createNew">新建 UI 用例</button>
      </div>
    </div>

    <div class="toolbar">
      <input v-model="search" class="filter-input" placeholder="搜索名称 / ID" @keyup.enter="load" />
      <select v-model="platform" class="filter-select" @change="load">
        <option value="">全部平台</option>
        <option value="web">Web</option>
        <option value="app">App</option>
      </select>
      <button class="btn btn-sm" @click="load">搜索</button>
    </div>

    <div class="template-strip card-lite">
      <div class="template-head">
        <strong>示例模板库</strong>
        <span>一键创建可编辑的 UI 用例模板</span>
      </div>
      <div class="template-grid">
        <button v-for="tpl in sampleTemplates" :key="tpl.key" class="template-card" @click="createSampleCase(tpl)">
          <strong>{{ tpl.name }}</strong>
          <span>{{ tpl.desc }}</span>
        </button>
      </div>
    </div>

    <table class="table">
      <thead>
        <tr>
          <th style="width:80px">ID</th>
          <th>名称</th>
          <th style="width:180px">项目</th>
          <th style="width:160px">产品线</th>
          <th style="width:100px">平台</th>
          <th style="width:180px">更新时间</th>
          <th style="width:180px">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>#{{ item.id }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.project_name || '-' }}</td>
          <td>{{ item.product_line_name || '-' }}</td>
          <td><span class="type-tag">{{ item.platform || 'web' }}</span></td>
          <td>{{ formatDate(item.updated_at || item.created_at) }}</td>
          <td>
            <div class="row-actions">
              <button class="btn-action btn-info" @click="openDetail(item.id)">打开</button>
              <button class="btn-action btn-danger" @click="removeItem(item)">删除</button>
            </div>
          </td>
        </tr>
        <tr v-if="!items.length">
          <td colspan="7" class="empty-state">暂无 UI 用例</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getUICases, deleteUICase, createUICase } from '@/api/uiCase'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'

const router = useRouter()
const items = ref([])
const search = ref('')
const platform = ref('')
const sampleTemplates = [
  {
    key: 'login-basic',
    name: '登录页检查',
    desc: '打开登录页、填写用户名、断言 URL、截图',
    payload: {
      name: '示例UI用例-登录页检查',
      platform: 'web',
      entry_url: '/login',
      pre_script: "ctx['demo_username'] = ctx.get('demo_username', 'tester')",
      post_script: '',
      steps: [
        { name: '打开登录页', action: 'goto', target: '/login', enabled: true },
        { name: '填写用户名', action: 'fill', locator: '#username', value: '${demo_username}', enabled: true },
        { name: '等待标题', action: 'wait_for_text', value: '登录', enabled: true },
        { name: '断言URL', action: 'assert_url', value: '/login', enabled: true },
        { name: '截图', action: 'screenshot', enabled: true },
      ],
      validate: [{ type: 'url_contains', name: '登录页URL校验', expected: '/login' }],
      extract: [],
    },
  },
  {
    key: 'search-page',
    name: '搜索页模板',
    desc: '输入搜索词、触发搜索、断言结果可见',
    payload: {
      name: '示例UI用例-搜索页',
      platform: 'web',
      entry_url: '/search',
      pre_script: "ctx['keyword'] = ctx.get('keyword', 'Tesla')",
      post_script: '',
      steps: [
        { name: '打开搜索页', action: 'goto', target: '/search', enabled: true },
        { name: '填写关键词', action: 'fill', locator: 'input[type=search]', value: '${keyword}', enabled: true },
        { name: '回车搜索', action: 'press', locator: 'input[type=search]', value: 'Enter', enabled: true },
        { name: '等待结果文本', action: 'wait_for_text', value: '${keyword}', enabled: true },
        { name: '截图', action: 'screenshot', enabled: true },
      ],
      validate: [],
      extract: [],
    },
  },
  {
    key: 'extract-list-id',
    name: '列表页提取ID',
    desc: '从列表页提取首条记录 ID 供后续接口使用',
    payload: {
      name: '示例UI用例-列表提取ID',
      platform: 'web',
      entry_url: '/orders',
      pre_script: '',
      post_script: '',
      steps: [
        { name: '打开订单列表', action: 'goto', target: '/orders', enabled: true },
        { name: '等待列表渲染', action: 'wait_for_selector', locator: '.order-row:first-child', enabled: true },
        { name: '提取订单号', action: 'extract_attr', locator: '.order-row:first-child', attr: 'data-id', save_as: 'order_id', enabled: true },
        { name: '截图', action: 'screenshot', enabled: true },
      ],
      validate: [],
      extract: [],
    },
  },
  {
    key: 'inject-token',
    name: 'localStorage 注入 token',
    desc: '适合 API 登录后把 token 注入前端页面',
    payload: {
      name: '示例UI用例-token注入',
      platform: 'web',
      entry_url: '/dashboard',
      pre_script: "ctx['token'] = ctx.get('token', 'demo-token')",
      post_script: '',
      steps: [
        { name: '打开首页', action: 'goto', target: '/dashboard', enabled: true },
        { name: '写入 token', action: 'set_local_storage', key: 'token', value: '${token}', enabled: true },
        { name: '重新打开首页', action: 'goto', target: '/dashboard', enabled: true },
        { name: '断言 URL', action: 'assert_url', value: '/dashboard', enabled: true },
        { name: '截图', action: 'screenshot', enabled: true },
      ],
      validate: [],
      extract: [],
    },
  },
]

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

const load = async () => {
  const res = await getUICases({ search: search.value || undefined, platform: platform.value || undefined, page_size: 500 })
  items.value = res.result?.list || res.result || []
}

const openDetail = (id) => router.push(`/ui-cases/${id}`)
const createNew = () => router.push('/ui-cases/new')
const createSampleCase = async (template = sampleTemplates[0]) => {
  try {
    const res = await createUICase(template.payload)
    const id = res.result?.id || res.id
    await alert(`已创建示例 UI 用例：${template.name}`, 'success')
    await load()
    if (id) openDetail(id)
  } catch (e) {
    alert(e.response?.data?.message || e.message || '创建示例失败')
  }
}

const removeItem = async (item) => {
  const ok = await confirm(`确定删除 UI 用例「${item.name}」吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await deleteUICase(item.id)
    await load()
  } catch (e) {
    alert(e.response?.data?.message || e.message || '删除失败')
  }
}

onMounted(load)
</script>

<style scoped>
.ui-case-view { padding: 24px; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:18px; }
.header-actions { display:flex; gap:10px; }
.page-header h2 { margin:0 0 6px; }
.page-header p { margin:0; color:var(--text-light); font-size:13px; }
.toolbar { display:flex; gap:12px; margin-bottom:16px; }
.template-strip { border:1px solid var(--border); border-radius:14px; padding:16px; margin-bottom:16px; background:linear-gradient(180deg,#fcfdff,#f7faff); }
.template-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; color:var(--text-light); font-size:13px; }
.template-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:12px; }
.template-card { border:1px solid #d9e6ff; background:white; border-radius:12px; padding:14px; text-align:left; cursor:pointer; display:flex; flex-direction:column; gap:6px; }
.template-card:hover { border-color:#8db2ff; box-shadow:0 6px 18px rgba(48,94,208,.08); }
.template-card strong { color:#274472; }
.template-card span { color:var(--text-light); font-size:12px; }
.filter-input,.filter-select { border:1px solid var(--border); border-radius:8px; padding:9px 12px; }
.filter-input { min-width:260px; }
.type-tag { display:inline-block; padding:3px 8px; border-radius:10px; background:#e8f5e9; color:#2e7d32; font-size:12px; font-weight:700; }
.row-actions { display:flex; gap:8px; }
.empty-state { text-align:center; color:var(--text-light); padding:28px 0; }
</style>
