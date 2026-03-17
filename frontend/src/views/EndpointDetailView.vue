<template>
  <div class="endpoint-detail">
    <div class="detail-header">
      <button @click="$router.back()" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button v-if="!editing" @click="startEdit" class="btn btn-primary">编辑接口</button>
        <button v-if="editing" @click="handleSubmit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        <button v-if="editing" @click="cancelEdit" class="btn btn-refresh">取消</button>
        <button v-if="!editing" @click="deleteEndpointItem" class="btn btn-danger">删除接口</button>
      </div>
    </div>

    <div v-if="endpoint" class="detail-content">
      <!-- 查看模式 -->
      <div v-if="!editing" class="info-card card">
        <div class="endpoint-header">
          <h2>{{ endpoint.name }}</h2>
          <span class="method-badge" :class="`method-${endpoint.method.toLowerCase()}`">{{ endpoint.method }}</span>
        </div>
        <div class="info-grid">
          <div class="info-item full-width">
            <label>接口地址</label>
            <code class="url-display">
              <span v-if="endpoint.service_key" class="url-service-tag">{{{ endpoint.service_key }}}</span>
              <span v-if="endpoint.service_key" class="url-sep-text"> + </span>
              <span>{{ endpoint.url }}</span>
            </code>
            <span v-if="endpoint.service_key" class="url-hint">执行时 {{{ endpoint.service_key }}} 将被替换为所选环境的实际 URL</span>
          </div>
          <div class="info-item">
            <label>所属项目</label>
            <span class="project-link" @click="router.push(`/projects/${endpoint.project}`)">
              {{ endpoint.project_name || `项目 #${endpoint.project}` }}
            </span>
          </div>
          <div class="info-item">
            <label>创建时间</label>
            <span>{{ formatDate(endpoint.created_at) }}</span>
          </div>
          <div v-if="endpoint.description" class="info-item full-width">
            <label>描述</label>
            <span>{{ endpoint.description }}</span>
          </div>
        </div>
        <div class="params-section">
          <div v-if="hasKeys(endpoint.params)" class="param-block"><h4>查询参数</h4><pre>{{ JSON.stringify(endpoint.params, null, 2) }}</pre></div>
          <div v-if="hasKeys(endpoint.headers)" class="param-block"><h4>请求头</h4><pre>{{ JSON.stringify(endpoint.headers, null, 2) }}</pre></div>
          <div v-if="hasKeys(endpoint.data)" class="param-block"><h4>表单参数</h4><pre>{{ JSON.stringify(endpoint.data, null, 2) }}</pre></div>
          <div v-if="hasKeys(endpoint.json)" class="param-block"><h4>JSON 参数</h4><pre>{{ JSON.stringify(endpoint.json, null, 2) }}</pre></div>
          <div v-if="!hasKeys(endpoint.params) && !hasKeys(endpoint.headers) && !hasKeys(endpoint.data) && !hasKeys(endpoint.json)" class="empty-params">暂无参数</div>
        </div>
      </div>

      <!-- 编辑模式 -->
      <div v-else class="info-card card">
        <h3 class="edit-title">编辑接口</h3>
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>接口名称 <span class="required">*</span></label>
            <input v-model="formData.name" required />
          </div>
          <div class="form-group">
            <label>所属项目</label>
            <select v-model="formData.project">
              <option :value="null">不指定</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>请求方法 <span class="required">*</span></label>
            <div class="method-options">
              <label v-for="m in ['GET','POST','PUT','DELETE','PATCH']" :key="m"
                class="method-radio" :class="{ active: formData.method === m, ['m-'+m.toLowerCase()]: true }">
                <input type="radio" v-model="formData.method" :value="m" hidden />{{ m }}
              </label>
            </div>
          </div>
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
              中为各环境配置「服务 URL」（变量名即为 service_key）
            </span>
            <span v-else class="field-hint">服务标识来自环境管理中各环境的「变量名」字段，套件执行时自动匹配所选环境的实际 URL</span>
          </div>
          <div class="form-group">
            <label>描述</label>
            <input v-model="formData.description" placeholder="可选备注" />
          </div>
          <div class="section-title">Headers</div>
          <div class="params-panel">
            <div class="tab-pane">
              <div class="kv-table">
                <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                <div v-for="(row, i) in editHeaders" :key="i" class="kv-row">
                  <input type="checkbox" v-model="row.enabled" class="kv-check" />
                  <input v-model="row.k" placeholder="Key" class="kv-input" />
                  <input v-model="row.v" placeholder="Value" class="kv-input" />
                  <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                  <button type="button" class="kv-del" @click="editHeaders.splice(i,1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="editHeaders.push({enabled:true,k:'',v:'',desc:''})">+ 添加请求头</button>
            </div>
          </div>

          <!-- 入参 -->
          <div class="section-title">入参</div>
          <div class="params-panel">
            <div class="params-tabs">
              <button type="button" v-for="t in editTabs" :key="t.key"
                class="params-tab" :class="{ active: editActiveTab === t.key }"
                @click="editActiveTab = t.key">
                {{ t.label }}
                <span v-if="editTabBadge(t.key)" class="tab-badge">{{ editTabBadge(t.key) }}</span>
              </button>
            </div>
            <div v-show="editActiveTab === 'params'" class="tab-pane">
              <div class="kv-table">
                <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                <div v-for="(row, i) in editQueryParams" :key="i" class="kv-row">
                  <input type="checkbox" v-model="row.enabled" class="kv-check" />
                  <input v-model="row.k" placeholder="Key" class="kv-input" />
                  <input v-model="row.v" placeholder="Value" class="kv-input" />
                  <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                  <button type="button" class="kv-del" @click="editQueryParams.splice(i,1)">✕</button>
                </div>
              </div>
              <button type="button" class="btn-add-row" @click="editQueryParams.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
            </div>
            <div v-show="editActiveTab === 'body'" class="tab-pane">
              <div class="body-type-bar">
                <label v-for="bt in bodyTypes" :key="bt.key" class="body-type-radio" :class="{ active: editBodyType === bt.key }">
                  <input type="radio" v-model="editBodyType" :value="bt.key" hidden />{{ bt.label }}
                </label>
              </div>
              <div v-if="editBodyType === 'none'" class="body-none">此请求没有 Body</div>
              <div v-else-if="editBodyType === 'form-data'">
                <div class="kv-table">
                  <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                  <div v-for="(row, i) in editFormDataRows" :key="i" class="kv-row">
                    <input type="checkbox" v-model="row.enabled" class="kv-check" />
                    <input v-model="row.k" placeholder="Key" class="kv-input" />
                    <input v-model="row.v" placeholder="Value" class="kv-input" />
                    <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                    <button type="button" class="kv-del" @click="editFormDataRows.splice(i,1)">✕</button>
                  </div>
                </div>
                <button type="button" class="btn-add-row" @click="editFormDataRows.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
              </div>
              <div v-else-if="editBodyType === 'urlencoded'">
                <div class="kv-table">
                  <div class="kv-head"><span>启用</span><span>Key</span><span>Value</span><span>备注</span><span></span></div>
                  <div v-for="(row, i) in editUrlencodedRows" :key="i" class="kv-row">
                    <input type="checkbox" v-model="row.enabled" class="kv-check" />
                    <input v-model="row.k" placeholder="Key" class="kv-input" />
                    <input v-model="row.v" placeholder="Value" class="kv-input" />
                    <input v-model="row.desc" placeholder="备注" class="kv-input kv-desc" />
                    <button type="button" class="kv-del" @click="editUrlencodedRows.splice(i,1)">✕</button>
                  </div>
                </div>
                <button type="button" class="btn-add-row" @click="editUrlencodedRows.push({enabled:true,k:'',v:'',desc:''})">+ 添加</button>
              </div>
              <div v-else-if="editBodyType === 'json'" class="json-editor-wrap">
                <textarea v-model="editJsonBody" rows="10" class="json-editor" placeholder='{
  "key": "value"
}'></textarea>
                <span v-if="editJsonError" class="json-error">⚠ JSON 格式有误</span>
              </div>
              <div v-else-if="editBodyType === 'raw'" class="json-editor-wrap">
                <textarea v-model="editRawBody" rows="10" class="json-editor" placeholder="raw body content"></textarea>
              </div>
            </div>
          </div>
        </form>
      </div>

      <!-- 关联用例 -->
      <div v-if="!editing" class="related-section">
        <div class="section-card card">
          <h3>关联用例 ({{ cases.length }})</h3>
          <div class="list-items">
            <div v-for="item in cases" :key="item.id" class="list-item" @click="viewCase(item.id)">
              <span class="item-name">{{ item.name }}</span>
            </div>
            <div v-if="!cases.length" class="empty-state">暂无关联用例</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEndpointDetail, updateEndpoint, deleteEndpoint } from '@/api/endpoint'
import { confirm } from '@/composables/useConfirm'
import { getCases } from '@/api/case'
import { getProjects } from '@/api/project'
import { getEnvironments, getServices } from '@/api/suite'
import { useUserStore } from '@/stores/user'

const route  = useRoute()
const router = useRouter()
const userStore = useUserStore()

const endpoint     = ref(null)
const cases        = ref([])
const projects     = ref([])
const services     = ref([])  // 服务注册表
const editing      = ref(false)
const saving       = ref(false)
const urlPrefix    = ref('')
const urlPath      = ref('')

// 编辑模式 KV 状态
const editHeaders        = ref([{ enabled: true, k: '', v: '', desc: '' }])
const editQueryParams    = ref([{ enabled: true, k: '', v: '', desc: '' }])
const editFormDataRows   = ref([{ enabled: true, k: '', v: '', desc: '' }])
const editUrlencodedRows = ref([{ enabled: true, k: '', v: '', desc: '' }])
const editActiveTab      = ref('params')
const editBodyType       = ref('none')
const editJsonBody       = ref('')
const editRawBody        = ref('')
const editJsonError      = ref(false)

const editTabs = [
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
const editTabBadge = (key) => {
  if (key === 'params') return editQueryParams.value.filter(r => r.enabled && r.k).length || null
  if (key === 'body')   return editBodyType.value !== 'none' ? '●' : null
  return null
}

const kvToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.enabled && r.k?.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}

const objToKvRows = (obj) => {
  if (!obj || typeof obj !== 'object' || Array.isArray(obj)) return [{ enabled: true, k: '', v: '', desc: '' }]
  return Object.entries(obj).map(([k, v]) => ({ enabled: true, k, v: String(v), desc: '' }))
}

const formData = ref({ name: '', method: 'GET', project: null, description: '' })

const fullUrl = computed(() => {
  const path = urlPath.value ? '/' + urlPath.value.replace(/^\//, '') : ''
  if (urlPrefix.value) {
    return `{${urlPrefix.value}}` + path || '（请输入路径）'
  }
  return path || '（请输入路径）'
})

const parseJson = (val) => {
  if (!val?.trim()) return null
  try { return JSON.parse(val) } catch { return val }
}

const splitUrl = (ep, svcs) => {
  // 新格式：ep 有 service_key，直接用
  if (ep.service_key) return { prefix: ep.service_key, path: ep.url?.replace(/^\//, '') || '' }
  // 旧格式：url 是完整路径，service_key 为空，直接作为路径
  return { prefix: '', path: ep.url || '' }
}

const loadEndpoint = async () => {
  const res = await getEndpointDetail(route.params.id)
  endpoint.value = res.result
}

const loadCases = async () => {
  const res = await getCases({ endpoint: route.params.id })
  cases.value = res.result?.list || []
}

const startEdit = () => {
  const ep = endpoint.value
  const { prefix, path } = splitUrl(ep, services.value)
  urlPrefix.value = prefix
  urlPath.value   = path
  formData.value = {
    name:        ep.name,
    method:      ep.method,
    project:     ep.project,
    description: ep.description || '',
  }
  // 反解析 headers
  editHeaders.value = ep.headers ? objToKvRows(ep.headers) : [{ enabled: true, k: '', v: '', desc: '' }]
  // 反解析 params (query)
  editQueryParams.value = ep.params ? objToKvRows(ep.params) : [{ enabled: true, k: '', v: '', desc: '' }]
  // 反解析 body
  if (ep.json) {
    editBodyType.value  = 'json'
    editJsonBody.value  = JSON.stringify(ep.json, null, 2)
  } else if (ep.data) {
    editBodyType.value     = 'form-data'
    editFormDataRows.value = objToKvRows(ep.data)
  } else {
    editBodyType.value = 'none'
  }
  editActiveTab.value = 'params'
  editing.value = true
}

const cancelEdit = () => { editing.value = false }

const handleSubmit = async () => {
  saving.value = true
  try {
    let json = null, data = null
    if (editBodyType.value === 'json') {
      try { json = editJsonBody.value.trim() ? JSON.parse(editJsonBody.value) : null } catch { alert('JSON Body 格式有误'); saving.value = false; return }
    } else if (editBodyType.value === 'form-data') {
      data = kvToObj(editFormDataRows.value)
    } else if (editBodyType.value === 'urlencoded') {
      data = kvToObj(editUrlencodedRows.value)
    } else if (editBodyType.value === 'raw') {
      json = editRawBody.value || null
    }
    await updateEndpoint(route.params.id, {
      name:        formData.value.name,
      method:      formData.value.method,
      url:         urlPath.value ? '/' + urlPath.value.replace(/^\//, '') : '',
      service_key: urlPrefix.value || '',
      project:     formData.value.project,
      description: formData.value.description,
      headers:     kvToObj(editHeaders.value),
      params:      kvToObj(editQueryParams.value),
      json,
      data,
    })
    editing.value = false
    await loadEndpoint()
  } catch (e) {
    alert('保存失败，请检查内容是否正确')
  } finally {
    saving.value = false
  }
}

const deleteEndpointItem = async () => {
  const confirmed = await confirm('确定要删除这个接口吗？', { type: 'danger' })
  if (!confirmed) return
  await deleteEndpoint(route.params.id)
  router.push('/endpoints')
}

const viewCase = (id) => router.push(`/cases/${id}`)
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

// 判断对象/字符串是否有实际内容（过滤空对象、null、undefined）
const hasKeys = (val) => {
  if (!val) return false
  if (typeof val === 'string') return val.trim().length > 0
  if (typeof val === 'object') return Object.keys(val).length > 0
  return !!val
}

onMounted(async () => {
  const plId = userStore.currentProductLine?.id
  const [, , pr, sr] = await Promise.all([
    loadEndpoint(),
    loadCases(),
    getProjects({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
    getServices({ page_size: 200, ...(plId ? { product_line: plId } : {}) }),
  ])
  projects.value  = pr.result?.list || []
  services.value  = sr.result?.list || []
})
</script>

<style scoped>
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.btn-back { background: white; border: 1px solid var(--border); color: var(--text); }
.header-actions { display: flex; gap: 12px; }
.info-card { margin-bottom: 32px; padding: 32px; }
.edit-title { font-size: 18px; font-weight: 700; color: var(--primary); margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--border); }
.endpoint-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }
.endpoint-header h2 { font-size: 26px; font-weight: 700; color: var(--primary); }
.method-badge { padding: 5px 12px; border-radius: 6px; font-size: 13px; font-weight: 700; }
.method-get    { background: #e3f2fd; color: #1976d2; }
.method-post   { background: #e8f5e9; color: #388e3c; }
.method-put    { background: #fff3e0; color: #f57c00; }
.method-delete { background: #ffebee; color: #d32f2f; }
.method-patch  { background: #f3e5f5; color: #7b1fa2; }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px,1fr)); gap: 20px; margin-bottom: 24px; }
.info-item { display: flex; flex-direction: column; gap: 6px; }
.info-item.full-width { grid-column: 1/-1; }
.info-item label { font-size: 12px; color: var(--text-light); font-weight: 600; text-transform: uppercase; letter-spacing: .04em; }
.url-display { background: var(--bg); padding: 10px 14px; border-radius: 6px; font-family: 'Monaco','Courier New',monospace; font-size: 13px; color: var(--primary); display: flex; align-items: center; flex-wrap: wrap; gap: 4px; }
.url-service-tag { background: #e3f2fd; color: #1565c0; padding: 1px 6px; border-radius: 4px; font-weight: 600; }
.url-sep-text { color: #aaa; font-size: 12px; }
.url-hint { font-size: 11px; color: #aaa; margin-top: 4px; display: block; font-family: inherit; }
.project-link { color: var(--accent); cursor: pointer; text-decoration: underline; text-underline-offset: 3px; }
.params-section { display: grid; gap: 16px; }
.param-block h4 { font-size: 13px; font-weight: 600; margin-bottom: 6px; color: var(--text); }
.param-block pre { background: var(--bg); padding: 14px; border-radius: 8px; font-family: 'Monaco','Courier New',monospace; font-size: 12px; line-height: 1.6; overflow-x: auto; }
.related-section { display: grid; gap: 24px; }
.section-card h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; }
.list-items { display: flex; flex-direction: column; gap: 8px; }
.list-item { padding: 10px 14px; background: var(--bg); border-radius: 8px; cursor: pointer; transition: all .2s; }
.list-item:hover { background: #e8f4f8; transform: translateX(4px); }
.empty-state { text-align: center; padding: 24px; color: var(--text-light); }
.form-row { display: grid; grid-template-columns: 1fr 160px; gap: 16px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.required { color: var(--danger); }
.label-hint { font-size: 11px; color: var(--text-light); font-weight: 400; }
.url-input-group { display: flex; align-items: center; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; }
.url-input-group:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(52,152,219,.1); }
.url-prefix-select { border: none; border-right: 1px solid var(--border); background: #f5f7fa; padding: 10px 12px; font-size: 13px; outline: none; max-width: 260px; min-width: 100px; cursor: pointer; }
.url-sep { padding: 0 6px; color: var(--text-light); background: #f5f7fa; border-right: 1px solid var(--border); line-height: 42px; font-size: 15px; }
.url-path-input { border: none; flex: 1; padding: 10px 12px; font-size: 14px; font-family: 'Monaco','Courier New',monospace; outline: none; }
.url-preview { font-size: 12px; color: var(--text-light); margin-top: 6px; display: block; }
.preview-note { margin-left: 8px; color: #aaa; font-style: italic; }
.field-hint { font-size: 12px; color: var(--text-light); margin-top: 6px; display: block; }
.service-hint { color: #e65100; }
.hint-link { color: var(--accent); text-decoration: underline; }
.url-preview code { color: var(--accent); font-family: monospace; }
.params-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
textarea { font-family: 'Monaco','Courier New',monospace; font-size: 13px; resize: vertical; }
.method-options { display: flex; gap: 8px; flex-wrap: wrap; }
.method-radio { padding: 6px 18px; border-radius: 6px; border: 1px solid var(--border); cursor: pointer; font-size: 13px; font-weight: 600; color: var(--text-light); background: white; user-select: none; transition: all .15s; }
.method-radio:hover { border-color: var(--accent); color: var(--accent); }
.method-radio.active.m-get    { background: #e3f2fd; color: #1976d2; border-color: #1976d2; }
.method-radio.active.m-post   { background: #e8f5e9; color: #388e3c; border-color: #388e3c; }
.method-radio.active.m-put    { background: #fff3e0; color: #f57c00; border-color: #f57c00; }
.method-radio.active.m-delete { background: #ffebee; color: #d32f2f; border-color: #d32f2f; }
.method-radio.active.m-patch  { background: #f3e5f5; color: #7b1fa2; border-color: #7b1fa2; }
.section-title { font-size: 13px; font-weight: 700; color: var(--primary); margin: 24px 0 10px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); display: inline-block; }
.params-panel { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; margin-bottom: 20px; }
.params-tabs { display: flex; background: #f8f9fa; border-bottom: 1px solid var(--border); }
.params-tab { background: none; border: none; border-bottom: 2px solid transparent; padding: 10px 20px; font-size: 13px; font-weight: 500; color: var(--text-light); cursor: pointer; display: flex; align-items: center; gap: 6px; transition: all .15s; }
.params-tab:hover { color: var(--text); }
.params-tab.active { color: var(--accent); border-bottom-color: var(--accent); background: white; font-weight: 600; }
.tab-badge { background: var(--accent); color: white; border-radius: 10px; padding: 1px 7px; font-size: 11px; font-weight: 700; }
.tab-pane { padding: 16px; }
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
.body-type-bar { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.body-type-radio { padding: 4px 14px; border-radius: 5px; border: 1px solid var(--border); cursor: pointer; font-size: 12px; font-weight: 500; color: var(--text-light); background: white; user-select: none; transition: all .15s; }
.body-type-radio:hover { border-color: var(--accent); color: var(--accent); }
.body-type-radio.active { background: var(--accent); color: white; border-color: var(--accent); }
.body-none { padding: 20px; text-align: center; color: var(--text-light); font-size: 13px; }
.json-editor-wrap { position: relative; }
.json-editor { width: 100%; box-sizing: border-box; font-family: 'Monaco','Courier New',monospace; font-size: 13px; line-height: 1.6; border: 1px solid var(--border); border-radius: 6px; padding: 12px; resize: vertical; outline: none; background: #1e1e2e; color: #cdd6f4; }
.json-editor:focus { border-color: var(--accent); }
.json-error { font-size: 12px; color: var(--danger); margin-top: 4px; display: block; }
.empty-params { padding: 16px; text-align: center; color: var(--text-light); font-size: 13px; background: var(--bg); border-radius: 8px; }
</style>