<template>
  <div class="endpoint-form-view">
    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回接口列表
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <a-spin size="large" />
      <span>加载中...</span>
    </div>

    <!-- 主要内容 -->
    <div v-if="!loading">
      <!-- 基本信息卡片 -->
      <div class="form-card">
        <div class="form-card__header">
          <div class="form-card__title-group">
            <div class="form-card__title">{{ isEditing ? '编辑接口' : '新建接口' }}</div>
            <div class="form-card__subtitle">{{ isEditing ? '修改接口配置信息' : '填写接口基本信息' }}</div>
          </div>
          <div class="form-card__actions" v-if="isEditing">
            <button class="btn btn--primary" :disabled="saving" @click="handleSubmit">
              <SaveOutlined /> {{ saving ? '保存中...' : '保存修改' }}
            </button>
            <button class="btn btn--ghost" @click="$router.back()">取消</button>
          </div>
        </div>

        <div class="form-card__body">
          <!-- 基本信息区域 -->
          <div class="section-block">
            <div class="section-block__title">基本信息</div>
            <div class="form-row">
              <!-- 接口名称 -->
              <div class="form-group">
                <label class="form-group__label">接口名称 <span class="required">*</span></label>
                <input
                  v-model="formData.name"
                  class="form-input"
                  placeholder="如：获取用户信息"
                />
              </div>

              <!-- 所属项目 -->
              <div class="form-group">
                <label class="form-group__label">所属项目</label>
                <select v-model="formData.project" class="form-select">
                  <option :value="null">不指定</option>
                  <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <!-- 请求方法 -->
              <div class="form-group">
                <label class="form-group__label">请求方法 <span class="required">*</span></label>
                <div class="method-options">
                  <button
                    v-for="m in methods"
                    :key="m.value"
                    type="button"
                    class="method-btn"
                    :class="[{ active: formData.method === m.value }, `m-${m.value.toLowerCase()}`]"
                    @click="formData.method = m.value"
                  >
                    {{ m.value }}
                  </button>
                </div>
              </div>
            </div>

            <!-- 接口地址 -->
            <div class="form-group">
              <label class="form-group__label">接口地址 <span class="required">*</span></label>
              <div class="url-input-group">
                <select v-model="urlPrefix" class="url-prefix-select">
                  <option value="">无服务</option>
                  <option v-for="svc in services" :key="svc.key" :value="svc.key">
                    {{ svc.name }} ({{ svc.key }})
                  </option>
                </select>
                <span class="url-sep">/</span>
                <input
                  v-model="urlPath"
                  class="url-path-input"
                  placeholder="api/users"
                />
              </div>
              <div class="field-hint-row">
                <span class="url-preview">路径预览：<code>{{ fullUrl }}</code></span>
              </div>
              <div v-if="!services.length" class="field-hint field-hint--warning">
                暂无可用服务，请先在环境管理中配置服务 URL
              </div>
            </div>

            <!-- 描述 -->
            <div class="form-group">
              <label class="form-group__label">描述</label>
              <textarea
                v-model="formData.description"
                class="form-textarea"
                rows="2"
                placeholder="可选备注"
              ></textarea>
            </div>
          </div>

          <!-- 请求参数区域 -->
          <div class="section-block">
            <div class="section-block__title">请求参数</div>

            <!-- Headers -->
            <div class="params-block">
              <div class="params-block__header">
                <span class="params-block__title">Headers</span>
                <span class="params-block__count">{{ enabledHeadersCount }}</span>
              </div>
              <div class="kv-table">
                <div class="kv-head">
                  <span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span>
                </div>
                <div v-for="(row, i) in headers" :key="i" class="kv-row">
                  <input type="checkbox" v-model="row.enabled" class="kv-check" />
                  <input v-model="row.k" placeholder="Key" class="kv-input" />
                  <input v-model="row.v" placeholder="Value" class="kv-input" />
                  <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                  <button type="button" class="kv-del" @click="headers.splice(i, 1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="headers.push({ enabled: true, k: '', v: '', desc: '' })">
                + 添加请求头
              </button>
            </div>

            <!-- Query Params / Body Tabs -->
            <div class="params-block">
              <div class="params-block__header">
                <span class="params-block__title">入参</span>
              </div>
              <div class="params-tabs">
                <button
                  v-for="t in tabs"
                  :key="t.key"
                  type="button"
                  class="params-tab"
                  :class="{ active: activeTab === t.key }"
                  @click="activeTab = t.key"
                >
                  {{ t.label }}
                  <span v-if="tabBadge(t.key)" class="tab-badge">{{ tabBadge(t.key) }}</span>
                </button>
              </div>

              <!-- Query Params -->
              <div v-show="activeTab === 'params'" class="tab-pane">
                <div class="kv-table">
                  <div class="kv-head">
                    <span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span>
                  </div>
                  <div v-for="(row, i) in queryParams" :key="i" class="kv-row">
                    <input type="checkbox" v-model="row.enabled" class="kv-check" />
                    <input v-model="row.k" placeholder="Key" class="kv-input" />
                    <input v-model="row.v" placeholder="Value" class="kv-input" />
                    <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                    <button type="button" class="kv-del" @click="queryParams.splice(i, 1)">✕</button>
                  </div>
                </div>
                <button type="button" class="btn-add-row" @click="queryParams.push({ enabled: true, k: '', v: '', desc: '' })">
                  + 添加参数
                </button>
              </div>

              <!-- Body -->
              <div v-show="activeTab === 'body'" class="tab-pane">
                <!-- Body 类型选择 -->
                <div class="body-type-bar">
                  <button
                    v-for="bt in bodyTypes"
                    :key="bt.key"
                    type="button"
                    class="body-type-btn"
                    :class="{ active: bodyType === bt.key }"
                    @click="bodyType = bt.key"
                  >
                    {{ bt.label }}
                  </button>
                </div>

                <!-- none -->
                <div v-if="bodyType === 'none'" class="body-none">此请求没有 Body</div>

                <!-- form-data -->
                <div v-else-if="bodyType === 'form-data'">
                  <div class="kv-table">
                    <div class="kv-head">
                      <span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span>
                    </div>
                    <div v-for="(row, i) in formDataRows" :key="i" class="kv-row">
                      <input type="checkbox" v-model="row.enabled" class="kv-check" />
                      <input v-model="row.k" placeholder="Key" class="kv-input" />
                      <input v-model="row.v" placeholder="Value" class="kv-input" />
                      <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                      <button type="button" class="kv-del" @click="formDataRows.splice(i, 1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-row" @click="formDataRows.push({ enabled: true, k: '', v: '', desc: '' })">
                    + 添加字段
                  </button>
                </div>

                <!-- x-www-form-urlencoded -->
                <div v-else-if="bodyType === 'urlencoded'">
                  <div class="kv-table">
                    <div class="kv-head">
                      <span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span>
                    </div>
                    <div v-for="(row, i) in urlencodedRows" :key="i" class="kv-row">
                      <input type="checkbox" v-model="row.enabled" class="kv-check" />
                      <input v-model="row.k" placeholder="Key" class="kv-input" />
                      <input v-model="row.v" placeholder="Value" class="kv-input" />
                      <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                      <button type="button" class="kv-del" @click="urlencodedRows.splice(i, 1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-row" @click="urlencodedRows.push({ enabled: true, k: '', v: '', desc: '' })">
                    + 添加字段
                  </button>
                </div>

                <!-- JSON -->
                <div v-else-if="bodyType === 'json'" class="json-editor-wrap">
                  <textarea
                    v-model="jsonBody"
                    rows="10"
                    class="json-editor"
                    :class="{ 'json-editor--error': jsonError }"
                    placeholder='{
  "key": "value"
}'
                  ></textarea>
                  <span v-if="jsonError" class="json-error">⚠ JSON 格式有误</span>
                </div>

                <!-- Raw -->
                <div v-else-if="bodyType === 'raw'" class="json-editor-wrap">
                  <textarea
                    v-model="rawBody"
                    rows="10"
                    class="json-editor"
                    placeholder="raw body content"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>

          <!-- 底部操作（仅新建模式） -->
          <div v-if="!isEditing" class="form-footer">
            <button type="button" class="btn btn--ghost" @click="$router.back()">取消</button>
            <button type="button" class="btn btn--primary" :disabled="saving" @click="handleSubmit">
              <PlusOutlined /> {{ saving ? '创建中...' : '创建接口' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  ArrowLeftOutlined,
  PlusOutlined,
  SaveOutlined,
} from '@ant-design/icons-vue'
import { createEndpoint, getEndpointDetail, updateEndpoint } from '@/api/endpoint'
import { getProjects } from '@/api/project'
import { getServices } from '@/api/suite'
import { useUserStore } from '@/stores/user'
import { alert } from '@/composables/useAlert'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const loading = ref(false)
const saving = ref(false)
const editingId = ref(null)
const isEditing = computed(() => !!editingId.value)

const projects  = ref([])
const services  = ref([])
const urlPrefix = ref('')
const urlPath   = ref('')
const activeTab = ref('params')
const bodyType  = ref('json')
const jsonBody  = ref('')
const rawBody   = ref('')
const jsonError = ref(false)

const headers        = ref([{ enabled: true, k: '', v: '', desc: '' }])
const queryParams    = ref([{ enabled: true, k: '', v: '', desc: '' }])
const formDataRows   = ref([{ enabled: true, k: '', v: '', desc: '' }])
const urlencodedRows = ref([{ enabled: true, k: '', v: '', desc: '' }])

const formData = ref({
  name: '',
  method: 'GET',
  project: null,
  description: '',
})

const methods = [
  { value: 'GET' },
  { value: 'POST' },
  { value: 'PUT' },
  { value: 'DELETE' },
  { value: 'PATCH' },
]

const tabs = [
  { key: 'params', label: 'Query Params' },
  { key: 'body',   label: 'Body' },
]

const bodyTypes = [
  { key: 'none',       label: 'none' },
  { key: 'json',       label: 'JSON' },
  { key: 'form-data',  label: 'form-data' },
  { key: 'urlencoded', label: 'x-www-form-urlencoded' },
  { key: 'raw',        label: 'raw' },
]

const enabledHeadersCount = computed(() =>
  headers.value.filter(r => r.enabled && r.k).length
)

const tabBadge = (key) => {
  if (key === 'params') return queryParams.value.filter(r => r.enabled && r.k).length || null
  if (key === 'body')  return bodyType.value !== 'none' ? '●' : null
  return null
}

const fullUrl = computed(() => {
  const path = urlPath.value ? '/' + urlPath.value.replace(/^\//, '') : ''
  return urlPrefix.value ? `{${urlPrefix.value}}${path}` : (path || '（请输入路径）')
})

watch(jsonBody, (val) => {
  if (!val.trim()) { jsonError.value = false; return }
  try { JSON.parse(val); jsonError.value = false } catch { jsonError.value = true }
})

const kvToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.enabled && r.k?.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}

const buildPayload = () => {
  const payload = {
    name:        formData.value.name,
    method:      formData.value.method,
    url:         urlPath.value ? '/' + urlPath.value.replace(/^\//, '') : '',
    service_key: urlPrefix.value || '',
    project:     formData.value.project,
    description: formData.value.description,
    headers:     kvToObj(headers.value),
    params:      kvToObj(queryParams.value),
    json:        null,
    data:        null,
  }
  if (bodyType.value === 'json') {
    try { payload.json = jsonBody.value.trim() ? JSON.parse(jsonBody.value) : null } catch {}
  } else if (bodyType.value === 'form-data') {
    payload.data = kvToObj(formDataRows.value)
  } else if (bodyType.value === 'urlencoded') {
    payload.data = kvToObj(urlencodedRows.value)
  } else if (bodyType.value === 'raw') {
    payload.json = rawBody.value || null
  }
  return payload
}

const handleSubmit = async () => {
  if (!formData.value.name.trim()) return alert('请输入接口名称')
  if (!urlPath.value.trim() && !urlPrefix.value) return alert('请输入接口路径')
  if (bodyType.value === 'json' && jsonError.value) return alert('JSON Body 格式有误，请检查')
  saving.value = true
  try {
    if (editingId.value) {
      await updateEndpoint(editingId.value, buildPayload())
      router.push('/endpoints')
    } else {
      const res = await createEndpoint(buildPayload())
      const newId = res.result?.id || res.id
      router.push(newId ? `/endpoints/${newId}` : '/endpoints')
    }
  } catch (e) {
    alert((editingId.value ? '更新' : '创建') + '失败: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  loading.value = true
  const plId = userStore.currentProductLine?.id

  const [pr, sr] = await Promise.all([
    getProjects({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
    getServices({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
  ])
  projects.value = pr.result?.list || []
  services.value = sr.result?.list || []

  const id = route.params.id
  if (id) {
    editingId.value = id
    try {
      const res = await getEndpointDetail(id)
      const data = (res && typeof res === 'object' && 'result' in res) ? res.result : res
      console.log('[编辑接口] API 返回数据:', data)
      formData.value.name        = data.name || ''
      formData.value.method      = data.method || 'GET'
      formData.value.project     = data.project || null
      formData.value.description = data.description || ''
      urlPath.value              = data.url || ''
      urlPrefix.value            = data.service_key || ''

      if (data.headers) {
        headers.value = Object.entries(data.headers).map(([k, v]) => ({ enabled: true, k, v, desc: '' }))
        if (!headers.value.length) headers.value = [{ enabled: true, k: '', v: '', desc: '' }]
      }
      if (data.params) {
        queryParams.value = Object.entries(data.params).map(([k, v]) => ({ enabled: true, k, v, desc: '' }))
        if (!queryParams.value.length) queryParams.value = [{ enabled: true, k: '', v: '', desc: '' }]
      }
      // 回显 body（API 返回 json / data 字段）
      if (data.json) {
        bodyType.value  = 'json'
        jsonBody.value  = JSON.stringify(data.json, null, 2)
      } else if (data.data) {
        bodyType.value = 'form-data'
        formDataRows.value = Object.entries(data.data).map(([k, v]) => ({ enabled: true, k, v, desc: '' }))
        if (!formDataRows.value.length) formDataRows.value = [{ enabled: true, k: '', v: '', desc: '' }]
      } else {
        bodyType.value = 'none'
      }
    } catch (e) {
      alert('加载接口详情失败')
      router.push('/endpoints')
    }
  } else if (projects.value.length && !formData.value.project) {
    formData.value.project = projects.value[0].id
  }

  loading.value = false
})
</script>

<style scoped>
/* ─── 页面容器 ─── */
.endpoint-form-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 10px;
  color: var(--color-text-secondary, #6b7280);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn-back:hover {
  color: var(--color-text-primary, #111827);
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
  color: var(--color-text-secondary, #6b7280);
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

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn--primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-2px);
}

.btn--primary:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--ghost {
  background: white;
  color: var(--color-text-secondary, #6b7280);
  border: 1.5px solid #e5e7eb;
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-text-primary, #111827);
  border-color: #d1d5db;
  background: #f9fafb;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

/* ─── 表单卡片 ─── */
.form-card {
  background: white;
  border: 1px solid var(--color-border, #e5e7eb);
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
}

.form-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
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

.form-card__title {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  line-height: 1.3;
  margin-bottom: 4px;
}

.form-card__subtitle {
  font-size: 13px;
  color: var(--color-text-secondary, #6b7280);
}

.form-card__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.form-card__body {
  padding: 28px;
}

/* ─── 分区块 ─── */
.section-block {
  margin-bottom: 32px;
}

.section-block:last-child {
  margin-bottom: 0;
}

.section-block__title {
  font-size: 15px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e5e7eb;
}

/* ─── 表单行 ─── */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;
}

/* ─── 表单组 ─── */
.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--color-text-secondary, #6b7280);
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

.required {
  color: #ef4444;
}

/* ─── 表单输入 ─── */
.form-input,
.form-select,
.form-textarea {
  padding: 9px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  color: var(--color-text-primary, #111827);
  background: white;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #9ca3af;
}

.form-textarea {
  resize: vertical;
  line-height: 1.6;
}

.form-select {
  cursor: pointer;
}

/* ─── 请求方法按钮 ─── */
.method-options {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.method-btn {
  padding: 7px 16px;
  border-radius: 8px;
  border: 1.5px solid #e5e7eb;
  cursor: pointer;
  font-size: 13px;
  font-weight: 700;
  background: white;
  color: var(--color-text-secondary, #6b7280);
  transition: all 0.15s;
  outline: none;
}

.method-btn:hover {
  border-color: #3B82F6;
  color: #3B82F6;
}

.method-btn.active.m-get    { background: #dbeafe; color: #1d4ed8; border-color: #3b82f6; }
.method-btn.active.m-post   { background: #dcfce7; color: #15803d; border-color: #22c55e; }
.method-btn.active.m-put    { background: #fef3c7; color: #b45309; border-color: #f59e0b; }
.method-btn.active.m-delete { background: #fee2e2; color: #dc2626; border-color: #ef4444; }
.method-btn.active.m-patch  { background: #f3e8ff; color: #7c3aed; border-color: #a855f7; }

/* ─── URL 输入组 ─── */
.url-input-group {
  display: flex;
  align-items: center;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.15s, box-shadow 0.15s;
}

.url-input-group:focus-within {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.url-prefix-select {
  border: none;
  border-right: 1px solid #e5e7eb;
  background: #f9fafb;
  padding: 9px 12px;
  font-size: 13px;
  outline: none;
  min-width: 160px;
  max-width: 300px;
  cursor: pointer;
  color: var(--color-text-primary, #111827);
}

.url-sep {
  padding: 0 6px;
  color: var(--color-text-secondary, #6b7280);
  background: #f9fafb;
  border-right: 1px solid #e5e7eb;
  line-height: 42px;
  font-size: 15px;
  user-select: none;
}

.url-path-input {
  border: none;
  flex: 1;
  padding: 9px 12px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  outline: none;
  background: white;
  color: var(--color-text-primary, #111827);
}

.url-preview {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 6px;
  display: block;
}

.url-preview code {
  color: #3B82F6;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-weight: 600;
  background: #eff6ff;
  padding: 1px 5px;
  border-radius: 4px;
}

.field-hint-row {
  margin-top: 4px;
}

.field-hint {
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
  margin-top: 6px;
  display: block;
}

.field-hint--warning {
  color: #b45309;
  background: #fef3c7;
  padding: 6px 10px;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
}

/* ─── 参数块 ─── */
.params-block {
  margin-bottom: 20px;
}

.params-block__header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.params-block__title {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-text-primary, #111827);
}

.params-block__count {
  background: #eff6ff;
  color: #3B82F6;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 700;
}

/* ─── 参数 Tabs ─── */
.params-tabs {
  display: flex;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-bottom: none;
  border-radius: 10px 10px 0 0;
  overflow: hidden;
}

.params-tab {
  flex: 1;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary, #6b7280);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.15s;
  outline: none;
}

.params-tab:hover {
  color: var(--color-text-primary, #111827);
  background: white;
}

.params-tab.active {
  color: #3B82F6;
  border-bottom-color: #3B82F6;
  background: white;
  font-weight: 700;
}

.tab-badge {
  background: #3B82F6;
  color: white;
  border-radius: 10px;
  padding: 1px 7px;
  font-size: 11px;
  font-weight: 700;
}

.tab-pane {
  padding: 14px;
  border: 1.5px solid #e5e7eb;
  border-top: none;
  border-radius: 0 0 10px 10px;
  background: white;
}

/* ─── KV 表格 ─── */
.kv-table {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 10px;
}

.kv-head {
  display: grid;
  grid-template-columns: 40px 1fr 1fr 1fr 32px;
  background: #f9fafb;
  color: var(--color-text-secondary, #6b7280);
  font-size: 11px;
  font-weight: 700;
  padding: 8px 10px;
  gap: 8px;
  border-bottom: 1px solid #e5e7eb;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kv-row {
  display: grid;
  grid-template-columns: 40px 1fr 1fr 1fr 32px;
  gap: 8px;
  padding: 7px 10px;
  border-bottom: 1px solid #f0f0f0;
  align-items: center;
}

.kv-row:last-child {
  border-bottom: none;
}

.kv-row:hover {
  background: #fafbfc;
}

.kv-check {
  width: 16px;
  height: 16px;
  cursor: pointer;
  accent-color: #3B82F6;
}

.kv-input {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 6px 8px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.15s;
}

.kv-input:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

.kv-desc {
  font-family: inherit;
  font-size: 12px;
  color: var(--color-text-secondary, #6b7280);
}

.kv-del {
  background: none;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  width: 24px;
  height: 24px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.15s, background 0.15s;
}

.kv-del:hover {
  color: #ef4444;
  background: #fef2f2;
}

.btn-add-row {
  background: none;
  border: 1.5px dashed #3B82F6;
  color: #3B82F6;
  border-radius: 8px;
  padding: 7px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  outline: none;
}

.btn-add-row:hover {
  background: #eff6ff;
  border-style: solid;
}

/* ─── Body 类型选择 ─── */
.body-type-bar {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.body-type-btn {
  padding: 5px 14px;
  border-radius: 6px;
  border: 1.5px solid #e5e7eb;
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-secondary, #6b7280);
  background: white;
  transition: all 0.15s;
  outline: none;
}

.body-type-btn:hover {
  border-color: #3B82F6;
  color: #3B82F6;
}

.body-type-btn.active {
  background: #3B82F6;
  color: white;
  border-color: #3B82F6;
}

.body-none {
  padding: 20px;
  text-align: center;
  color: var(--color-text-secondary, #6b7280);
  font-size: 13px;
}

/* ─── JSON 编辑器 ─── */
.json-editor-wrap {
  position: relative;
}

.json-editor {
  width: 100%;
  box-sizing: border-box;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  resize: vertical;
  outline: none;
  background: #1e1e2e;
  color: #cdd6f4;
  transition: border-color 0.15s;
}

.json-editor:focus {
  border-color: #3B82F6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.json-editor--error {
  border-color: #ef4444;
}

.json-error {
  font-size: 12px;
  color: #ef4444;
  margin-top: 4px;
  display: block;
}

/* ─── 底部操作 ─── */
.form-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .form-card__header {
    flex-direction: column;
    gap: 12px;
  }

  .form-card__actions {
    width: 100%;
  }

  .form-card__actions .btn {
    flex: 1;
  }

  .params-block__header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
}
</style>
