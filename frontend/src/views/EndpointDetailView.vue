<template>
  <div class="endpoint-detail-view">

    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回接口列表
      </button>
      <div class="page-header__actions">
        <button class="btn btn--primary btn--sm" @click="$router.push(`/endpoints/edit/${route.params.id}`)">
          <EditOutlined /> 编辑接口
        </button>
        <button class="btn btn--danger-ghost btn--sm" @click="deleteEndpointItem">
          <DeleteOutlined /> 删除
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <a-spin size="large" />
      <span>加载中...</span>
    </div>

    <!-- 主要内容 -->
    <div v-if="endpoint && !loading" class="detail-content">

      <!-- 基本信息卡片 -->
      <div class="form-card">
        <div class="form-card__header">
          <div class="form-card__title-group">
            <div class="form-card__title-row">
              <div class="form-card__title">{{ endpoint.name }}</div>
              <span class="method-badge method-badge--lg" :class="`m-${endpoint.method?.toLowerCase()}`">
                {{ endpoint.method }}
              </span>
            </div>
            <div class="form-card__subtitle" v-if="endpoint.description">{{ endpoint.description }}</div>
          </div>
        </div>

        <div class="form-card__body">
          <!-- 接口地址 -->
          <div class="url-display-block">
            <label class="info-label">接口地址</label>
            <div class="url-box">
              <span v-if="endpoint.service_key" class="url-service-tag">{{ endpoint.service_key }}</span>
              <code class="url-path-text">{{ endpoint.url || '-' }}</code>
            </div>
            <span v-if="endpoint.service_key" class="url-hint">
              执行时 <strong>{{ endpoint.service_key }}</strong> 将被替换为所选环境的实际 URL
            </span>
          </div>

          <!-- 完整 URL 预览 -->
          <div v-if="fullUrlPreview.length" class="url-preview-section">
            <label class="info-label">完整 URL 预览（按环境）</label>
            <div class="url-preview-list">
              <div v-for="item in fullUrlPreview" :key="item.envName" class="url-preview-item">
                <span class="env-tag">{{ item.envName }}</span>
                <code class="full-url">{{ item.url }}</code>
              </div>
            </div>
          </div>

          <!-- 信息网格 -->
          <div class="info-grid">
            <div class="info-item" v-if="endpoint.project">
              <label class="info-label">所属项目</label>
              <div class="info-value">
                <span class="project-link" @click="$router.push(`/projects/${endpoint.project}`)">
                  {{ endpoint.project_name || `项目 #${endpoint.project}` }}
                </span>
              </div>
            </div>
            <div class="info-item" v-if="endpoint.product_line_name">
              <label class="info-label">所属产品线</label>
              <div class="info-value">
                <div class="pl-badge">
                  <span class="pl-badge__dot" :style="{ background: plColor }"></span>
                  <span>{{ endpoint.product_line_name }}</span>
                </div>
              </div>
            </div>
            <div class="info-item">
              <label class="info-label">创建时间</label>
              <span class="info-value">{{ formatDate(endpoint.created_at) }}</span>
            </div>
            <div class="info-item" v-if="endpoint.updated_at">
              <label class="info-label">更新时间</label>
              <span class="info-value">{{ formatDate(endpoint.updated_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 切换区 -->
      <div class="form-card form-card--no-clip">
        <div class="tabs-wrapper">
          <div class="tabs-nav">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="tab-btn"
              :class="{ 'tab-btn--active': activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              <component :is="tab.icon" class="tab-btn__icon" />
              {{ tab.label }}
              <span v-if="tab.count" class="tab-btn__count">{{ tab.count }}</span>
            </button>
          </div>

          <!-- 请求参数 Tab -->
          <div v-show="activeTab === 'params'" class="tab-content">
            <div class="params-display-grid">
              <!-- 查询参数 -->
              <div v-if="hasKeys(endpoint.params)" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">Query Params</span>
                  <span class="param-count">{{ Object.keys(endpoint.params).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div class="kv-display-head">
                    <span>Key</span><span>Value</span>
                  </div>
                  <div
                    v-for="(v, k) in endpoint.params"
                    :key="k"
                    class="kv-display-row"
                  >
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>

              <!-- Headers -->
              <div v-if="hasKeys(endpoint.headers)" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">Headers</span>
                  <span class="param-count">{{ Object.keys(endpoint.headers).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div class="kv-display-head">
                    <span>Key</span><span>Value</span>
                  </div>
                  <div
                    v-for="(v, k) in endpoint.headers"
                    :key="k"
                    class="kv-display-row"
                  >
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>

              <!-- 表单参数 -->
              <div v-if="hasKeys(endpoint.data)" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">表单参数</span>
                  <span class="param-count">{{ Object.keys(endpoint.data).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div class="kv-display-head">
                    <span>Key</span><span>Value</span>
                  </div>
                  <div
                    v-for="(v, k) in endpoint.data"
                    :key="k"
                    class="kv-display-row"
                  >
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>

              <!-- JSON 参数 -->
              <div v-if="hasKeys(endpoint.json)" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">JSON Body</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(endpoint.json, null, 2) }}</pre>
              </div>

              <!-- 空状态 -->
              <div v-if="!hasKeys(endpoint.params) && !hasKeys(endpoint.headers) && !hasKeys(endpoint.data) && !hasKeys(endpoint.json)" class="empty-tab">
                <ApiOutlined class="empty-tab__icon" />
                <p>暂无请求参数</p>
              </div>
            </div>
          </div>

          <!-- 关联用例 Tab -->
          <div v-show="activeTab === 'cases'" class="tab-content">
            <div class="tab-toolbar">
              <div class="tab-toolbar__info">
                共 <strong>{{ cases.length }}</strong> 个关联用例
              </div>
            </div>
            <div v-if="cases.length" class="ref-list">
              <div
                v-for="item in cases"
                :key="item.id"
                class="ref-item"
                @click="$router.push(`/cases/${item.id}`)"
              >
                <span class="ref-item__icon">
                  <FileProtectOutlined />
                </span>
                <span class="ref-item__name">{{ item.name }}</span>
                <ArrowRightOutlined class="ref-item__arrow" />
              </div>
            </div>
            <div v-else class="empty-tab">
              <FileProtectOutlined class="empty-tab__icon" />
              <p>暂无关联用例</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  ApiOutlined,
  FileProtectOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons-vue'
import { getEndpointDetail, deleteEndpoint } from '@/api/endpoint'
import { getCases } from '@/api/case'
import { getEnvironments } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { useUserStore } from '@/stores/user'

const route  = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading  = ref(true)
const endpoint     = ref(null)
const cases        = ref([])
const environments = ref([])
const activeTab    = ref('params')

const tabs = computed(() => [
  {
    key: 'params',
    label: '请求参数',
    icon: ApiOutlined,
    count: paramCount.value,
  },
  {
    key: 'cases',
    label: '关联用例',
    icon: FileProtectOutlined,
    count: cases.value.length || null,
  },
])

const paramCount = computed(() => {
  let n = 0
  if (hasKeys(endpoint.value?.params))   n += Object.keys(endpoint.value.params).length
  if (hasKeys(endpoint.value?.headers)) n += Object.keys(endpoint.value.headers).length
  if (hasKeys(endpoint.value?.data))    n += Object.keys(endpoint.value.data).length
  if (hasKeys(endpoint.value?.json))    n++
  return n || null
})

const plColor = computed(() => {
  const name = endpoint.value?.product_line_name || ''
  const colors = ['#3B82F6','#10B981','#F59E0B','#EF4444','#8B5CF6','#EC4899']
  let hash = 0
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) & 0xffffffff
  return colors[Math.abs(hash) % colors.length]
})

const fullUrlPreview = computed(() => {
  if (!endpoint.value || !environments.value.length) return []
  const results = []
  for (const env of environments.value) {
    let fullUrl = ''
    if (endpoint.value.service_key && env.urls) {
      const svcUrl = env.urls.find(u => u.var === endpoint.value.service_key)
      if (svcUrl && svcUrl.url) {
        fullUrl = svcUrl.url.replace(/\/$/, '') + (endpoint.value.url || '')
      }
    } else if (env.base_url) {
      fullUrl = env.base_url.replace(/\/$/, '') + (endpoint.value.url || '')
    }
    if (fullUrl) results.push({ envName: env.name, url: fullUrl })
  }
  return results
})

const hasKeys = (val) => {
  if (!val) return false
  if (typeof val === 'object') return Object.keys(val).length > 0
  return !!String(val).trim()
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

const loadEndpoint = async () => {
  const res = await getEndpointDetail(route.params.id)
  endpoint.value = res.result ?? res
}

const loadCases = async () => {
  const res = await getCases({ endpoint: route.params.id })
  cases.value = res.result?.list || []
}

const loadEnvironments = async () => {
  if (!endpoint.value?.project) return
  const res = await getEnvironments({ project: endpoint.value.project, page_size: 100 })
  environments.value = res.result?.list || []
}

const deleteEndpointItem = async () => {
  const confirmed = await confirm('确定要删除这个接口吗？此操作不可恢复。', { type: 'danger' })
  if (!confirmed) return
  try {
    await deleteEndpoint(route.params.id)
    router.push('/endpoints')
  } catch (e) {
    alert('删除失败: ' + (e.response?.data?.message || e.message))
  }
}

onMounted(async () => {
  loading.value = true
  await loadEndpoint()
  await Promise.all([loadCases(), loadEnvironments()])
  loading.value = false
})
</script>

<style scoped>
/* ─── 页面容器 ─── */
.endpoint-detail-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  color: #6b7280;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn-back:hover {
  color: #111827;
  border-color: #d1d5db;
  background: #f9fafb;
}

/* ─── 加载状态 ─── */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 60px;
  color: #6b7280;
  font-size: 14px;
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 18px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn--primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn--primary:hover {
  background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
}

.btn--primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--danger-ghost {
  background: white;
  color: #ef4444;
  border: 1.5px solid #fecaca;
}

.btn--danger-ghost:hover {
  background: #fef2f2;
  border-color: #ef4444;
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.15);
}

.btn--sm {
  padding: 8px 16px;
  font-size: 13px;
  border-radius: 8px;
}

/* ─── 表单卡片 ─── */
.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
}

.form-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.form-card--no-clip {
  overflow: visible;
}

.form-card__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px 28px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-radius: 16px 16px 0 0;
}

.form-card__title-group {
  flex: 1;
  min-width: 0;
}

.form-card__title-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 6px;
}

.form-card__title {
  font-size: 20px;
  font-weight: 700;
  color: #111827;
  line-height: 1.3;
}

.form-card__subtitle {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

.form-card__body {
  padding: 24px 28px;
}

/* ─── 信息标签 ─── */
.info-label {
  font-size: 12px;
  font-weight: 700;
  color: #9CA3AF;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  display: block;
  margin-bottom: 6px;
}

.info-value {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

/* ─── 接口地址展示 ─── */
.url-display-block {
  margin-bottom: 16px;
}

.url-box {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px 16px;
  flex-wrap: wrap;
}

.url-service-tag {
  background: #dbeafe;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  padding: 2px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
}

.url-path-text {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #111827;
  font-weight: 500;
}

.url-hint {
  font-size: 12px;
  color: #9CA3AF;
  margin-top: 6px;
  display: block;
}

/* ─── URL 预览 ─── */
.url-preview-section {
  margin-bottom: 16px;
}

.url-preview-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.url-preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px 14px;
}

.env-tag {
  font-size: 12px;
  font-weight: 700;
  color: #3B82F6;
  min-width: 80px;
  background: #eff6ff;
  padding: 2px 8px;
  border-radius: 6px;
  text-align: center;
}

.full-url {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  color: #374151;
  word-break: break-all;
}

/* ─── 项目链接 ─── */
.project-link {
  color: #3B82F6;
  cursor: pointer;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.project-link:hover {
  color: #1d4ed8;
}

.pl-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.pl-badge__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.pl-badge__name {
  font-size: 14px;
  color: #111827;
  font-weight: 500;
}

/* ─── Method Badge ─── */
.method-badge--lg {
  padding: 5px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  flex-shrink: 0;
}

.m-get    { background: #dbeafe; color: #1d4ed8; }
.m-post   { background: #dcfce7; color: #15803d; }
.m-put    { background: #fef3c7; color: #b45309; }
.m-delete { background: #fee2e2; color: #dc2626; }
.m-patch  { background: #f3e8ff; color: #7c3aed; }

/* ─── Tabs ─── */
.tabs-wrapper {
  background: white;
}

.tabs-nav {
  display: flex;
  gap: 4px;
  padding: 16px 24px 0;
  border-bottom: 1px solid #f0f0f0;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
  border-radius: 8px 8px 0 0;
}

.tab-btn:hover {
  color: #111827;
  background: #f9fafb;
}

.tab-btn--active {
  color: #3B82F6;
  border-bottom-color: #3B82F6;
  font-weight: 700;
  background: white;
}

.tab-btn__icon {
  font-size: 14px;
}

.tab-btn__count {
  background: #eff6ff;
  color: #3B82F6;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 700;
}

.tab-content {
  padding: 20px 24px;
}

/* ─── Tab Toolbar ─── */
.tab-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.tab-toolbar__info {
  font-size: 13px;
  color: #6b7280;
}

.tab-toolbar__info strong {
  color: #111827;
}

/* ─── 请求参数展示 ─── */
.params-display-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.param-section {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.param-section--full {
  grid-column: 1 / -1;
}

.param-section__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.param-section__title {
  font-size: 12px;
  font-weight: 700;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.param-count {
  background: #eff6ff;
  color: #3B82F6;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 700;
}

/* KV Display Table */
.kv-display-table {
  overflow: hidden;
}

.kv-display-head {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px;
  padding: 8px 14px;
  background: #f3f4f6;
  font-size: 11px;
  font-weight: 700;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kv-display-row {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px;
  padding: 8px 14px;
  border-top: 1px solid #f0f0f0;
  transition: background 0.1s;
}

.kv-display-row:hover {
  background: #fafbfc;
}

.kv-key {
  font-size: 12px;
  font-weight: 700;
  color: #3B82F6;
  font-family: 'SF Mono', 'Fira Code', monospace;
  word-break: break-all;
}

.kv-value {
  font-size: 13px;
  color: #374151;
  font-family: 'SF Mono', 'Fira Code', monospace;
  word-break: break-all;
}

/* JSON Display */
.json-display {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 16px 20px;
  border-radius: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
  border-radius: 0 0 12px 12px;
}

/* ─── 关联列表 ─── */
.ref-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ref-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s;
}

.ref-item:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
  transform: translateX(4px);
}

.ref-item__icon {
  font-size: 16px;
  color: #6b7280;
  flex-shrink: 0;
}

.ref-item:hover .ref-item__icon {
  color: #3B82F6;
}

.ref-item__name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.ref-item__arrow {
  font-size: 12px;
  color: #d1d5db;
  flex-shrink: 0;
  transition: transform 0.15s, color 0.15s;
}

.ref-item:hover .ref-item__arrow {
  color: #3B82F6;
  transform: translateX(2px);
}

/* ─── 空状态 ─── */
.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 48px 24px;
  color: #9CA3AF;
  font-size: 14px;
  text-align: center;
}

.empty-tab__icon {
  font-size: 32px;
  color: #d1d5db;
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .params-display-grid {
    grid-template-columns: 1fr;
  }

  .form-card__header {
    flex-direction: column;
    gap: 12px;
  }

  .form-card__title-row {
    flex-wrap: wrap;
  }
}
</style>
