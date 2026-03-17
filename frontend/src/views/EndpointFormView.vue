<template>
  <div class="endpoint-form-view">
    <div class="detail-header">
      <button @click="$router.back()" class="btn btn-back">← 返回</button>
      <h2 class="page-title">➕ 新建接口</h2>
    </div>

    <div class="form-card card">
      <form @submit.prevent="handleSubmit">

        <!-- 接口名称 -->
        <div class="form-group">
          <label>接口名称 <span class="required">*</span></label>
          <input v-model="formData.name" required placeholder="如：获取用户信息" />
        </div>

        <!-- 所属项目 -->
        <div class="form-group">
          <label>所属项目</label>
          <select v-model="formData.project">
            <option :value="null">不指定</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>

        <!-- 请求方法 -->
        <div class="form-group">
          <label>请求方法 <span class="required">*</span></label>
          <div class="method-options">
            <label v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m"
              class="method-radio" :class="{ active: formData.method === m, ['m-'+m.toLowerCase()]: true }">
              <input type="radio" v-model="formData.method" :value="m" hidden />{{ m }}
            </label>
          </div>
        </div>

        <!-- 接口地址 -->
        <div class="form-group">
          <label>接口地址 <span class="required">*</span></label>
          <div class="url-input-group">
            <select v-model="urlPrefix" class="url-prefix-select">
              <option value="">无服务（填完整 URL）</option>
              <option v-for="svc in services" :key="svc.key" :value="svc.key">
                {{ svc.name }} ({{ svc.key }})
              </option>
            </select>
            <span class="url-sep">/</span>
            <input v-model="urlPath" class="url-path-input" placeholder="api/users" />
          </div>
          <span class="url-preview">路径预览：<code>{{ fullUrl }}</code><span class="preview-note">（执行时由所选环境替换 {服务} 为实际域名）</span></span>
          <span v-if="!services.length" class="field-hint service-hint">
            ⚠ 暂无可用服务，请先在
            <a href="/environments" class="hint-link">环境管理</a>
            中为各环境配置「服务 URL」（填写变量名即为 service_key）
          </span>
          <span v-else class="field-hint">服务标识来自环境管理中各环境的「变量名」字段，套件执行时自动匹配所选环境的实际 URL</span>
        </div>

        <!-- 请求头 -->
        <div class="section-title">Headers</div>
        <div class="params-panel">
          <div class="tab-pane">
            <div class="kv-table">
              <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
              <div v-for="(row, i) in headers" :key="i" class="kv-row">
                <input type="checkbox" v-model="row.enabled" class="kv-check" />
                <input v-model="row.k" placeholder="Key" class="kv-input" />
                <input v-model="row.v" placeholder="Value" class="kv-input" />
                <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                <button type="button" class="kv-del" @click="headers.splice(i,1)">✕</button>
              </div>
            </div>
            <button type="button" class="btn-add-row" @click="headers.push({enabled:true,k:'',v:'',desc:''})">+ 添加请求头</button>
          </div>
        </div>

        <!-- 入参 -->
        <div class="section-title">入参</div>

        <!-- Postman 风格 Tab 入参区 -->
        <div class="params-panel">
          <div class="params-tabs">
            <button type="button" v-for="t in tabs" :key="t.key"
              class="params-tab" :class="{ active: activeTab === t.key }"
              @click="activeTab = t.key">
              {{ t.label }}
              <span v-if="tabBadge(t.key)" class="tab-badge">{{ tabBadge(t.key) }}</span>
            </button>
          </div>

          <!-- Query Params -->
          <div v-show="activeTab === 'params'" class="tab-pane">
            <div class="kv-table">
              <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
              <div v-for="(row, i) in queryParams" :key="i" class="kv-row">
                <input type="checkbox" v-model="row.enabled" class="kv-check" />
                <input v-model="row.k" placeholder="Key" class="kv-input" />
                <input v-model="row.v" placeholder="Value" class="kv-input" />
                <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                <button type="button" class="kv-del" @click="queryParams.splice(i,1)">✕</button>
              </div>
            </div>
            <button type="button" class="btn-add-row" @click="queryParams.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
          </div>

          <!-- Body -->
          <div v-show="activeTab === 'body'" class="tab-pane">
            <div class="body-type-bar">
              <label v-for="bt in bodyTypes" :key="bt.key"
                class="body-type-radio" :class="{ active: bodyType === bt.key }">
                <input type="radio" v-model="bodyType" :value="bt.key" hidden />{{ bt.label }}
              </label>
            </div>

            <!-- none -->
            <div v-if="bodyType === 'none'" class="body-none">此请求没有 Body</div>

            <!-- form-data -->
            <div v-else-if="bodyType === 'form-data'">
              <div class="kv-table">
                <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                <div v-for="(row, i) in formDataRows" :key="i" class="kv-row">
                  <input type="checkbox" v-model="row.enabled" class="kv-check" />
                  <input v-model="row.k" placeholder="Key" class="kv-input" />
                  <input v-model="row.v" placeholder="Value" class="kv-input" />
                  <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                  <button type="button" class="kv-del" @click="formDataRows.splice(i,1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="formDataRows.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
            </div>

            <!-- x-www-form-urlencoded -->
            <div v-else-if="bodyType === 'urlencoded'">
              <div class="kv-table">
                <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                <div v-for="(row, i) in urlencodedRows" :key="i" class="kv-row">
                  <input type="checkbox" v-model="row.enabled" class="kv-check" />
                  <input v-model="row.k" placeholder="Key" class="kv-input" />
                  <input v-model="row.v" placeholder="Value" class="kv-input" />
                  <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                  <button type="button" class="kv-del" @click="urlencodedRows.splice(i,1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="urlencodedRows.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
            </div>

            <!-- JSON -->
            <div v-else-if="bodyType === 'json'" class="json-editor-wrap">
              <textarea v-model="jsonBody" rows="10" class="json-editor"
                placeholder='{
  "key": "value"
}'></textarea>
              <span v-if="jsonError" class="json-error">⚠ JSON 格式有误</span>
            </div>

            <!-- Raw -->
            <div v-else-if="bodyType === 'raw'" class="json-editor-wrap">
              <textarea v-model="rawBody" rows="10" class="json-editor" placeholder="raw body content"></textarea>
            </div>
          </div>
        </div>

        <!-- 描述 -->
        <div class="form-group">
          <label>描述</label>
          <input v-model="formData.description" placeholder="可选备注" />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '✓ 创建接口' }}</button>
          <button type="button" class="btn btn-refresh" @click="$router.back()">取消</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createEndpoint } from '@/api/endpoint'
import { getProjects } from '@/api/project'
import { getEnvironments, getServices } from '@/api/suite'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const projects     = ref([])
const services     = ref([])  // 服务注册表
const saving       = ref(false)
const urlPrefix    = ref('')
const urlPath      = ref('')
const activeTab    = ref('params')
const bodyType     = ref('json')
const jsonBody     = ref('')
const rawBody      = ref('')
const jsonError    = ref(false)

const headers        = ref([{ enabled: true, k: '', v: '', desc: '' }])
const queryParams    = ref([{ enabled: true, k: '', v: '', desc: '' }])
const formDataRows   = ref([{ enabled: true, k: '', v: '', desc: '' }])
const urlencodedRows = ref([{ enabled: true, k: '', v: '', desc: '' }])

const formData = ref({ name: '', method: 'GET', project: null, description: '' })

const tabs = [
  { key: 'params',  label: 'Query Params' },
  { key: 'body',    label: 'Body' },
]
const bodyTypes = [
  { key: 'none',       label: 'none' },
  { key: 'json',       label: 'JSON' },
  { key: 'form-data',  label: 'form-data' },
  { key: 'urlencoded', label: 'x-www-form-urlencoded' },
  { key: 'raw',        label: 'raw' },
]

const tabBadge = (key) => {
  if (key === 'params')   return queryParams.value.filter(r => r.enabled && r.k).length || null
  if (key === 'body')     return bodyType.value !== 'none' ? '●' : null
  return null
}

const fullUrl = computed(() => {
  const path = urlPath.value ? '/' + urlPath.value.replace(/^\//, '') : ''
  if (urlPrefix.value) {
    return `{${urlPrefix.value}}` + path || '（请输入路径）'
  }
  return path || '（请输入路径）'
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
  if (!urlPath.value.trim() && !urlPrefix.value) return alert('请输入接口路径')
  if (bodyType.value === 'json' && jsonError.value) return alert('JSON Body 格式有误，请检查')
  saving.value = true
  try {
    const res = await createEndpoint(buildPayload())
    const newId = res.result?.id || res.id
    router.push(newId ? `/endpoints/${newId}` : '/endpoints')
  } catch (e) {
    alert('创建失败: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const plId = userStore.currentProductLine?.id
  const [pr, sr] = await Promise.all([
    getProjects({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
    getServices({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
  ])
  projects.value = pr.result?.list || []
  services.value = sr.result?.list || []
  if (projects.value.length && !formData.value.project) {
    formData.value.project = projects.value[0].id
  }
})
</script>

<style scoped>
.endpoint-form-view { display: flex; flex-direction: column; gap: 20px; }
.detail-header { display: flex; align-items: center; gap: 16px; }
.page-title { font-size: 20px; font-weight: 700; color: var(--primary); margin: 0; }
.btn-back { background: white; border: 1px solid var(--border); color: var(--text); }
.form-card { padding: 32px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.required { color: var(--danger); }

.method-options { display: flex; gap: 8px; flex-wrap: wrap; }
.method-radio { padding: 6px 18px; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-light); background: white; user-select: none; transition: all .15s; }
.method-radio:hover { border-color: var(--accent); color: var(--accent); }
.method-radio.active.m-get    { background: #e3f2fd; color: #1976d2; border-color: #1976d2; }
.method-radio.active.m-post   { background: #e8f5e9; color: #388e3c; border-color: #388e3c; }
.method-radio.active.m-put    { background: #fff3e0; color: #f57c00; border-color: #f57c00; }
.method-radio.active.m-delete { background: #ffebee; color: #d32f2f; border-color: #d32f2f; }
.method-radio.active.m-patch  { background: #f3e5f5; color: #7b1fa2; border-color: #7b1fa2; }

.url-input-group { display: flex; align-items: center; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.url-input-group:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(52,152,219,.1); }
.url-prefix-select { border: none; border-right: 1px solid var(--border); background: #f5f7fa; padding: 10px 12px; font-size: 13px; outline: none; max-width: 280px; min-width: 120px; cursor: pointer; }
.url-sep { padding: 0 6px; color: var(--text-light); background: #f5f7fa; border-right: 1px solid var(--border); line-height: 42px; font-size: 15px; }
.url-path-input { border: none; flex: 1; padding: 10px 12px; font-size: 14px; font-family: 'Monaco','Courier New',monospace; outline: none; background: white; }
.url-preview { font-size: 12px; color: var(--text-light); margin-top: 6px; display: block; }
.preview-note { margin-left: 8px; color: #aaa; font-style: italic; }
.field-hint { font-size: 12px; color: var(--text-light); margin-top: 6px; display: block; }
.service-hint { color: #e65100; }
.hint-link { color: var(--accent); text-decoration: underline; }
.url-preview code { color: var(--accent); font-family: monospace; }

/* Postman 风格 Tabs */
.params-panel { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
.params-tabs { display: flex; background: #f8f9fa; border-bottom: 1px solid var(--border); }
.params-tab { background: none; border: none; border-bottom: 2px solid transparent; padding: 10px 20px; font-size: 13px; font-weight: 500; color: var(--text-light); cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all .15s; }
.params-tab:hover { color: var(--text); }
.params-tab.active { color: var(--accent); border-bottom-color: var(--accent); background: white; font-weight: 600; }
.tab-badge { background: var(--accent); color: white; border-radius: 10px; padding: 1px 7px; font-size: 11px; font-weight: 700; }
.tab-pane { padding: 16px; }

/* KV 表格 */
.kv-table { border: 1px solid var(--border); border-radius: 6px; overflow: hidden; margin-bottom: 10px; }
.kv-head { display: grid; grid-template-columns: 36px 1fr 1fr 1fr 28px; background: var(--primary); color: white; font-size: 11px; font-weight: 600; padding: 7px 10px; gap: 8px; }
.kv-row  { display: grid; grid-template-columns: 36px 1fr 1fr 1fr 28px; gap: 8px; padding: 6px 10px; border-top: 1px solid var(--border); align-items: center; }
.kv-row:hover { background: #fafbfc; }
.kv-check { width: 16px; height: 16px; cursor: pointer; accent-color: var(--accent); }
.kv-input { border: 1px solid var(--border); border-radius: 4px; padding: 5px 8px; font-size: 13px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; }
.kv-input:focus { border-color: var(--accent); }
.kv-desc { font-family: inherit; font-size: 12px; color: var(--text-light); }
.kv-del { background: none; border: none; color: #ccc; cursor: pointer; font-size: 13px; }
.kv-del:hover { color: var(--danger); }
.btn-add-row { background: none; border: 1px dashed var(--accent); color: var(--accent); border-radius: 5px; padding: 4px 14px; font-size: 12px; cursor: pointer; }
.btn-add-row:hover { background: #e3f2fd; }

/* Body 类型选择 */
.body-type-bar { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.body-type-radio { padding: 4px 14px; border-radius: 5px; border: 1px solid var(--border); cursor: pointer; font-size: 12px; font-weight: 500; color: var(--text-light); background: white; user-select: none; transition: all .15s; }
.body-type-radio:hover { border-color: var(--accent); color: var(--accent); }
.body-type-radio.active { background: var(--accent); color: white; border-color: var(--accent); }
.body-none { padding: 20px; text-align: center; color: var(--text-light); font-size: 13px; }

/* JSON 编辑器 */
.json-editor-wrap { position: relative; }
.json-editor { width: 100%; box-sizing: border-box; font-family: 'Monaco','Courier New',monospace; font-size: 13px; line-height: 1.6; border: 1px solid var(--border); border-radius: 6px; padding: 12px; resize: vertical; outline: none; background: #1e1e2e; color: #cdd6f4; }
.json-editor:focus { border-color: var(--accent); }
.json-error { font-size: 12px; color: var(--danger); margin-top: 4px; display: block; }

.form-actions { display: flex; gap: 12px; margin-top: 8px; padding-top: 20px; border-top: 1px solid var(--border); }
.section-title { font-size: 13px; font-weight: 700; color: var(--primary); margin: 24px 0 10px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); display: inline-block; }
</style>