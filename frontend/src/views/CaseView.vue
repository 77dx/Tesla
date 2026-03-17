<template>
  <div class="case-view">
    <div class="toolbar">
      <button @click="showCreateDialog = true" class="btn btn-primary">
        ➕ 新建用例
      </button>
      <button @click="loadCases(1)" class="btn btn-refresh">↻ 刷新</button>
      <button @click="batchDelete" :disabled="!selectedIds.length" class="btn btn-batch-delete">
        🗑 删除选中 {{ selectedIds.length ? `(${selectedIds.length})` : '' }}
      </button>
    </div>

    <div class="filter-bar card">
      <div class="filter-input-wrap">
        <span class="filter-icon">🔍</span>
        <input v-model="searchText" class="filter-input" placeholder="搜索用例名称或ID..." @keyup.enter="handleSearch" />
      </div>
      <select v-model="filterProject" class="filter-select">
        <option value="">全部项目</option>
        <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
      </select>
      <select v-model="filterEndpoint" class="filter-select">
        <option value="">全部接口</option>
        <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
      </select>
      <button @click="handleSearch" class="btn btn-primary btn-sm">搜索</button>
      <button @click="resetFilter" class="btn btn-sm">重置</button>
    </div>
    
    <div class="table-container card">
      <table class="table">
        <thead>
          <tr>
            <th style="width:40px"><input type="checkbox" :checked="allSelected" @change="toggleAll" /></th>
            <th>ID</th>
            <th>用例名称</th>
            <th>所属接口</th>
            <th>所属项目</th>
            <th>更新人</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in cases" :key="item.id">
            <td><input type="checkbox" :value="item.id" v-model="selectedIds" /></td>
            <td class="cell-sm">{{ item.id }}</td>
            <td class="cell-md" :title="item.name">
              <a @click.prevent="viewDetail(item.id)" class="link-text">{{ item.name }}</a>
            </td>
            <td class="cell-md" :title="item.endpoint?.name || ''">{{ item.endpoint?.name || '-' }}</td>
            <td class="cell-md" :title="item.project_name || ''">{{ item.project_name || '-' }}</td>
            <td class="cell-sm">
              <span class="creator-badge">{{ item.created_by_name || '-' }}</span>
            </td>
            <td class="cell-md">{{ formatDate(item.created_at) }}</td>
            <td>
              <button @click="viewDetail(item.id)" class="btn-action btn-info">详情</button>
              <button @click="deleteCaseItem(item.id)" class="btn-action btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="!cases.length" class="empty-state">
        暂无数据
      </div>
      <div v-if="pagination.pageCount > 1" class="pagination">
        <span class="pagination-info">共 {{ pagination.itemCount }} 条</span>
        <button class="page-btn" :disabled="pagination.page <= 1" @click="changePage(pagination.page - 1)">‹</button>
        <button v-for="p in pagination.pageCount" :key="p" class="page-btn" :class="{ active: p === pagination.page }" @click="changePage(p)">{{ p }}</button>
        <button class="page-btn" :disabled="pagination.page >= pagination.pageCount" @click="changePage(pagination.page + 1)">›</button>
      </div>
    </div>
    
    <!-- 创建/编辑对话框 -->
    <div v-if="showCreateDialog" class="modal" @click.self="closeDialog">
      <div class="modal-content modal-tab">
        <div class="modal-header">
          <h3>{{ editingItem ? '编辑用例' : '新建用例' }}</h3>
          <button type="button" @click="closeDialog" class="btn-close">✕</button>
        </div>

        <!-- Tab 导航 -->
        <div class="tab-nav">
          <button v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key">{{ tab.label }}</button>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="tab-content">
            <!-- Tab 1: 基本信息 -->
            <div v-show="activeTab === 'basic'">
              <div class="form-group">
                <label>用例名称 *</label>
                <input v-model="formData.name" required placeholder="用例名称" />
              </div>
              <div class="form-row">
                <div class="form-group">
                  <label>所属接口</label>
                  <select v-model="formData.endpoint">
                    <option :value="null">请选择接口</option>
                    <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>所属项目</label>
                  <select v-model="formData.project">
                    <option :value="null">请选择项目</option>
                    <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label>Allure 标注 <span class="field-hint">(JSON 格式，可选)</span></label>
                <textarea v-model="formData.alluer" rows="4" placeholder='{"feature": "用户模块", "story": "登录"}'></textarea>
              </div>
            </div>

            <!-- Tab 2: 接口参数 -->
            <div v-show="activeTab === 'params'">
              <div class="form-group">
                <div class="param-type-row">
                  <label>接口参数</label>
                  <div class="param-type-tabs">
                    <button type="button" :class="['param-type-btn', formData.paramType==='json'?'active':'']"
                      @click="formData.paramType='json'">JSON Body</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='form'?'active':'']"
                      @click="formData.paramType='form'">Form Data</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='query'?'active':'']"
                      @click="formData.paramType='query'">Query Params</button>
                    <button type="button" :class="['param-type-btn', formData.paramType==='raw'?'active':'']"
                      @click="formData.paramType='raw'">原始 JSON</button>
                  </div>
                </div>
                <div v-if="formData.paramType==='json'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.jsonRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.jsonRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.jsonRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else-if="formData.paramType==='form'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.formRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.formRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.formRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else-if="formData.paramType==='query'">
                  <div class="kv-editor">
                    <div class="kv-header"><span>Key</span><span>Value</span><span></span></div>
                    <div v-for="(row,idx) in formData.queryRows" :key="idx" class="kv-row">
                      <input v-model="row.k" placeholder="key" class="kv-input" />
                      <input v-model="row.v" placeholder="value" class="kv-input" />
                      <button type="button" class="btn-remove-rule" @click="formData.queryRows.splice(idx,1)">✕</button>
                    </div>
                  </div>
                  <button type="button" class="btn-add-rule" @click="formData.queryRows.push({k:'',v:''})">+ 添加字段</button>
                </div>
                <div v-else>
                  <textarea v-model="formData.api_args" rows="7" placeholder='{"json":{"key":"value"}}'></textarea>
                </div>
              </div>
            </div>

            <!-- Tab 3: 数据提取 -->
            <div v-show="activeTab === 'extract'">
              <div class="extract-tip">
                接口响应后按 JSONPath 提取值，存为变量。后续用例在参数/请求头中使用 <code>${变量名}</code> 引用。
              </div>
              <div class="extract-label-row">
                <span class="extract-count">共 {{ editExtractRules.length }} 条规则</span>
                <button type="button" class="btn-add-rule" @click="addExtractRule">+ 添加规则</button>
              </div>
              <div v-if="editExtractRules.length" class="extract-editor">
                <div class="extract-editor-header">
                  <span>变量名</span><span>JSONPath 表达式</span><span class="col-index">取第几个</span><span></span>
                </div>
                <div v-for="(rule, idx) in editExtractRules" :key="idx" class="extract-editor-row">
                  <input v-model="rule.name" placeholder="token" class="rule-input" />
                  <input v-model="rule.expr" placeholder="$.data.token" class="rule-input" />
                  <input v-model.number="rule.index" type="number" min="0" placeholder="0" class="rule-input rule-index" />
                  <button type="button" class="btn-remove-rule" @click="removeExtractRule(idx)">✕</button>
                </div>
              </div>
              <div v-else class="empty-hint" style="padding:20px 0">暂无提取规则，点击「+ 添加规则」新增</div>
            </div>

            <!-- Tab 4: 断言 -->
            <div v-show="activeTab === 'validate'">
              <div class="assert-tip">按顺序执行所有断言规则，支持状态码、JSONPath、响应文本等来源。</div>
              <div class="assert-label-row">
                <span class="assert-count">共 {{ editAssertRules.length }} 条规则</span>
                <div class="assert-add-btns">
                  <button type="button" class="btn-add-assert" @click="addAssertRule('status_code')">+ 状态码</button>
                  <button type="button" class="btn-add-assert" @click="addAssertRule('jsonpath')">+ JSONPath</button>
                  <button type="button" class="btn-add-assert" @click="addAssertRule('text')">+ 响应文本</button>
                </div>
              </div>
              <div v-if="editAssertRules.length" class="assert-editor">
                <div v-for="(rule, idx) in editAssertRules" :key="idx" class="assert-rule-row">
                  <span class="assert-idx">{{ idx + 1 }}</span>
                  <input v-model="rule.name" placeholder="断言描述" class="assert-input assert-name" />
                  <select v-model="rule.type" class="assert-select assert-type">
                    <option value="eq">等于 (eq)</option>
                    <option value="not_eq">不等于 (not_eq)</option>
                    <option value="contains">包含 (contains)</option>
                    <option value="not_contains">不包含 (not_contains)</option>
                    <option value="exists">存在 (exists)</option>
                    <option value="regex">正则匹配 (regex)</option>
                  </select>
                  <select v-model="rule.source" class="assert-select assert-source">
                    <option value="status_code">状态码</option>
                    <option value="jsonpath">JSONPath</option>
                    <option value="text">响应文本</option>
                  </select>
                  <input v-if="rule.source !== 'status_code'" v-model="rule.expr"
                    :placeholder="rule.source === 'jsonpath' ? '$.data.code' : '正则表达式'"
                    class="assert-input assert-expr" />
                  <span v-else class="assert-expr-placeholder">HTTP 状态码</span>
                  <input v-if="rule.type !== 'exists'" v-model="rule.expect" placeholder="期望值" class="assert-input assert-expect" />
                  <span v-else class="assert-expr-placeholder assert-exists-hint">值存在且非空即通过</span>
                  <button type="button" class="btn-remove-rule" @click="editAssertRules.splice(idx,1)">✕</button>
                </div>
              </div>
              <div v-else class="empty-hint" style="padding:20px 0">暂无断言规则，点击上方按钮添加</div>
              <div v-if="editAssertRules.length" class="assert-preview">
                <span class="assert-preview-label">JSON 预览</span>
                <pre class="assert-preview-code">{{ JSON.stringify(buildAssertList(), null, 2) }}</pre>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeDialog" class="btn">取消</button>
            <button type="submit" class="btn btn-primary">确定</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCases, createCase, updateCase, deleteCase, getEndpoints } from '@/api/case'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const router = useRouter()
const cases = ref([])
const endpoints = ref([])
const projects = ref([])
const showCreateDialog = ref(false)
const editingItem = ref(null)
const pagination = ref({ page: 1, pageCount: 1, itemCount: 0 })
const activeTab = ref('basic')

const searchText = ref('')
const filterProject = ref('')
const filterEndpoint = ref('')

const tabs = [
  { key: 'basic',    label: '基本信息' },
  { key: 'params',   label: '接口参数' },
  { key: 'extract',  label: '数据提取' },
  { key: 'validate', label: '断言规则' },
]

const loadCases = async (page = 1) => {
  try {
    const params = { page, page_size: 10 }
    if (searchText.value)    params.search   = searchText.value
    if (filterProject.value) params.project  = filterProject.value
    if (filterEndpoint.value) params.endpoint = filterEndpoint.value
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getCases(params)
    cases.value = res.result?.list || []
    pagination.value = { page: res.result?.page || 1, pageCount: res.result?.pageCount || 1, itemCount: res.result?.itemCount || 0 }
  } catch (error) { console.error('加载用例列表失败:', error) }
}

const handleSearch = () => loadCases(1)
const resetFilter = () => { searchText.value = ''; filterProject.value = ''; filterEndpoint.value = ''; loadCases(1) }

const changePage = (page) => { selectedIds.value = []; loadCases(page) }

const selectedIds = ref([])
const allSelected = computed(() => cases.value.length > 0 && cases.value.every(i => selectedIds.value.includes(i.id)))
const toggleAll = (e) => { selectedIds.value = e.target.checked ? cases.value.map(i => i.id) : [] }
const batchDelete = async () => {
  if (!selectedIds.value.length) return
  const confirmed = await confirm(`确定要删除选中的 ${selectedIds.value.length} 条数据吗？`, { type: 'danger' })
  if (!confirmed) return
  try {
    await Promise.all(selectedIds.value.map(id => deleteCase(id)))
    cases.value = cases.value.filter(i => !selectedIds.value.includes(i.id))
    selectedIds.value = []
  } catch (error) { console.error('批量删除失败:', error) }
}

const formData = ref({
  name: '', endpoint: null, project: null,
  alluer: '', api_args: '', validate: '',
  paramType: 'json',
  jsonRows:  [],
  formRows:  [],
  queryRows: []
})

// 把 kv 行数组转成 {k:v} 对象，过滤空行
const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}

// 把 {k:v} 对象还原成行数组
const objToRows = (obj) =>
  obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []

// 根据 paramType 和 kv 行构建 api_args
const buildApiArgs = () => {
  if (formData.value.paramType === 'raw') {
    return formData.value.api_args ? JSON.parse(formData.value.api_args) : null
  }
  const obj = {}
  if (formData.value.paramType === 'json') {
    const d = rowsToObj(formData.value.jsonRows)
    if (d) obj.json = d
  } else if (formData.value.paramType === 'form') {
    const d = rowsToObj(formData.value.formRows)
    if (d) obj.data = d
  } else if (formData.value.paramType === 'query') {
    const d = rowsToObj(formData.value.queryRows)
    if (d) obj.params = d
  }
  return Object.keys(obj).length ? obj : null
}

// 从已有 api_args 反推 paramType 和行数据
const parseApiArgs = (api_args) => {
  if (!api_args) return { paramType: 'json', jsonRows: [], formRows: [], queryRows: [], api_args: '' }
  if (api_args.json)   return { paramType: 'json',  jsonRows: objToRows(api_args.json),   formRows: [], queryRows: [], api_args: '' }
  if (api_args.data)   return { paramType: 'form',  formRows: objToRows(api_args.data),   jsonRows: [], queryRows: [], api_args: '' }
  if (api_args.params) return { paramType: 'query', queryRows: objToRows(api_args.params), jsonRows: [], formRows: [], api_args: '' }
  // 其他情况用原始模式
  return { paramType: 'raw', api_args: JSON.stringify(api_args, null, 2), jsonRows: [], formRows: [], queryRows: [] }
}

const editExtractRules = ref([])
const addExtractRule = () => editExtractRules.value.push({ name: '', expr: '', index: 0 })
const removeExtractRule = (idx) => editExtractRules.value.splice(idx, 1)
const buildExtractObj = () => {
  const obj = {}
  for (const r of editExtractRules.value)
    if (r.name.trim()) obj[r.name.trim()] = ['json', r.expr.trim(), r.index ?? 0]
  return Object.keys(obj).length ? obj : null
}

// ---- 断言规则 ----
const editAssertRules = ref([])

const addAssertRule = (source = 'jsonpath') => {
  editAssertRules.value.push({
    name:   '',
    type:   'eq',
    source,
    expr:   '',
    expect: source === 'status_code' ? '200' : '',
  })
}

const buildAssertList = () =>
  editAssertRules.value
    .filter(r => r.name.trim())
    .map(r => {
      const rule = { name: r.name.trim(), type: r.type, source: r.source }
      if (r.source !== 'status_code') rule.expr = r.expr.trim()
      if (r.type !== 'exists') rule.expect = r.expect
      return rule
    })

const parseAssertList = (validate) => {
  if (!validate) return []
  if (Array.isArray(validate)) {
    return validate.map(r => ({
      name:   r.name   || '',
      type:   r.type   || 'eq',
      source: r.source || 'jsonpath',
      expr:   r.expr   || '',
      expect: r.expect != null ? String(r.expect) : '',
    }))
  }
  const rows = []
  for (const [k, v] of Object.entries(validate)) {
    if (k === 'status_code') {
      rows.push({ name: '状态码', type: 'eq', source: 'status_code', expr: '', expect: String(v) })
      continue
    }
    if (typeof v === 'object' && v !== null) {
      for (const [desc, item] of Object.entries(v)) {
        const expected = Array.isArray(item) ? item[0] : ''
        const target   = Array.isArray(item) ? item[1] : null
        const expr     = Array.isArray(target) && target[1] ? target[1] : ''
        rows.push({ name: desc, type: k === 'equals' ? 'eq' : k, source: 'jsonpath', expr, expect: String(expected) })
      }
    }
  }
  return rows
}

const loadEndpoints = async () => {
  try {
    const params = { page_size: 100 }
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getEndpoints(params)
    endpoints.value = res.result?.list || []
  } catch (error) { console.error('加载接口列表失败:', error) }
}
const loadProjects = async () => {
  try {
    const params = { page_size: 100 }
    if (userStore.currentProductLine) params.product_line = userStore.currentProductLine.id
    const res = await getProjects(params)
    projects.value = res.result?.list || []
  } catch (error) { console.error('加载项目列表失败:', error) }
}

const viewDetail = (id) => router.push(`/cases/${id}`)

const editCase = (item) => {
  editingItem.value = item
  activeTab.value = 'basic'
  const parsed = parseApiArgs(item.api_args)
  formData.value = {
    name:      item.name,
    endpoint:  item.endpoint?.id || item.endpoint,
    project:   item.project,
    alluer:    item.alluer   ? JSON.stringify(item.alluer,   null, 2) : '',
    validate:  item.validate ? JSON.stringify(item.validate, null, 2) : '',
    ...parsed
  }
  editExtractRules.value = item.extract
    ? Object.entries(item.extract).map(([name, rule]) =>
        Array.isArray(rule) ? { name, expr: rule[1]??'', index: rule[2]??0 } : { name, expr: String(rule), index: 0 }
      )
    : []
  editAssertRules.value = parseAssertList(item.validate)
  showCreateDialog.value = true
}

const handleSubmit = async () => {
  try {
    let api_args = buildApiArgs()
    const data = {
      name:     formData.value.name,
      endpoint: formData.value.endpoint,
      project:  formData.value.project,
      alluer:   formData.value.alluer   ? JSON.parse(formData.value.alluer)   : null,
      api_args,
      extract:  buildExtractObj(),
      validate: buildAssertList().length ? buildAssertList() : null
    }
    if (editingItem.value) {
      await updateCase(editingItem.value.id, data)
    } else {
      await createCase(data)
    }
    closeDialog()
    loadCases()
  } catch (error) {
    console.error('操作失败:', error)
    alert('保存失败，请检查JSON格式是否正确')
  }
}

const deleteCaseItem = async (id) => {
  const confirmed = await confirm('确定要删除这个用例吗？', { type: 'danger' })
  if (confirmed) {
    try { await deleteCase(id); cases.value = cases.value.filter(c => c.id !== id) }
    catch (error) { console.error('删除失败:', error) }
  }
}

const closeDialog = () => {
  showCreateDialog.value = false
  editingItem.value = null
  activeTab.value = 'basic'
  editExtractRules.value = []
  editAssertRules.value = []
  formData.value = {
    name: '', endpoint: null, project: null,
    alluer: '', api_args: '',
    paramType: 'json', jsonRows: [], formRows: [], queryRows: []
  }
}

const formatDate = (date) => date ? new Date(date).toLocaleString('zh-CN') : '-'

onMounted(() => { loadCases(); loadEndpoints(); loadProjects() })
</script>

<style scoped>
.toolbar { margin-bottom: 16px; }
.filter-bar { display:flex; align-items:center; gap:8px; padding:10px 14px; margin-bottom:16px; flex-wrap:nowrap; }
.filter-input-wrap { display:flex; align-items:center; gap:5px; border:1px solid var(--border); border-radius:6px; padding:0 8px; background:white; width:200px; flex-shrink:0; }
.filter-icon { color:var(--text-light); font-size:13px; }
.filter-input { border:none; outline:none; padding:7px 0; font-size:13px; width:100%; background:transparent; }
.filter-select { border:1px solid var(--border); border-radius:6px; padding:7px 8px; font-size:13px; background:white; color:var(--text); outline:none; cursor:pointer; width:120px; flex-shrink:0; }
.filter-select:focus { border-color:var(--accent); }
.btn-sm { padding:7px 14px; font-size:13px; white-space:nowrap; }
.table-container { overflow-x: auto; }
.btn-action { padding: 6px 12px; margin: 0 4px; border: none; background: var(--accent); color: white; border-radius: 4px; cursor: pointer; font-size: 13px; }
.btn-action:hover { opacity: 0.8; }
.btn-action.btn-danger { background: var(--danger); }
.btn-action.btn-info { background: #3498db; }
.creator-badge {
  display: inline-block; padding: 2px 10px; border-radius: 20px;
  background: linear-gradient(135deg, #e8f4fd, #d6eaf8);
  color: #1a6fa8; font-size: 12px; font-weight: 600;
  border: 1px solid #aed6f1; letter-spacing: 0.02em;
}
.link-text { color: var(--primary); cursor: pointer; text-decoration: none; font-weight: 500; }
.link-text:hover { text-decoration: underline; }
.empty-state { text-align: center; padding: 48px; color: var(--text-light); }

/* ===== Modal ===== */
.modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex;
  align-items: center; justify-content: center; z-index: 1000;
}
.modal-content {
  background: white; border-radius: 12px; width: 90%; max-width: 500px;
  animation: slideUp 0.3s ease; overflow: hidden;
}
.modal-tab { max-width: 680px; }
.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 0; margin-bottom: 0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; margin: 0; }
.btn-close { border: none; background: none; font-size: 18px; color: var(--text-light); cursor: pointer; padding: 4px 8px; border-radius: 4px; }
.btn-close:hover { background: #f5f5f5; }

/* ===== Tab ===== */
.tab-nav {
  display: flex; border-bottom: 2px solid var(--border);
  padding: 0 16px; gap: 2px; margin-top: 16px; background: #fafafa;
}
.tab-btn {
  padding: 11px 18px; border: none; background: none;
  font-size: 13px; font-weight: 500; color: var(--text-light);
  cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px;
  transition: color .2s, border-color .2s;
}
.tab-btn:hover { color: var(--primary); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab-content { padding: 20px 24px 8px; max-height: 60vh; overflow-y: auto; }

/* ===== Form ===== */
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text); font-size: 13px; }
.form-group input, .form-group select, .form-group textarea { width: 100%; box-sizing: border-box; }
.field-hint { font-size: 11px; font-weight: 400; color: var(--text-light); margin-left: 6px; }
.field-hint code { background: #fff3e0; color: #e65100; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
.modal-actions { display: flex; gap: 12px; justify-content: flex-end; padding: 12px 24px 20px; border-top: 1px solid var(--border); }

/* ===== 数据提取编辑器 ===== */
.extract-tip { background: #f0f8ff; border-left: 3px solid #3498db; padding: 9px 12px; border-radius: 4px; font-size: 12px; color: var(--text-light); margin-bottom: 14px; }
.extract-tip code { background: #fff3e0; color: #e65100; padding: 1px 4px; border-radius: 3px; font-size: 11px; }
.extract-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.extract-count { font-size: 13px; color: var(--text-light); }
.btn-add-rule { font-size: 12px; padding: 5px 14px; border: 1px solid #3498db; color: #3498db; background: white; border-radius: 5px; cursor: pointer; }
.btn-add-rule:hover { background: #e3f2fd; }
.extract-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; }
.extract-editor-header { display: grid; grid-template-columns: 140px 1fr 70px 32px; background: #e3f2fd; font-size: 11px; font-weight: 600; color: #1565c0; padding: 6px 10px; gap: 6px; }
.extract-editor-row { display: grid; grid-template-columns: 140px 1fr 70px 32px; gap: 6px; padding: 7px 10px; border-top: 1px solid #e8f4fd; align-items: center; background: white; }
.extract-editor-row:hover { background: #f8fcff; }
.rule-input { border: 1px solid #d0e8f8; border-radius: 4px; padding: 4px 7px; font-size: 12px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; }
.rule-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.12); }
.rule-index { text-align: center; font-family: inherit; }
.col-index { text-align: center; }
.empty-hint { color: var(--text-light); font-size: 13px; }
.btn-remove-rule { border: none; background: none; color: #e74c3c; cursor: pointer; font-size: 14px; padding: 2px 3px; border-radius: 3px; }
.btn-remove-rule:hover { background: #fdecea; }

/* ===== 接口参数类型切换 ===== */
.param-type-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px;
}
.param-type-tabs { display: flex; gap: 4px; }
.param-type-btn {
  padding: 4px 12px; font-size: 12px; border: 1px solid #d0e8f8;
  background: white; color: var(--text-light); border-radius: 4px; cursor: pointer;
}
.param-type-btn:hover { background: #f0f8ff; color: var(--primary); }
.param-type-btn.active {
  background: var(--primary); color: white; border-color: var(--primary);
}
.param-hint {
  font-size: 12px; color: var(--text-light); margin-bottom: 8px;
}
.param-hint code {
  background: #f0f4ff; color: #3a56c9;
  padding: 1px 5px; border-radius: 3px; font-size: 11px;
}

/* ===== KV 编辑器 ===== */
.kv-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; margin-bottom: 8px; }
.kv-header {
  display: grid; grid-template-columns: 1fr 1fr 32px;
  background: #e3f2fd; font-size: 11px; font-weight: 600;
  color: #1565c0; padding: 6px 10px; gap: 6px;
}
.kv-row {
  display: grid; grid-template-columns: 1fr 1fr 32px;
  gap: 6px; padding: 6px 10px; border-top: 1px solid #e8f4fd;
  align-items: center; background: white;
}
.kv-row:hover { background: #f8fcff; }
.kv-input {
  border: 1px solid #d0e8f8; border-radius: 4px;
  padding: 4px 7px; font-size: 12px;
  font-family: 'Monaco','Courier New',monospace;
  outline: none; width: 100%; box-sizing: border-box;
}
.kv-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.12); }

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.assert-tip { background: #f0faf4; border-left: 3px solid #27ae60; padding: 10px 14px; border-radius: 4px; font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.assert-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.assert-count { font-size: 13px; color: var(--text-light); }
.assert-add-btns { display: flex; gap: 8px; }
.btn-add-assert { background: none; border: 1px dashed #27ae60; color: #27ae60; border-radius: 5px; padding: 4px 12px; font-size: 12px; cursor: pointer; }
.btn-add-assert:hover { background: #f0faf4; }
.assert-editor { border: 1px solid #d5e8d4; border-radius: 8px; overflow: hidden; margin-bottom: 16px; }
.assert-rule-row { display: grid; grid-template-columns: 28px 160px 130px 110px 1fr 140px 32px; gap: 8px; padding: 8px 12px; border-top: 1px solid #e8f4e8; align-items: center; background: white; }
.assert-rule-row:first-child { border-top: none; }
.assert-rule-row:hover { background: #f6fdf6; }
.assert-idx { text-align: center; font-size: 12px; color: #aaa; font-weight: 600; }
.assert-input { border: 1px solid #d5e8d4; border-radius: 4px; padding: 5px 8px; font-size: 12px; outline: none; width: 100%; box-sizing: border-box; }
.assert-input:focus { border-color: #27ae60; box-shadow: 0 0 0 2px rgba(39,174,96,.12); }
.assert-select { border: 1px solid #d5e8d4; border-radius: 4px; padding: 5px 6px; font-size: 12px; outline: none; width: 100%; box-sizing: border-box; background: white; }
.assert-select:focus { border-color: #27ae60; }
.assert-name { font-family: inherit; }
.assert-expr { font-family: 'Monaco','Courier New',monospace; color: #2e7d32; }
.assert-expect { font-family: 'Monaco','Courier New',monospace; color: #1565c0; }
.assert-expr-placeholder { font-size: 12px; color: #aaa; font-style: italic; padding: 0 4px; }
.assert-exists-hint { font-size: 11px; }
.assert-preview { margin-top: 4px; }
.assert-preview-label { font-size: 11px; font-weight: 600; color: #aaa; text-transform: uppercase; letter-spacing: .05em; display: block; margin-bottom: 6px; }
.assert-preview-code { background: #1a1a2e; color: #a8ff78; padding: 14px 16px; border-radius: 8px; font-family: 'Monaco','Courier New',monospace; font-size: 12px; line-height: 1.6; overflow-x: auto; margin: 0; }
</style>
