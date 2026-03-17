<template>
  <div class="env-view">

    <!-- Tab 导航 -->
    <div class="tab-nav">
      <button
        v-for="t in tabs" :key="t.key"
        class="tab-btn"
        :class="{ active: activeTab === t.key }"
        @click="activeTab = t.key"
      >
        <span class="tab-icon">{{ t.icon }}</span>
        {{ t.label }}
        <span v-if="t.badge" class="tab-badge">{{ t.badge }}</span>
      </button>
    </div>

    <!-- Tab: 运行环境 -->
    <div v-show="activeTab === 'env'">
      <div class="tab-toolbar">
        <span class="tab-hint">管理各运行环境的服务 URL、变量和请求头配置</span>
        <button @click="openCreate" class="btn btn-primary">+ 新建环境</button>
      </div>
      <div class="two-col">
      <!-- 左：环境列表 -->
      <div class="env-list card">
        <div v-if="!envs.length" class="empty-state">暂无环境，点击「新建环境」</div>
        <div
          v-for="env in envs" :key="env.id"
          class="env-item"
          :class="{ active: selectedEnv?.id === env.id }"
          @click="selectEnv(env)"
        >
          <div class="env-item-left">
            <div class="env-item-icon">🌐</div>
            <div>
              <div class="env-item-name">{{ env.name }}</div>
              <div class="env-item-meta">
                {{ env.urls?.length ? env.urls.length + ' 个服务' : (env.base_url || '未配置 URL') }}
                · {{ env.variables ? Object.keys(env.variables).length : 0 }} 个变量
              </div>
            </div>
          </div>
          <button class="env-del-btn" @click.stop="deleteEnv(env)" title="删除">✕</button>
        </div>
      </div>

      <!-- 右：新建 -->
      <div v-if="creating" class="env-detail card">
        <div class="detail-title-row">
          <h3>新建环境</h3>
          <div class="detail-actions">
            <button @click="saveEnv" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
            <button @click="cancelEdit" class="btn btn-refresh">取消</button>
          </div>
        </div>
        <div class="form-group">
          <label>环境名称 <span class="required">*</span></label>
          <input v-model="form.name" placeholder="如：测试环境、预发布环境" />
        </div>
        <div class="form-group">
          <label>所属项目 <span class="required">*</span></label>
          <select v-model="form.project">
            <option :value="null">请选择项目</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </div>
        <div class="form-group">
          <label>备注</label>
          <input v-model="form.description" placeholder="可选备注描述" />
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>服务 URL<span class="label-hint">微服务可配置多个</span></label>
            <button type="button" class="btn-add-row" @click="form.urlRows.push({name:'',url:'',var:''})">+ 添加服务</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header url-header"><span>服务（从注册表选择）</span><span>该环境的实际 URL</span><span></span></div>
            <div v-for="(row, idx) in form.urlRows" :key="idx" class="kv-row url-row">
              <select v-model="row.var" class="kv-input">
                <option value="">请选择服务</option>
                <option v-for="svc in services" :key="svc.key" :value="svc.key">{{ svc.name }} ({{ svc.key }})</option>
              </select>
              <input v-model="row.url" placeholder="https://user.example.com" class="kv-input kv-input-wide" />
              <button type="button" class="btn-del-row" @click="form.urlRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.urlRows.length" class="kv-empty">暂未配置服务 URL</div>
          </div>
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>环境变量<span class="label-hint">用例参数中可用 ${变量名} 引用</span></label>
            <button type="button" class="btn-add-row" @click="form.varRows.push({k:'',v:''})">+ 添加变量</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header"><span>变量名</span><span>变量值</span><span></span></div>
            <div v-for="(row, idx) in form.varRows" :key="idx" class="kv-row">
              <input v-model="row.k" placeholder="变量名" class="kv-input" />
              <input v-model="row.v" placeholder="变量值" class="kv-input" />
              <button type="button" class="btn-del-row" @click="form.varRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.varRows.length" class="kv-empty">暂未配置环境变量</div>
          </div>
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>全局请求头<span class="label-hint">注入到所有请求</span></label>
            <button type="button" class="btn-add-row" @click="form.headerRows.push({k:'',v:''})">+ 添加请求头</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header"><span>Header 名</span><span>Header 值</span><span></span></div>
            <div v-for="(row, idx) in form.headerRows" :key="idx" class="kv-row">
              <input v-model="row.k" placeholder="Authorization" class="kv-input" />
              <input v-model="row.v" placeholder="Bearer xxx" class="kv-input" />
              <button type="button" class="btn-del-row" @click="form.headerRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.headerRows.length" class="kv-empty">暂未配置请求头</div>
          </div>
        </div>
      </div>

      <!-- 右：详情查看 -->
      <div v-else-if="selectedEnv && !editing" class="env-detail card">
        <div class="detail-title-row">
          <h3>{{ selectedEnv.name }}</h3>
          <div class="detail-actions">
            <button @click="startEdit" class="btn btn-primary">编辑</button>
            <button @click="deleteEnv(selectedEnv)" class="btn btn-danger">删除</button>
          </div>
        </div>
        <div class="view-block">
          <div class="view-block-title">基本信息</div>
          <div class="kv-editor">
            <div class="kv-header kv-header-2col"><span>字段</span><span>内容</span></div>
            <div class="kv-row kv-row-2col">
              <span class="kv-field-label">环境名称</span>
              <span class="kv-field-value">{{ selectedEnv.name }}</span>
            </div>
            <div class="kv-row kv-row-2col">
              <span class="kv-field-label">备注</span>
              <span class="kv-field-value">{{ selectedEnv.description || '-' }}</span>
            </div>
          </div>
        </div>
        <div class="view-block">
          <div class="view-block-title">服务 URL <span class="view-block-badge">{{ selectedEnv.urls?.length || 0 }}</span></div>
          <div v-if="selectedEnv.urls?.length" class="kv-editor">
            <div class="kv-header kv-header-2col"><span>服务标识</span><span>实际 URL</span></div>
            <div v-for="(u, i) in selectedEnv.urls" :key="i" class="kv-row kv-row-2col">
              <code class="tag-code">{{ u.var }}</code>
              <span class="view-url">{{ u.url }}</span>
            </div>
          </div>
          <div v-else class="kv-empty">未配置服务 URL</div>
        </div>
        <div class="view-block">
          <div class="view-block-title">环境变量 <span class="view-block-badge">{{ selectedEnv.variables ? Object.keys(selectedEnv.variables).length : 0 }}</span></div>
          <div v-if="selectedEnv.variables && Object.keys(selectedEnv.variables).length" class="kv-editor">
            <div class="kv-header kv-header-2col"><span>变量名</span><span>变量值</span></div>
            <div v-for="(val, key) in selectedEnv.variables" :key="key" class="kv-row kv-row-2col">
              <code class="tag-code">{{ key }}</code>
              <span>{{ val }}</span>
            </div>
          </div>
          <div v-else class="kv-empty">未配置环境变量</div>
        </div>
        <div class="view-block">
          <div class="view-block-title">全局请求头 <span class="view-block-badge">{{ selectedEnv.headers ? Object.keys(selectedEnv.headers).length : 0 }}</span></div>
          <div v-if="selectedEnv.headers && Object.keys(selectedEnv.headers).length" class="kv-editor">
            <div class="kv-header kv-header-2col"><span>Header 名</span><span>Header 值</span></div>
            <div v-for="(val, key) in selectedEnv.headers" :key="key" class="kv-row kv-row-2col">
              <code class="tag-code">{{ key }}</code>
              <span>{{ val }}</span>
            </div>
          </div>
          <div v-else class="kv-empty">未配置请求头</div>
        </div>
      </div>

      <!-- 右：编辑模式 -->
      <div v-else-if="selectedEnv && editing" class="env-detail card">
        <div class="detail-title-row">
          <h3>编辑环境</h3>
          <div class="detail-actions">
            <button @click="saveEnv" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
            <button @click="cancelEdit" class="btn btn-refresh">取消</button>
          </div>
        </div>
        <div class="form-group">
          <label>环境名称 <span class="required">*</span></label>
          <input v-model="form.name" placeholder="如：测试环境、预发布环境" />
        </div>
        <div class="form-group">
          <label>备注</label>
          <input v-model="form.description" placeholder="可选备注描述" />
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>服务 URL<span class="label-hint">微服务可配置多个</span></label>
            <button type="button" class="btn-add-row" @click="form.urlRows.push({name:'',url:'',var:''})">+ 添加服务</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header url-header"><span>服务（从注册表选择）</span><span>该环境的实际 URL</span><span></span></div>
            <div v-for="(row, idx) in form.urlRows" :key="idx" class="kv-row url-row">
              <select v-model="row.var" class="kv-input">
                <option value="">请选择服务</option>
                <option v-for="svc in services" :key="svc.key" :value="svc.key">{{ svc.name }} ({{ svc.key }})</option>
              </select>
              <input v-model="row.url" placeholder="https://user.example.com" class="kv-input kv-input-wide" />
              <button type="button" class="btn-del-row" @click="form.urlRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.urlRows.length" class="kv-empty">暂未配置服务 URL</div>
          </div>
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>环境变量<span class="label-hint">用例参数中可用 ${变量名} 引用</span></label>
            <button type="button" class="btn-add-row" @click="form.varRows.push({k:'',v:''})">+ 添加变量</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header"><span>变量名</span><span>变量值</span><span></span></div>
            <div v-for="(row, idx) in form.varRows" :key="idx" class="kv-row">
              <input v-model="row.k" placeholder="变量名" class="kv-input" />
              <input v-model="row.v" placeholder="变量值" class="kv-input" />
              <button type="button" class="btn-del-row" @click="form.varRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.varRows.length" class="kv-empty">暂未配置环境变量</div>
          </div>
        </div>
        <div class="form-group">
          <div class="label-row">
            <label>全局请求头<span class="label-hint">注入到所有请求</span></label>
            <button type="button" class="btn-add-row" @click="form.headerRows.push({k:'',v:''})">+ 添加请求头</button>
          </div>
          <div class="kv-editor">
            <div class="kv-header"><span>Header 名</span><span>Header 值</span><span></span></div>
            <div v-for="(row, idx) in form.headerRows" :key="idx" class="kv-row">
              <input v-model="row.k" placeholder="Authorization" class="kv-input" />
              <input v-model="row.v" placeholder="Bearer xxx" class="kv-input" />
              <button type="button" class="btn-del-row" @click="form.headerRows.splice(idx,1)">✕</button>
            </div>
            <div v-if="!form.headerRows.length" class="kv-empty">暂未配置请求头</div>
          </div>
        </div>
      </div>

      <!-- 右：占位 -->
      <div v-else class="env-placeholder">
        <div class="placeholder-inner">
          <div class="placeholder-icon">🌐</div>
          <p>选择左侧环境查看详情</p>
          <button @click="openCreate" class="btn btn-primary">+ 新建环境</button>
        </div>
      </div>
      </div>
    </div>
    <!-- /Tab: 运行环境 -->

    <!-- Tab: 全局变量 -->
    <div v-show="activeTab === 'vars'">
      <div class="tab-toolbar">
        <span class="tab-hint">套件执行时选择对应环境后自动注入，优先级低于套件变量</span>
        <div class="toolbar-right">
          <select v-model="gvEnv" class="filter-select">
            <option value="">全部环境</option>
            <option v-for="e in envs" :key="e.id" :value="e.id">{{ e.name }}</option>
          </select>
          <button @click="addGvRow" class="btn btn-primary">+ 新建变量</button>
        </div>
      </div>
      <div class="card table-card">
        <table class="table">
          <thead><tr><th>所属环境</th><th>变量名</th><th>变量值</th><th>备注</th><th style="width:120px">操作</th></tr></thead>
          <tbody>
            <tr v-for="(gv, idx) in filteredGvs" :key="gv.id || 'new-'+idx">
              <td>
                <select v-if="gv._edit" v-model="gv.environment" class="gv-input">
                  <option v-for="e in envs" :key="e.id" :value="e.id">{{ e.name }}</option>
                </select>
                <span v-else>{{ gv.environment_name }}</span>
              </td>
              <td>
                <input v-if="gv._edit" v-model="gv.key" class="gv-input" placeholder="变量名" />
                <code v-else class="var-code">{{ gv.key }}</code>
              </td>
              <td>
                <input v-if="gv._edit" v-model="gv.value" class="gv-input" placeholder="变量值" />
                <span v-else>{{ gv.value }}</span>
              </td>
              <td>
                <input v-if="gv._edit" v-model="gv.description" class="gv-input" placeholder="备注" />
                <span v-else class="cell-muted">{{ gv.description || '-' }}</span>
              </td>
              <td>
                <template v-if="gv._edit">
                  <button class="btn-action btn-success" @click="saveGv(gv, idx)">保存</button>
                  <button class="btn-action btn-gray" @click="cancelGv(gv, idx)">取消</button>
                </template>
                <template v-else>
                  <button class="btn-action btn-info" @click="gv._edit = true">编辑</button>
                  <button class="btn-action btn-danger" @click="deleteGv(gv, idx)">删除</button>
                </template>
              </td>
            </tr>
            <tr v-if="!filteredGvs.length"><td colspan="5" class="empty-state">暂无全局变量</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Tab: 服务注册表 -->
    <div v-show="activeTab === 'services'">
      <div class="tab-toolbar">
        <span class="tab-hint">统一管理服务标识（service_key）。环境配置服务 URL 时从此列表选择，确保各环境标识绝对一致。</span>
        <button @click="addSvcRow" class="btn btn-primary">+ 新建服务</button>
      </div>
      <div class="card table-card">
        <table class="table">
          <thead><tr><th>服务名称</th><th>服务标识 (key)</th><th>所属项目</th><th>备注</th><th style="width:120px">操作</th></tr></thead>
          <tbody>
            <tr v-for="(svc, idx) in services" :key="svc.id || 'new-'+idx">
              <td>
                <input v-if="svc._edit" v-model="svc.name" class="gv-input" placeholder="用户服务" />
                <span v-else>{{ svc.name }}</span>
              </td>
              <td>
                <input v-if="svc._edit" v-model="svc.key" class="gv-input" placeholder="user-site" />
                <code v-else class="var-code">{{ svc.key }}</code>
              </td>
              <td>
                <select v-if="svc._edit" v-model="svc.project" class="gv-input">
                  <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
                <span v-else>{{ svc.project_name || '-' }}</span>
              </td>
              <td>
                <input v-if="svc._edit" v-model="svc.description" class="gv-input" placeholder="备注" />
                <span v-else class="cell-muted">{{ svc.description || '-' }}</span>
              </td>
              <td>
                <template v-if="svc._edit">
                  <button class="btn-action btn-success" @click="saveSvc(svc, idx)">保存</button>
                  <button class="btn-action btn-gray" @click="cancelSvc(svc, idx)">取消</button>
                </template>
                <template v-else>
                  <button class="btn-action btn-info" @click="svc._edit = true">编辑</button>
                  <button class="btn-action btn-danger" @click="deleteSvc(svc, idx)">删除</button>
                </template>
              </td>
            </tr>
            <tr v-if="!services.length"><td colspan="5" class="empty-state">暂无服务，点击「新建服务」添加</td></tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getProjects } from '@/api/project'
import {
  getEnvironments, createEnvironment, updateEnvironment, deleteEnvironment,
  getGlobalVariables, createGlobalVariable, updateGlobalVariable, deleteGlobalVariable,
  getServices, createService, updateService, deleteService,
} from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

const activeTab = ref('env')
const tabs = computed(() => [
  { key: 'env',      icon: '🌐', label: '运行环境',   badge: envs.value.length || null },
  { key: 'vars',     icon: '🔑', label: '全局变量',   badge: globalVars.value.length || null },
  { key: 'services', icon: '🔧', label: '服务注册表', badge: services.value.length || null },
])

const projects    = ref([])
const envs        = ref([])
const globalVars  = ref([])
const services    = ref([])  // 服务注册表
const gvEnv       = ref('')
const selectedEnv = ref(null)
const creating    = ref(false)
const editing     = ref(false)
const saving      = ref(false)

const blankForm = () => ({ name: '', description: '', project: null, urlRows: [], varRows: [], headerRows: [] })
const form = ref(blankForm())

const filteredGvs = computed(() =>
  gvEnv.value ? globalVars.value.filter(g => g.environment == gvEnv.value) : globalVars.value
)

const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k?.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}
const objToRows = (obj) => obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []
const urlsToRows = (urls) => Array.isArray(urls) ? urls.map(u => ({ var: u.var || '', url: u.url || '' })) : []

const loadAll = async () => {
  const plId = userStore.currentProductLine?.id
  const params = { page_size: 200, ...(plId ? { product_line: plId } : {}) }
  const [er, gr, sr] = await Promise.all([
    getEnvironments(params),
    getGlobalVariables({ page_size: 200 }),
    getServices(params),
  ])
  envs.value       = er.result?.list || []
  globalVars.value = (gr.result?.list || []).map(g => ({ ...g, _edit: false }))
  services.value   = sr.result?.list || []
}

const selectEnv = (env) => {
  creating.value = false
  editing.value  = false
  selectedEnv.value = env
}

const startEdit = () => {
  const env = selectedEnv.value
  form.value = {
    name:        env.name,
    description: env.description || '',
    urlRows:     urlsToRows(env.urls),
    varRows:     objToRows(env.variables),
    headerRows:  objToRows(env.headers),
  }
  editing.value = true
}

const openCreate = () => {
  selectedEnv.value = null
  creating.value = true
  editing.value  = false
  form.value = blankForm()
}

const cancelEdit = () => {
  if (creating.value) {
    creating.value = false
  } else {
    editing.value = false
  }
}

const saveEnv = async () => {
  if (!form.value.name?.trim()) return alert('环境名称必填')
  saving.value = true
  try {
    const urls = form.value.urlRows
      .filter(r => r.url?.trim() && r.var?.trim())
      .map(r => ({ var: r.var.trim(), url: r.url.trim() }))
    const payload = {
      name:        form.value.name.trim(),
      description: form.value.description,
      urls:        urls.length ? urls : null,
      variables:   rowsToObj(form.value.varRows),
      headers:     rowsToObj(form.value.headerRows),
      project:     form.value.project || selectedEnv.value?.project || (projects.value[0]?.id ?? 1),
    }
    if (creating.value) {
      await createEnvironment(payload)
      creating.value = false
      selectedEnv.value = null
    } else {
      await updateEnvironment(selectedEnv.value.id, payload)
      editing.value = false
      // 刷新后重新选中当前环境
      const id = selectedEnv.value.id
      await loadAll()
      selectedEnv.value = envs.value.find(e => e.id === id) || null
      return
    }
    await loadAll()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

const deleteEnv = async (env) => {
  const ok = await confirm(`确定删除环境「${env.name}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteEnvironment(env.id)
  if (selectedEnv.value?.id === env.id) selectedEnv.value = null
  await loadAll()
}

const addGvRow = () => {
  const defaultEnv = gvEnv.value || selectedEnv.value?.id || (envs.value[0]?.id ?? '')
  globalVars.value.unshift({ id: null, environment: defaultEnv, environment_name: '', key: '', value: '', description: '', _edit: true })
}

const saveGv = async (gv) => {
  if (!gv.key?.trim()) return alert('变量名必填')
  if (!gv.environment) return alert('请选择所属环境')
  // 本地重复校验
  const isDup = globalVars.value.some(
    g => g.id !== gv.id && g.environment == gv.environment && g.key?.trim() === gv.key.trim()
  )
  if (isDup) return alert(`变量名「${gv.key.trim()}」在该环境中已存在，请使用不同的变量名`)
  try {
    const payload = { environment: gv.environment, key: gv.key.trim(), value: gv.value, description: gv.description || '' }
    if (gv.id) { await updateGlobalVariable(gv.id, payload) }
    else { await createGlobalVariable(payload) }
    await loadAll()
  } catch (e) {
    const msg = e.response?.data?.key?.[0] || e.response?.data?.non_field_errors?.[0] || e.response?.data?.message || e.message
    alert('保存失败: ' + msg)
  }
}

const cancelGv = (gv, idx) => {
  if (!gv.id) globalVars.value.splice(idx, 1)
  else gv._edit = false
}

const deleteGv = async (gv, idx) => {
  if (!gv.id) { globalVars.value.splice(idx, 1); return }
  const ok = await confirm(`确定删除全局变量「${gv.key}」吗？`, { type: 'danger' })
  if (!ok) return
  await deleteGlobalVariable(gv.id)
  await loadAll()
}

// ---- 服务管理 ----
const addSvcRow = () => {
  services.value.unshift({ _edit: true, name: '', key: '', description: '', project: projects.value[0]?.id || null, project_name: '' })
}

const saveSvc = async (svc, idx) => {
  if (!svc.name?.trim()) return alert('服务名称必填')
  if (!svc.key?.trim()) return alert('服务标识必填')
  if (!svc.project) return alert('所属项目必填')
  try {
    if (svc.id) {
      await updateService(svc.id, { name: svc.name, key: svc.key, description: svc.description, project: svc.project })
    } else {
      await createService({ name: svc.name, key: svc.key, description: svc.description, project: svc.project })
    }
    await loadAll()
  } catch (e) {
    alert('保存失败: ' + (e.response?.data?.key?.[0] || e.response?.data?.message || e.message))
  }
}

const cancelSvc = (svc, idx) => {
  if (!svc.id) { services.value.splice(idx, 1); return }
  svc._edit = false
}

const deleteSvc = async (svc, idx) => {
  if (!svc.id) { services.value.splice(idx, 1); return }
  const ok = await confirm(`确定删除服务「${svc.name}」吗？删除后各环境中引用该服务的 URL 配置将失效。`, { type: 'danger' })
  if (!ok) return
  await deleteService(svc.id)
  await loadAll()
}

onMounted(async () => {
  const [, pr] = await Promise.all([
    loadAll(),
    getProjects({ page_size: 200 }),
  ])
  projects.value = pr.result?.list || []
})
</script>

<style scoped>
.env-view { display: flex; flex-direction: column; gap: 20px; }

/* Tab 导航 */
.tab-nav { display: flex; gap: 4px; border-bottom: 2px solid var(--border); padding-bottom: 0; }
.tab-btn { display: flex; align-items: center; gap: 8px; padding: 12px 24px; border: none; border-bottom: 2px solid transparent; margin-bottom: -2px; background: none; color: var(--text-light); font-size: 14px; font-weight: 500; cursor: pointer; border-radius: 8px 8px 0 0; transition: all .2s; }
.tab-btn:hover { color: var(--text); background: rgba(0,0,0,.04); }
.tab-btn.active { color: var(--accent); border-bottom-color: var(--accent); background: rgba(52,152,219,.06); font-weight: 600; }
.tab-icon { font-size: 16px; }
.tab-badge { background: var(--accent); color: white; border-radius: 10px; padding: 1px 7px; font-size: 11px; font-weight: 600; }

/* Tab 内容区 */
.tab-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; gap: 12px; }
.tab-hint { font-size: 13px; color: var(--text-light); line-height: 1.5; }
.toolbar-right { display: flex; gap: 10px; align-items: center; flex-shrink: 0; white-space: nowrap; }
.table-card { padding: 0; overflow: hidden; }

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 4px; }
.section-title { font-size: 20px; font-weight: 700; color: var(--primary); margin: 0; }
.two-col { display: grid; grid-template-columns: 280px 1fr; gap: 20px; align-items: start; }

.env-list { padding: 12px; min-height: 300px; }
.env-item { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-radius: 8px; cursor: pointer; transition: background .15s; margin-bottom: 4px; border: 1px solid transparent; }
.env-item:hover { background: #f0f7ff; border-color: var(--border); }
.env-item.active { background: #e3f2fd; border-color: var(--accent); }
.env-item-left { display: flex; align-items: center; gap: 10px; min-width: 0; }
.env-item-icon { font-size: 20px; flex-shrink: 0; }
.env-item-name { font-weight: 600; font-size: 14px; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 160px; }
.env-item-meta { font-size: 12px; color: var(--text-light); margin-top: 2px; }
.env-del-btn { background: none; border: none; color: #ccc; cursor: pointer; font-size: 14px; padding: 2px 6px; border-radius: 4px; transition: all .15s; }
.env-del-btn:hover { color: var(--danger); background: #fff0f0; }

.env-detail { padding: 24px; overflow-y: visible; }
.detail-title-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 16px; }
.detail-title-row h3 { font-size: 16px; font-weight: 700; color: var(--primary); margin: 0; }
.detail-actions { display: flex; gap: 10px; }

.env-placeholder { display: flex; align-items: center; justify-content: center; min-height: 300px; background: var(--card-bg); border-radius: 12px; box-shadow: 0 2px 8px var(--shadow); }
.placeholder-inner { text-align: center; color: var(--text-light); }
.placeholder-icon { font-size: 48px; margin-bottom: 12px; }
.placeholder-inner p { margin-bottom: 16px; font-size: 14px; }

.form-group { margin-bottom: 20px; }
.form-group label { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.required { color: var(--danger); }
.label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.label-row label { margin-bottom: 0; }
.label-hint { font-size: 12px; color: var(--text-light); font-weight: 400; margin-left: 6px; }
.btn-add-row { background: none; border: 1px dashed var(--accent); color: var(--accent); border-radius: 6px; padding: 3px 12px; font-size: 12px; cursor: pointer; white-space: nowrap; }
.btn-add-row:hover { background: #e3f2fd; }

.kv-editor { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.kv-header { display: grid; grid-template-columns: 1fr 1fr 28px; background: var(--primary); color: white; font-size: 12px; font-weight: 600; padding: 8px 12px; gap: 8px; }
.url-header { grid-template-columns: 1fr 2fr 1fr 28px; }
.kv-row { display: grid; grid-template-columns: 1fr 1fr 28px; gap: 8px; padding: 7px 12px; border-top: 1px solid var(--border); align-items: center; }
.url-row { grid-template-columns: 1fr 2fr 1fr 28px; }
.kv-input { border: 1px solid var(--border); border-radius: 5px; padding: 6px 8px; font-size: 13px; font-family: inherit; outline: none; width: 100%; box-sizing: border-box; transition: border-color .2s; }
.kv-input:focus { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(52,152,219,.1); }
.btn-del-row { background: none; border: none; color: #ccc; cursor: pointer; font-size: 13px; padding: 2px; border-radius: 4px; }
.btn-del-row:hover { color: var(--danger); }
.kv-empty { padding: 12px 14px; color: var(--text-light); font-size: 13px; background: #fafafa; font-style: italic; }

.gv-card { padding: 0; overflow: hidden; }
.gv-top { display: flex; align-items: center; justify-content: space-between; padding: 18px 24px; border-bottom: 1px solid var(--border); gap: 16px; flex-wrap: nowrap; }
.gv-title { font-size: 16px; font-weight: 700; color: var(--text); margin: 0 0 4px; }
.gv-hint { font-size: 12px; color: var(--text-light); }
.gv-top-right { display: flex; gap: 10px; align-items: center; flex-shrink: 0; white-space: nowrap; }
.filter-select { padding: 8px 12px; border: 1px solid var(--border); border-radius: 6px; font-size: 13px; background: white; color: var(--text); outline: none; }
.filter-select:focus { border-color: var(--accent); }
.var-code { background: #e8f4fd; color: #1565c0; padding: 2px 7px; border-radius: 4px; font-size: 12px; font-family: monospace; }
.cell-muted { color: var(--text-light); font-size: 13px; }
.gv-card .table th { font-size: 12px; padding: 10px 14px; }
.gv-card .table td { font-size: 13px; padding: 8px 14px; }
.gv-input { border: 1px solid var(--border); border-radius: 5px; padding: 6px 10px; font-size: 13px; width: 100%; box-sizing: border-box; outline: none; }
.gv-input:focus { border-color: var(--accent); }
.empty-state { text-align: center; padding: 32px; color: var(--text-light); font-size: 14px; }
.btn-action { padding: 5px 12px; margin: 0 2px; border: none; border-radius: 5px; cursor: pointer; font-size: 12px; font-weight: 500; color: white; transition: opacity .15s; }
.btn-action:hover { opacity: .82; }
.btn-action.btn-info    { background: var(--accent); }
.btn-action.btn-success { background: var(--success); }
.btn-action.btn-danger  { background: var(--danger); }
.btn-action.btn-gray    { background: white; border: 1px solid var(--border); color: var(--text); }

/* 详情查看模式 */
.view-block { margin-bottom: 20px; }
.view-block-title { font-size: 13px; font-weight: 700; color: var(--primary); margin-bottom: 8px; display: flex; align-items: center; gap: 8px; }
.view-block-badge { background: var(--accent); color: white; border-radius: 10px; padding: 1px 8px; font-size: 11px; font-weight: 600; }
.kv-header-2col { display: grid; grid-template-columns: 1fr 2fr; background: var(--primary); color: white; font-size: 12px; font-weight: 600; padding: 8px 12px; gap: 8px; }
.kv-row-2col { display: grid; grid-template-columns: 1fr 2fr; gap: 8px; padding: 8px 12px; border-top: 1px solid var(--border); align-items: center; }
.kv-field-label { font-size: 13px; color: var(--text-light); font-weight: 500; }
.kv-field-value { font-size: 13px; color: var(--text); }
.tag-code { background: #e8f4fd; color: #1565c0; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-family: monospace; white-space: nowrap; }
.view-url { font-family: 'Monaco','Courier New',monospace; font-size: 13px; color: var(--text); word-break: break-all; }
</style>
