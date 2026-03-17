<template>
  <div class="suite-detail">
    <div class="detail-header">
      <button @click="$router.push('/suites')" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button v-if="!editing" @click="startEdit" class="btn btn-primary">编辑套件</button>
        <button v-if="editing" @click="handleSubmit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
        <button v-if="editing" @click="cancelEdit" class="btn btn-refresh">取消</button>
        <button v-if="!editing" @click="runSuite" class="btn btn-success">▶ 运行套件</button>
        <button v-if="!editing" @click="deleteSuiteItem" class="btn btn-danger">删除套件</button>
      </div>
    </div>

    <div v-if="suite" class="detail-content">
      <!-- 顶部 Tab 导航 -->
      <div class="main-tabs">
        <button v-for="tab in mainTabs" :key="tab.id"
          class="main-tab" :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id">
          <span class="tab-icon">{{ tab.icon }}</span>{{ tab.label }}
        </button>
      </div>

      <!-- Tab: 基本信息 -->
      <div v-show="activeTab === 'info'">
        <div v-if="!editing" class="info-card card">
          <h2>{{ suite.name }}</h2>
          <div class="info-grid">
            <div class="info-item"><label>套件 ID</label><span>{{ suite.id }}</span></div>
            <div class="info-item"><label>所属项目</label><span>{{ suite.project_name || `项目 #${suite.project}` }}</span></div>
            <div class="info-item">
              <label>运行类型</label>
              <span class="type-badge" :class="'type-' + suite.run_type">{{ { O:'手动执行', C:'定时执行', W:'WebHook' }[suite.run_type] }}</span>
            </div>
            <div v-if="suite.cron" class="info-item"><label>Cron</label><code>{{ suite.cron }}</code></div>
            <div v-if="suite.hook_key" class="info-item"><label>Webhook 密钥</label><code>{{ suite.hook_key }}</code></div>
            <div v-if="suite.environment_name" class="info-item full-width"><label>运行环境</label><span class="env-badge">🌐 {{ suite.environment_name }}</span></div>
            <div v-if="suite.description" class="info-item full-width"><label>描述</label><span>{{ suite.description }}</span></div>
            <div class="info-item full-width execution-policy">
              <label>执行策略</label>
              <div class="policy-chips">
                <span class="policy-chip">⏱ 超时：{{ suite.timeout_seconds > 0 ? suite.timeout_seconds + ' 秒' : '不限制' }}</span>
                <span class="policy-chip" :class="suite.fail_strategy === 'stop' ? 'chip-danger' : 'chip-ok'">{{ suite.fail_strategy === 'stop' ? '⏹ 失败立即停止' : '▶ 失败继续执行' }}</span>
                <span class="policy-chip">🔁 重试：{{ suite.retry_count > 0 ? suite.retry_count + ' 次 / 间隔 ' + suite.retry_delay + 's' : '不重试' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 编辑模式 -->
        <div v-else class="info-card card">
          <h3 class="edit-title">编辑套件</h3>
          <form @submit.prevent="handleSubmit">
            <div class="form-group">
              <label>套件名称 <span class="required">*</span></label>
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
              <label>运行类型 <span class="required">*</span></label>
              <div class="run-type-options">
                <label v-for="t in runTypes" :key="t.value"
                  class="run-type-radio" :class="{ active: formData.run_type === t.value, ['rt-'+t.value.toLowerCase()]: true }">
                  <input type="radio" v-model="formData.run_type" :value="t.value" hidden />
                  <span class="rt-icon">{{ t.icon }}</span>{{ t.label }}
                </label>
              </div>
            </div>
            <div v-if="formData.run_type === 'C'" class="form-group">
              <label>Cron 表达式</label>
              <div class="cron-presets">
                <span v-for="p in cronPresets" :key="p.value" class="preset-tag" :class="{ active: formData.cron === p.value }" @click="formData.cron = p.value">{{ p.label }}</span>
              </div>
              <input v-model="formData.cron" placeholder="0 9 * * 1-5" />
              <span class="field-hint">格式：分 时 日 月 周</span>
            </div>
            <div v-if="formData.run_type === 'W'" class="form-group">
              <label>WebHook 密钥</label>
              <input v-model="formData.hook_key" placeholder="保存后自动生成" />
            </div>
            <div class="form-group">
              <label>运行环境</label>
              <select v-model="formData.environment">
                <option :value="null">不指定环境</option>
                <option v-for="e in environments" :key="e.id" :value="e.id">{{ e.name }}</option>
              </select>
              <span class="field-hint">执行时注入环境变量和 base_url</span>
            </div>
            <div class="form-group">
              <label>描述</label>
              <textarea v-model="formData.description" rows="2"></textarea>
            </div>
            <div class="left-section-title">执行策略</div>
            <div class="form-group">
              <label>用例超时时间<span class="label-hint">秒，0=不限制</span></label>
              <div class="input-addon">
                <input v-model.number="formData.timeout_seconds" type="number" min="0" placeholder="0" />
                <span class="addon-unit">秒</span>
              </div>
            </div>
            <div class="form-group">
              <label>失败策略</label>
              <div class="radio-group">
                <label class="radio-opt" :class="{ active: formData.fail_strategy === 'continue' }">
                  <input type="radio" v-model="formData.fail_strategy" value="continue" hidden /> ▶ 继续执行
                </label>
                <label class="radio-opt" :class="{ active: formData.fail_strategy === 'stop' }">
                  <input type="radio" v-model="formData.fail_strategy" value="stop" hidden /> ⏹ 立即停止
                </label>
              </div>
            </div>
            <div class="form-group">
              <label>失败重试</label>
              <div class="retry-row">
                <div class="input-addon">
                  <input v-model.number="formData.retry_count" type="number" min="0" max="10" placeholder="0" />
                  <span class="addon-unit">次</span>
                </div>
                <span class="retry-sep">间隔</span>
                <div class="input-addon">
                  <input v-model.number="formData.retry_delay" type="number" min="0" step="0.5" placeholder="1" />
                  <span class="addon-unit">秒</span>
                </div>
              </div>
            </div>
            <div class="edit-form-actions">
              <button type="submit" class="btn btn-primary" :disabled="saving">{{ saving ? '保存中...' : '保存' }}</button>
              <button type="button" class="btn btn-refresh" @click="cancelEdit">取消</button>
            </div>
          </form>
        </div>
      </div><!-- /Tab:基本信息 -->

      <!-- Tab: 执行用例 -->
      <div v-show="activeTab === 'cases'" class="card cases-card">
        <!-- 前置操作 -->
        <div class="phase-block phase-setup">
          <div class="phase-header">
            <span class="phase-icon">🔧</span>
            <span class="phase-title">前置操作</span>
            <span class="phase-badge">{{ setupItems.length }}</span>
            <span class="phase-hint">套件开始前执行，可用于创建数据、登录获取 Token 等</span>
            <button @click="openAddCaseDialog('API','setup')" class="btn btn-sm phase-add-btn">+ 添加</button>
          </div>
          <div v-if="setupItems.length" class="phase-table-wrap">
            <table class="table">
              <thead><tr><th style="width:60px">顺序</th><th>用例名称</th><th>类型</th><th>所属接口</th><th>操作</th></tr></thead>
              <tbody>
                <tr v-for="(item, idx) in setupItems" :key="item.id">
                  <td class="order-cell"><div class="order-btns">
                    <button @click="movePhaseUp('setup', idx)" :disabled="idx===0" class="order-btn">↑</button>
                    <span class="order-num">{{ idx+1 }}</span>
                    <button @click="movePhaseDown('setup', idx)" :disabled="idx===setupItems.length-1" class="order-btn">↓</button>
                  </div></td>
                  <td class="case-name">{{ item.case_name }}</td>
                  <td><span class="type-tag" :class="item.case_type==='API'?'tag-api':'tag-ui'">{{ item.case_type }}</span></td>
                  <td class="endpoint-name">{{ item.endpoint_name||'-' }}</td>
                  <td><button @click="removeCaseItem(item)" class="btn-action btn-danger">移除</button></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="phase-empty">暂无前置操作</div>
        </div>

        <!-- 正式用例 -->
        <div class="phase-block phase-main">
          <div class="phase-header">
            <span class="phase-icon">📋</span>
            <span class="phase-title">正式用例</span>
            <span class="phase-badge">{{ mainItems.length }}</span>
            <div class="phase-header-right">
              <button @click="openAddCaseDialog('API','main')" class="btn btn-primary btn-sm">+ 添加 API 用例</button>
              <button @click="openAddCaseDialog('UI','main')" class="btn btn-sm">+ 添加 UI 用例</button>
            </div>
          </div>
          <div v-if="mainItems.length" class="phase-table-wrap">
            <table class="table">
              <thead><tr><th style="width:60px">顺序</th><th>用例名称</th><th>类型</th><th>所属接口</th><th style="width:80px">启用</th><th>操作</th></tr></thead>
              <tbody>
                <tr v-for="(item, idx) in mainItems" :key="item.id" :class="{ 'row-disabled': !item.enabled }">
                  <td class="order-cell"><div class="order-btns">
                    <button @click="movePhaseUp('main', idx)" :disabled="idx===0" class="order-btn">↑</button>
                    <span class="order-num">{{ idx+1 }}</span>
                    <button @click="movePhaseDown('main', idx)" :disabled="idx===mainItems.length-1" class="order-btn">↓</button>
                  </div></td>
                  <td class="case-name">{{ item.case_name }}</td>
                  <td><span class="type-tag" :class="item.case_type==='API'?'tag-api':'tag-ui'">{{ item.case_type }}</span></td>
                  <td class="endpoint-name">{{ item.endpoint_name||'-' }}</td>
                  <td><label class="toggle"><input type="checkbox" v-model="item.enabled" @change="toggleEnabled(item)" /><span class="slider"></span></label></td>
                  <td><button @click="removeCaseItem(item)" class="btn-action btn-danger">移除</button></td>
                </tr>
              </tbody>
            </table>
            <div class="save-order-bar" v-if="orderChanged">
              <span>顺序已变更，记得保存</span>
              <button @click="saveOrder" class="btn btn-primary btn-sm">保存排序</button>
              <button @click="loadCaseItems" class="btn btn-sm">撤销</button>
            </div>
          </div>
          <div v-else class="phase-empty">暂无正式用例，点击右侧按钮添加</div>
        </div>

        <!-- 后置操作 -->
        <div class="phase-block phase-teardown">
          <div class="phase-header">
            <span class="phase-icon">🧹</span>
            <span class="phase-title">后置操作</span>
            <span class="phase-badge">{{ teardownItems.length }}</span>
            <span class="phase-hint">无论正式用例是否失败，后置操作都会执行</span>
            <button @click="openAddCaseDialog('API','teardown')" class="btn btn-sm phase-add-btn">+ 添加</button>
          </div>
          <div v-if="teardownItems.length" class="phase-table-wrap">
            <table class="table">
              <thead><tr><th style="width:60px">顺序</th><th>用例名称</th><th>类型</th><th>所属接口</th><th>操作</th></tr></thead>
              <tbody>
                <tr v-for="(item, idx) in teardownItems" :key="item.id">
                  <td class="order-cell"><div class="order-btns">
                    <button @click="movePhaseUp('teardown', idx)" :disabled="idx===0" class="order-btn">↑</button>
                    <span class="order-num">{{ idx+1 }}</span>
                    <button @click="movePhaseDown('teardown', idx)" :disabled="idx===teardownItems.length-1" class="order-btn">↓</button>
                  </div></td>
                  <td class="case-name">{{ item.case_name }}</td>
                  <td><span class="type-tag" :class="item.case_type==='API'?'tag-api':'tag-ui'">{{ item.case_type }}</span></td>
                  <td class="endpoint-name">{{ item.endpoint_name||'-' }}</td>
                  <td><button @click="removeCaseItem(item)" class="btn-action btn-danger">移除</button></td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else class="phase-empty">暂无后置操作</div>
        </div>
      </div><!-- /cases-card -->
      </div><!-- /Tab:执行用例 -->

      <!-- Tab: 套件变量 -->
      <div v-if="suite" v-show="activeTab === 'vars'" class="card vars-card-full">
        <div class="vars-full-header">
          <span class="vars-card-title">🔑 套件变量</span>
          <span class="vars-full-hint">优先级高于全局变量，可在用例参数中用 <code>${变量名}</code> 引用</span>
          <button class="btn btn-primary btn-sm" @click="addSuiteVar">+ 新增变量</button>
        </div>
        <table class="table">
          <thead><tr><th>变量名</th><th>变量值</th><th style="width:120px">操作</th></tr></thead>
          <tbody>
            <tr v-for="(row, idx) in suiteVarRows" :key="idx">
              <td>
                <input v-if="row._edit" v-model="row.k" class="gv-input" placeholder="变量名" />
                <code v-else class="var-code">{{ row.k }}</code>
              </td>
              <td>
                <input v-if="row._edit" v-model="row.v" class="gv-input" placeholder="变量值" />
                <span v-else>{{ row.v }}</span>
              </td>
              <td>
                <template v-if="row._edit">
                  <button class="btn-action btn-success" :disabled="saving" @click="saveSuiteVar(idx)">{{ saving ? '...' : '保存' }}</button>
                  <button class="btn-action btn-gray" @click="cancelSuiteVar(idx)">取消</button>
                </template>
                <template v-else>
                  <button class="btn-action btn-info" @click="row._edit = true">编辑</button>
                  <button class="btn-action btn-danger" @click="deleteSuiteVar(idx)">删除</button>
                </template>
              </td>
            </tr>
            <tr v-if="!suiteVarRows.length"><td colspan="3" class="empty-state">暂无套件变量，点击「+ 新增变量」添加</td></tr>
          </tbody>
        </table>
      </div><!-- /Tab:套件变量 -->

      <!-- Tab: 套件请求头 -->
      <div v-if="suite" v-show="activeTab === 'headers'" class="card vars-card-full">
        <div class="vars-full-header">
          <span class="vars-card-title">🌐 套件请求头</span>
          <span class="vars-full-hint">注入到本套件所有请求，优先级高于环境 Headers，支持 <code>${变量名}</code> 占位符</span>
          <button class="btn btn-primary btn-sm" @click="addSuiteHeader">+ 新增请求头</button>
        </div>
        <table class="table">
          <thead><tr><th>Header 名</th><th>Header 值</th><th style="width:120px">操作</th></tr></thead>
          <tbody>
            <tr v-for="(row, idx) in suiteHeaderRows" :key="idx">
              <td>
                <input v-if="row._edit" v-model="row.k" class="gv-input" placeholder="如：Authorization" />
                <code v-else class="var-code">{{ row.k }}</code>
              </td>
              <td>
                <input v-if="row._edit" v-model="row.v" class="gv-input" placeholder="如：Bearer ${token}" />
                <span v-else>{{ row.v }}</span>
              </td>
              <td>
                <template v-if="row._edit">
                  <button class="btn-action btn-success" :disabled="saving" @click="saveSuiteHeader(idx)">{{ saving ? '...' : '保存' }}</button>
                  <button class="btn-action btn-gray" @click="cancelSuiteHeader(idx)">取消</button>
                </template>
                <template v-else>
                  <button class="btn-action btn-info" @click="row._edit = true">编辑</button>
                  <button class="btn-action btn-danger" @click="deleteSuiteHeader(idx)">删除</button>
                </template>
              </td>
            </tr>
            <tr v-if="!suiteHeaderRows.length"><td colspan="3" class="empty-state">暂无套件请求头，点击「+ 新增请求头」添加</td></tr>
          </tbody>
        </table>
      </div><!-- /Tab:套件请求头 -->

    </div><!-- /detail-content -->

  <!-- 添加用例弹框 -->
  <div v-if="showAddCaseDialog" class="modal" @click.self="showAddCaseDialog=false">
    <div class="modal-content modal-large">
      <h3>添加 {{ addingCaseType }} 用例</h3>
      <div class="add-case-filters">
        <select v-model="addingProductLine" class="filter-select-sm">
          <option :value="null">全部产品线</option>
          <option v-for="pl in addingProductLines" :key="pl.id" :value="pl.id">{{ pl.name }}</option>
        </select>
        <input v-model="caseSearch" placeholder="搜索用例名称..." class="search-input-sm" />
      </div>
      <div class="available-cases">
        <div v-for="c in filteredAvailableCases" :key="c.id"
          class="available-item" :class="{ selected: selectedCaseIds.includes(c.id) }"
          @click="toggleSelectCase(c.id)">
          <div class="avail-check">{{ selectedCaseIds.includes(c.id) ? '✓' : '' }}</div>
          <div class="avail-info">
            <span class="avail-name">{{ c.name }}</span>
            <span class="avail-endpoint">{{ c.endpoint?.name || '' }}</span>
          </div>
        </div>
        <div v-if="!filteredAvailableCases.length" class="empty-state">暂无可用用例</div>
      </div>
      <div class="selected-count">已选 {{ selectedCaseIds.length }} 条</div>
      <div class="modal-actions">
        <button @click="showAddCaseDialog=false" class="btn">取消</button>
        <button @click="confirmAddCases" class="btn btn-primary" :disabled="!selectedCaseIds.length">添加到套件</button>
      </div>
    </div>
  </div>

  <!-- 运行结果弹框 -->
  <div v-if="showRunDialog" class="modal" @click.self="showRunDialog=false">
    <div class="modal-content">
      <h3>执行测试套件</h3>
      <div v-if="runResult.loading" class="loading-state"><div class="spinner"></div><p>正在提交执行...</p></div>
      <div v-else-if="runResult.success" class="success-state">
        <div class="success-icon">✓</div>
        <p>已提交执行，结果 ID: <strong>{{ runResult.result_id }}</strong></p>
        <div class="modal-actions">
          <button @click="showRunDialog=false" class="btn">关闭</button>
          <button @click="viewResult(runResult.result_id)" class="btn btn-primary">查看结果</button>
        </div>
      </div>
      <div v-else-if="runResult.error" class="error-state">
        <div class="error-icon">✗</div>
        <p>{{ runResult.error }}</p>
        <button @click="showRunDialog=false" class="btn">关闭</button>
      </div>
    </div>
  </div><!-- /suite-detail -->
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getSuiteDetail, updateSuite, deleteSuite, runSuite as runSuiteApi, getRunResults,
  getSuiteCaseItems, batchAddCaseItems, deleteCaseItem, updateCaseItem, reorderCaseItems,
  getEnvironments
} from '@/api/suite'
import { getCases } from '@/api/case'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { useUserStore } from '@/stores/user'
import { getMyProductLines } from '@/api/productLine'

const userStore = useUserStore()

const route   = useRoute()
const router  = useRouter()
const suiteId = route.params.id

const suite        = ref(null)
const caseItems    = ref([])
const results      = ref([])
const projects     = ref([])
const environments = ref([])
const orderChanged = ref(false)
const editing      = ref(false)
const saving       = ref(false)
const editVars     = ref([])
const activeTab    = ref('info')
const mainTabs = [
  { id: 'info',    label: '基本信息', icon: '📋' },
  { id: 'cases',   label: '执行用例', icon: '▶' },
  { id: 'vars',    label: '套件变量', icon: '🔑' },
  { id: 'headers', label: '套件请求头', icon: '🌐' },
]
const editActiveTab = ref('basic')
const editTabs = [
  { id: 'basic',   label: '基本信息', icon: '📋' },
  { id: 'vars',    label: '套件变量', icon: '🔑' },
  { id: 'headers', label: '套件请求头', icon: '🌐' },
  { id: 'policy',  label: '执行策略', icon: '🎯' },
]

const showAddCaseDialog = ref(false)
const showRunDialog     = ref(false)
const addingCaseType    = ref('API')
const addingRole        = ref('main')
const addingProductLine = ref(null)   // null = 全部产品线
const addingProductLines = ref([])    // 所有产品线供筛选
const availableCases    = ref([])
const caseSearch        = ref('')
const selectedCaseIds   = ref([])
const runResult         = ref({ loading: false, success: false, error: null, result_id: null })

const formData = ref({ name: '', description: '', run_type: 'O', cron: '', hook_key: '', project: null, environment: null, timeout_seconds: 0, fail_strategy: 'continue', retry_count: 0, retry_delay: 1.0 })

const runTypes = [
  { value: 'O', label: '手动执行', icon: '▶' },
  { value: 'C', label: '定时执行', icon: '🕐' },
  { value: 'W', label: 'WebHook',  icon: '🔗' },
]
const cronPresets = [
  { label: '每分钟', value: '* * * * *' },
  { label: '每小时', value: '0 * * * *' },
  { label: '每天9点', value: '0 9 * * *' },
  { label: '工作日9点', value: '0 9 * * 1-5' },
  { label: '每天0点', value: '0 0 * * *' },
]

const filteredAvailableCases = computed(() => {
  let list = availableCases.value
  if (addingProductLine.value) {
    list = list.filter(c => c.product_line === addingProductLine.value ||
      (c.project_product_line && c.project_product_line === addingProductLine.value))
  }
  if (!caseSearch.value) return list
  const q = caseSearch.value.toLowerCase()
  return list.filter(c => c.name.toLowerCase().includes(q))
})

// 按 role 分组
const setupItems    = computed(() => caseItems.value.filter(i => i.role === 'setup'))
const mainItems     = computed(() => caseItems.value.filter(i => !i.role || i.role === 'main'))
const teardownItems = computed(() => caseItems.value.filter(i => i.role === 'teardown'))

const loadSuite = async () => {
  const res = await getSuiteDetail(suiteId)
  suite.value = res.result || res
  syncSuiteVarRows()
  syncSuiteHeaderRows()
}

const loadCaseItems = async () => {
  const res = await getSuiteCaseItems(suiteId)
  caseItems.value = (res.result?.list || res.result || res || []).sort((a, b) => a.order - b.order)
  orderChanged.value = false
}

const loadResults = async () => {
  const res = await getRunResults({ suite: suiteId, page_size: 10 })
  results.value = res.result?.list || []
}

const startEdit = () => {
  const s = suite.value
  formData.value = {
    name:            s.name,
    description:     s.description || '',
    run_type:        s.run_type || 'O',
    cron:            s.cron || '',
    hook_key:        s.hook_key || '',
    project:         s.project,
    environment:     s.environment || null,
    timeout_seconds: s.timeout_seconds ?? 0,
    fail_strategy:   s.fail_strategy || 'continue',
    retry_count:     s.retry_count ?? 0,
    retry_delay:     s.retry_delay ?? 1.0,
  }
  editVars.value = s.suite_variables
    ? Object.entries(s.suite_variables).map(([k, v]) => ({ k, v: String(v) }))
    : []
  editActiveTab.value = 'basic'
  editing.value = true
}

const cancelEdit = () => { editing.value = false }

const addVar = () => {
  if (!editing.value) startEdit()
  editVars.value.push({ k: '', v: '' })
}

// 套件变量行内编辑
const suiteVarRows = ref([])

const syncSuiteVarRows = () => {
  const vars = suite.value?.suite_variables || {}
  suiteVarRows.value = Object.entries(vars).map(([k, v]) => ({ k, v: String(v), _edit: false }))
}

// 套件请求头行内编辑
const suiteHeaderRows = ref([])

const syncSuiteHeaderRows = () => {
  const headers = suite.value?.suite_headers || {}
  suiteHeaderRows.value = Object.entries(headers).map(([k, v]) => ({ k, v: String(v), _edit: false }))
}

const addSuiteHeader = () => {
  suiteHeaderRows.value.unshift({ k: '', v: '', _edit: true })
}

const saveSuiteHeader = async (idx) => {
  const row = suiteHeaderRows.value[idx]
  if (!row.k?.trim()) return alert('Header 名不能为空')
  const isDup = suiteHeaderRows.value.some((r, i) => i !== idx && r.k?.trim() === row.k.trim())
  if (isDup) return alert(`Header「${row.k.trim()}」已存在`)
  saving.value = true
  try {
    const shObj = {}
    for (const r of suiteHeaderRows.value) {
      const key = r === row ? row.k.trim() : r.k?.trim()
      if (key) shObj[key] = r === row ? row.v : r.v
    }
    await updateSuite(suiteId, { ...suite.value, suite_headers: shObj })
    await loadSuite()
    syncSuiteHeaderRows()
  } catch (e) { alert('保存失败: ' + (e.response?.data?.message || e.message)) }
  finally { saving.value = false }
}

const cancelSuiteHeader = (idx) => {
  const row = suiteHeaderRows.value[idx]
  if (!row.k && !row.v) suiteHeaderRows.value.splice(idx, 1)
  else row._edit = false
}

const deleteSuiteHeader = async (idx) => {
  const row = suiteHeaderRows.value[idx]
  const ok = await confirm(`确定删除请求头「${row.k}」吗？`, { type: 'danger' })
  if (!ok) return
  saving.value = true
  try {
    const shObj = {}
    suiteHeaderRows.value.forEach((r, i) => { if (i !== idx && r.k?.trim()) shObj[r.k.trim()] = r.v })
    await updateSuite(suiteId, { ...suite.value, suite_headers: Object.keys(shObj).length ? shObj : null })
    await loadSuite()
    syncSuiteHeaderRows()
  } catch (e) { alert('删除失败: ' + (e.response?.data?.message || e.message)) }
  finally { saving.value = false }
}

const addSuiteVar = () => {
  suiteVarRows.value.unshift({ k: '', v: '', _edit: true })
}

const saveSuiteVar = async (idx) => {
  const row = suiteVarRows.value[idx]
  if (!row.k?.trim()) return alert('变量名不能为空')
  const isDup = suiteVarRows.value.some((r, i) => i !== idx && r.k?.trim() === row.k.trim())
  if (isDup) return alert(`变量名「${row.k.trim()}」已存在`)
  saving.value = true
  try {
    const svObj = {}
    for (const r of suiteVarRows.value) {
      const key = r === row ? row.k.trim() : r.k?.trim()
      if (key) svObj[key] = r === row ? row.v : r.v
    }
    await updateSuite(suiteId, { ...suite.value, suite_variables: svObj })
    await loadSuite()
    syncSuiteVarRows()
  } catch (e) { alert('保存失败: ' + (e.response?.data?.message || e.message)) }
  finally { saving.value = false }
}

const cancelSuiteVar = (idx) => {
  const row = suiteVarRows.value[idx]
  if (!row.k && !row.v) suiteVarRows.value.splice(idx, 1)
  else row._edit = false
}

const deleteSuiteVar = async (idx) => {
  const row = suiteVarRows.value[idx]
  const ok = await confirm(`确定删除变量「${row.k}」吗？`, { type: 'danger' })
  if (!ok) return
  saving.value = true
  try {
    const svObj = {}
    suiteVarRows.value.forEach((r, i) => { if (i !== idx && r.k?.trim()) svObj[r.k.trim()] = r.v })
    await updateSuite(suiteId, { ...suite.value, suite_variables: Object.keys(svObj).length ? svObj : null })
    await loadSuite()
    syncSuiteVarRows()
  } catch (e) { alert('删除失败: ' + (e.response?.data?.message || e.message)) }
  finally { saving.value = false }
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const svObj = {}
    for (const r of editVars.value) if (r.k?.trim()) svObj[r.k.trim()] = r.v
    await updateSuite(suiteId, {
      ...formData.value,
      suite_variables: Object.keys(svObj).length ? svObj : null,
    })
    editing.value = false
    await loadSuite()
  } catch (e) { alert('保存失败: ' + (e.response?.data?.message || e.message)) }
  finally { saving.value = false }
}

const deleteSuiteItem = async () => {
  const confirmed = await confirm('确定要删除这个测试套件吗？', { type: 'danger' })
  if (!confirmed) return
  await deleteSuite(suiteId)
  router.push('/suites')
}

const runSuite = async () => {
  showRunDialog.value = true
  runResult.value = { loading: true, success: false, error: null, result_id: null }
  try {
    const res = await runSuiteApi(suiteId, {})
    const resultId = res.result?.result_id || res.result_id
    runResult.value = { loading: false, success: true, error: null, result_id: resultId }
    setTimeout(loadResults, 1500)
  } catch (e) {
    runResult.value = { loading: false, success: false,
      error: e.response?.data?.message || e.message || '执行失败', result_id: null }
  }
}

const openAddCaseDialog = async (caseType, role = 'main') => {
  addingCaseType.value = caseType
  addingRole.value = role
  selectedCaseIds.value = []
  caseSearch.value = ''
  addingProductLine.value = userStore.currentProductLine?.id || null
  showAddCaseDialog.value = true
  // 加载所有产品线供切换筛选
  if (!addingProductLines.value.length) {
    try {
      const pr = await getMyProductLines()
      addingProductLines.value = pr.result || pr || []
    } catch (e) { console.error(e) }
  }
  // 加载全部用例（不按产品线过滤，允许跨产品线选择）
  const res = await getCases({ page_size: 500 })
  availableCases.value = res.result?.list || []
}

const toggleSelectCase = (id) => {
  const idx = selectedCaseIds.value.indexOf(id)
  if (idx === -1) selectedCaseIds.value.push(id)
  else selectedCaseIds.value.splice(idx, 1)
}

const confirmAddCases = async () => {
  try {
    await batchAddCaseItems({ suite: suiteId, case_type: addingCaseType.value, case_ids: selectedCaseIds.value, role: addingRole.value })
    showAddCaseDialog.value = false
    loadCaseItems()
  } catch (e) { alert(e.response?.data?.message || '添加失败') }
}

const removeCaseItem = async (item) => {
  const confirmed = await confirm(`确定移除用例「${item.case_name}」吗？`, { type: 'danger' })
  if (!confirmed) return
  await deleteCaseItem(item.id)
  loadCaseItems()
}

const toggleEnabled = async (item) => {
  try { await updateCaseItem(item.id, { enabled: item.enabled }) }
  catch { item.enabled = !item.enabled }
}

const moveUp = (idx) => {
  if (idx === 0) return
  const arr = caseItems.value;[arr[idx-1], arr[idx]] = [arr[idx], arr[idx-1]]
  orderChanged.value = true
}
const moveDown = (idx) => {
  if (idx === caseItems.value.length - 1) return
  const arr = caseItems.value;[arr[idx], arr[idx+1]] = [arr[idx+1], arr[idx]]
  orderChanged.value = true
}

const movePhaseUp = (role, idx) => {
  const phaseArr = role === 'setup' ? setupItems.value : role === 'teardown' ? teardownItems.value : mainItems.value
  if (idx === 0) return
  const a = caseItems.value.indexOf(phaseArr[idx - 1])
  const b = caseItems.value.indexOf(phaseArr[idx]);[caseItems.value[a], caseItems.value[b]] = [caseItems.value[b], caseItems.value[a]]
  orderChanged.value = true
}
const movePhaseDown = (role, idx) => {
  const phaseArr = role === 'setup' ? setupItems.value : role === 'teardown' ? teardownItems.value : mainItems.value
  if (idx === phaseArr.length - 1) return
  const a = caseItems.value.indexOf(phaseArr[idx])
  const b = caseItems.value.indexOf(phaseArr[idx + 1]);[caseItems.value[a], caseItems.value[b]] = [caseItems.value[b], caseItems.value[a]]
  orderChanged.value = true
}

const saveOrder = async () => {
  const items = caseItems.value.map((item, idx) => ({ id: item.id, order: idx }))
  await reorderCaseItems(items)
  orderChanged.value = false
  loadCaseItems()
}

const viewResult = (id) => { showRunDialog.value = false; router.push(`/results?id=${id}`) }
const getStatusClass = (s) => ({ 0:'status-init', 1:'status-ready', 2:'status-running', 3:'status-reporting', 4:'status-done', '-1':'status-error' })[s] || 'status-init'
const getStatusText  = (s) => ({ 0:'初始化', 1:'准备开始', 2:'正在执行', 3:'生成报告', 4:'执行完毕', '-1':'执行出错' })[s] || '未知'

onMounted(async () => {
  const [, , , pr, er] = await Promise.all([
    loadSuite(), loadCaseItems(), loadResults(),
    getProjects({ page_size: 200 }),
    getEnvironments({ page_size: 200 }),
  ])
  projects.value     = pr.result?.list || []
  environments.value = er.result?.list || []
})
</script>

<style scoped>
.detail-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:24px; }
.btn-back { background:white; border:1px solid var(--border); color:var(--text); }
.btn-success { background:#27ae60; color:white; }
.btn-success:hover { background:#229954; }
.header-actions { display:flex; gap:12px; }
/* 主 Tab 导航 */
.main-tabs { display:flex; border-bottom:2px solid var(--border); margin-bottom:20px; gap:4px; }
.main-tab { display:flex; align-items:center; gap:6px; padding:10px 20px; border:none; background:none; cursor:pointer; font-size:14px; font-weight:500; color:var(--text-light); border-bottom:2px solid transparent; margin-bottom:-2px; transition:all .15s; border-radius:6px 6px 0 0; }
.main-tab:hover { color:var(--accent); background:#f0f7ff; }
.main-tab.active { color:var(--accent); border-bottom-color:var(--accent); background:white; font-weight:700; }
/* 套件变量全宽卡片 */
.vars-card-full { padding:24px; }
.vars-full-header { display:flex; align-items:center; gap:12px; margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid var(--border); }
.vars-full-hint { font-size:12px; color:var(--text-light); flex:1; }
.vars-full-hint code { background:#f0f4f8; padding:1px 5px; border-radius:3px; font-family:monospace; font-size:11px; }
.vars-empty-full { text-align:center; padding:40px; color:var(--text-light); font-size:13px; font-style:italic; }
.info-card { padding:24px; margin-bottom:0; }
.info-card h2 { font-size:20px; font-weight:700; margin-bottom:16px; color:var(--primary); }
.edit-title { font-size:15px; font-weight:700; color:var(--primary); margin-bottom:16px; padding-bottom:12px; border-bottom:1px solid var(--border); }
.info-grid { display:flex; flex-direction:column; gap:14px; }
.info-item { display:flex; flex-direction:column; gap:4px; }
.info-item.full-width { }
.info-item label { font-size:11px; color:var(--text-light); font-weight:600; text-transform:uppercase; letter-spacing:.5px; }
.info-item span,.info-item code { font-size:13px; color:var(--text); }
.info-item code { font-family:monospace; background:var(--bg,#f5f5f5); padding:2px 6px; border-radius:4px; }
.left-section-title { font-size:11px; font-weight:700; color:var(--primary); margin:14px 0 8px; padding-bottom:5px; border-bottom:1px solid var(--border); text-transform:uppercase; letter-spacing:.5px; }
/* 右列套件变量 */
.vars-card { padding:16px; }
.vars-card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; padding-bottom:10px; border-bottom:1px solid var(--border); }
.vars-card-title { font-size:13px; font-weight:700; color:var(--primary); }
.vars-empty { font-size:12px; color:var(--text-light); text-align:center; padding:20px 0; font-style:italic; }
.vars-hint { font-size:11px; color:var(--text-light); margin-bottom:10px; }
.vars-hint code { background:#f0f4f8; padding:1px 4px; border-radius:3px; font-family:monospace; font-size:11px; }
.type-badge { display:inline-block; padding:4px 12px; border-radius:12px; font-size:12px; font-weight:600; }
.type-O { background:#e3f2fd; color:#1976d2; } .type-C { background:#fff3e0; color:#e65100; } .type-W { background:#f3e5f5; color:#7b1fa2; }
.env-badge { display:inline-block; background:#e3f2fd; color:#1565c0; padding:3px 10px; border-radius:10px; font-size:13px; }
.var-chips { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
.var-chip { display:inline-flex; align-items:center; gap:6px; background:#f8f4ff; border:1px solid #e8deff; border-radius:6px; padding:3px 10px; font-size:12px; }
.form-row-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }
.input-addon { display:flex; align-items:center; border:1px solid var(--border); border-radius:6px; overflow:hidden; }
.input-addon input { border:none; outline:none; padding:8px 10px; flex:1; font-size:13px; min-width:0; }
.addon-unit { padding:8px 10px; background:#f5f7fa; color:var(--text-light); font-size:12px; border-left:1px solid var(--border); white-space:nowrap; }
.radio-group { display:flex; gap:8px; flex-wrap:wrap; }
.radio-opt { display:inline-flex; align-items:center; gap:6px; padding:7px 14px; border:1px solid var(--border); border-radius:6px; cursor:pointer; font-size:13px; transition:all .15s; }
.radio-opt.active { border-color:var(--accent); background:#e3f2fd; color:var(--accent); font-weight:600; }
.retry-row { display:flex; align-items:center; gap:8px; }
.retry-sep { color:var(--text-light); font-size:13px; white-space:nowrap; }
.policy-chips { display:flex; flex-wrap:wrap; gap:8px; }
.policy-chip { display:inline-flex; align-items:center; gap:4px; padding:4px 12px; border-radius:20px; font-size:12px; background:#f0f0f0; color:var(--text); border:1px solid var(--border); }
.chip-danger { background:#fff0f0; color:var(--danger); border-color:#ffcdd2; }
.chip-ok { background:#f0fff4; color:var(--success); border-color:#c8e6c9; }
.var-chip code { background:#ede7f6; color:#6a1b9a; padding:1px 5px; border-radius:3px; font-size:11px; }

.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.form-group { margin-bottom:20px; }
.form-group label { display:flex; align-items:center; gap:8px; font-size:13px; font-weight:600; color:var(--text); margin-bottom:8px; }
.required { color:var(--danger); }
.field-hint { font-size:12px; color:var(--text-light); margin-top:6px; display:block; }
.field-hint code { background:var(--bg,#f5f7fa); padding:1px 5px; border-radius:3px; font-family:monospace; }
.run-type-options { display:flex; gap:10px; flex-wrap:wrap; }
.run-type-radio { display:flex; align-items:center; gap:6px; padding:8px 20px; border-radius:8px; border:1.5px solid var(--border); cursor:pointer; font-size:13px; font-weight:600; color:var(--text-light); background:white; user-select:none; transition:all .15s; }
.run-type-radio:hover { border-color:var(--accent); color:var(--accent); }
.run-type-radio.active.rt-o { background:#e3f2fd; color:#1976d2; border-color:#1976d2; }
.run-type-radio.active.rt-c { background:#fff3e0; color:#e65100; border-color:#e65100; }
.run-type-radio.active.rt-w { background:#f3e5f5; color:#7b1fa2; border-color:#7b1fa2; }
.rt-icon { font-size:15px; }
.cron-presets { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:10px; }
.preset-tag { padding:4px 12px; border-radius:12px; font-size:12px; background:var(--bg,#f5f7fa); border:1px solid var(--border); cursor:pointer; transition:all .2s; user-select:none; }
.preset-tag:hover,.preset-tag.active { background:var(--accent); color:white; border-color:var(--accent); }
.section-title { font-size:13px; font-weight:700; color:var(--primary); margin:24px 0 10px; padding-bottom:8px; border-bottom:2px solid var(--accent); display:inline-block; }
.kv-table { border:1px solid var(--border); border-radius:6px; overflow:hidden; margin-bottom:10px; }
.kv-head { display:grid; grid-template-columns:1fr 1fr 28px; background:var(--primary); color:white; font-size:11px; font-weight:600; padding:7px 10px; gap:8px; }
.kv-row-2 { display:grid; grid-template-columns:1fr 1fr 28px; gap:8px; padding:6px 10px; border-top:1px solid var(--border); align-items:center; }
.kv-row-2:hover { background:#fafbfc; }
.kv-input { border:1px solid var(--border); border-radius:4px; padding:5px 8px; font-size:13px; font-family:'Monaco','Courier New',monospace; outline:none; width:100%; box-sizing:border-box; }
.kv-input:focus { border-color:var(--accent); }
.kv-del { background:none; border:none; color:#ccc; cursor:pointer; font-size:13px; }
.kv-del:hover { color:var(--danger); }
.btn-add-row { background:none; border:1px dashed var(--accent); color:var(--accent); border-radius:5px; padding:4px 14px; font-size:12px; cursor:pointer; margin-bottom:20px; }
.btn-add-row:hover { background:#e3f2fd; }

.cases-card { margin-bottom:0; padding:0; overflow:hidden; }
.phase-block { border-bottom:1px solid var(--border); }
.phase-block:last-child { border-bottom:none; }
.phase-header { display:flex; align-items:center; gap:8px; padding:12px 16px; background:#fafbfc; border-bottom:1px solid var(--border); flex-wrap:wrap; }
.phase-setup   .phase-header { background:#f0faf4; border-left:3px solid #27ae60; }
.phase-main    .phase-header { background:#f0f7ff; border-left:3px solid var(--accent); }
.phase-teardown .phase-header { background:#fff8f0; border-left:3px solid #f39c12; }
.phase-icon { font-size:14px; }
.phase-title { font-size:13px; font-weight:700; color:var(--text); }
.phase-badge { background:var(--accent); color:white; border-radius:10px; padding:1px 7px; font-size:11px; font-weight:600; }
.phase-hint { font-size:11px; color:var(--text-light); flex:1; }
.phase-header-right { display:flex; gap:6px; margin-left:auto; }
.phase-add-btn { margin-left:auto; }
.phase-table-wrap { overflow-x:auto; }
.phase-empty { padding:12px 16px; color:var(--text-light); font-size:12px; font-style:italic; }
.results-section { padding:16px; }
.results-section h3 { font-size:14px; font-weight:600; margin-bottom:12px; color:var(--primary); }
.results-list { display:flex; flex-direction:column; gap:6px; }
.result-item { display:flex; justify-content:space-between; align-items:center; padding:8px 12px; background:var(--bg,#f9f9f9); border-radius:6px; cursor:pointer; transition:all .2s; }
.result-item:hover { background:#e8f4f8; }
.result-info { display:flex; align-items:center; gap:8px; }
.result-id { font-weight:600; font-size:12px; }
.result-pass { padding:2px 7px; border-radius:8px; font-size:11px; font-weight:600; }
.result-pass.pass { background:#e8f5e9; color:#2e7d32; } .result-pass.fail { background:#ffebee; color:#c62828; }
.result-status { padding:3px 8px; border-radius:10px; font-size:11px; font-weight:500; }
.btn-sm { padding:6px 14px; font-size:13px; }
.case-table-wrap { overflow-x:auto; }
.row-disabled td { opacity:.45; }
.order-cell { text-align:center; }
.order-btns { display:flex; align-items:center; gap:4px; justify-content:center; }
.order-btn { width:22px; height:22px; border:1px solid var(--border); background:white; border-radius:4px; cursor:pointer; font-size:12px; padding:0; }
.order-btn:disabled { opacity:.3; cursor:not-allowed; }
.order-num { font-size:13px; font-weight:600; color:var(--text-light); min-width:16px; text-align:center; }
.case-name { font-weight:500; } .endpoint-name { font-size:13px; color:var(--text-light); }
.type-tag { display:inline-block; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700; }
.tag-api { background:#e3f2fd; color:#1565c0; } .tag-ui { background:#e8f5e9; color:#2e7d32; }
.toggle { position:relative; display:inline-block; width:36px; height:20px; }
.toggle input { opacity:0; width:0; height:0; }
.slider { position:absolute; inset:0; background:#ccc; border-radius:20px; cursor:pointer; transition:.3s; }
.slider:before { content:''; position:absolute; width:14px; height:14px; left:3px; bottom:3px; background:white; border-radius:50%; transition:.3s; }
.toggle input:checked + .slider { background:var(--accent); }
.toggle input:checked + .slider:before { transform:translateX(16px); }
.save-order-bar { display:flex; align-items:center; gap:12px; padding:10px 16px; background:#fff8e1; border-top:1px solid #ffe082; font-size:13px; color:#e65100; }
.btn-action { padding:6px 12px; border:none; background:var(--accent); color:white; border-radius:4px; cursor:pointer; font-size:13px; }
.btn-action.btn-danger { background:var(--danger); }

.results-section h3 { font-size:18px; font-weight:600; margin-bottom:16px; }
.results-list { display:flex; flex-direction:column; gap:8px; }
.result-item { display:flex; justify-content:space-between; align-items:center; padding:12px 16px; background:var(--bg,#f9f9f9); border-radius:8px; cursor:pointer; transition:all .2s; }
.result-item:hover { background:#e8f4f8; transform:translateX(4px); }
.result-info { display:flex; align-items:center; gap:12px; }
.result-id { font-weight:600; }
.result-pass { padding:2px 8px; border-radius:10px; font-size:12px; font-weight:600; }
.result-pass.pass { background:#e8f5e9; color:#2e7d32; } .result-pass.fail { background:#ffebee; color:#c62828; }
.result-status { padding:4px 12px; border-radius:12px; font-size:12px; font-weight:500; }
.status-init,.status-ready { background:#e3f2fd; color:#1976d2; }
.status-running,.status-reporting { background:#fff3e0; color:#f57c00; }
.status-done { background:#e8f5e9; color:#388e3c; } .status-error { background:#ffebee; color:#d32f2f; }

.modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px; overflow-y:auto; }
.modal-content { background:white; border-radius:12px; padding:32px; width:90%; max-width:520px; animation:slideUp .3s ease; }
.modal-large { max-width:680px; }
.modal-content h3 { margin-bottom:20px; font-size:18px; font-weight:600; }
.modal-actions { display:flex; gap:12px; justify-content:flex-end; margin-top:20px; }
.search-bar { margin-bottom:12px; }
.add-case-filters { display:flex; gap:10px; margin-bottom:12px; }
.filter-select-sm { border:1px solid var(--border); border-radius:6px; padding:7px 10px; font-size:13px; outline:none; min-width:140px; }
.search-input-sm { flex:1; border:1px solid var(--border); border-radius:6px; padding:7px 10px; font-size:13px; outline:none; }
.search-input-sm:focus, .filter-select-sm:focus { border-color:var(--accent); }
.available-cases { max-height:320px; overflow-y:auto; display:flex; flex-direction:column; gap:6px; }
.available-item { display:flex; align-items:center; gap:12px; padding:10px 14px; border:1px solid var(--border,#eee); border-radius:8px; cursor:pointer; transition:all .2s; }
.available-item:hover { border-color:var(--accent); background:#f0f8ff; }
.available-item.selected { border-color:var(--accent); background:#e3f2fd; }
.avail-check { width:20px; height:20px; border-radius:50%; background:var(--accent); color:white; font-size:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.avail-info { display:flex; flex-direction:column; gap:2px; }
.avail-name { font-weight:500; } .avail-endpoint { font-size:12px; color:var(--text-light); }
.selected-count { margin-top:10px; font-size:13px; color:var(--text-light); }
.loading-state,.success-state,.error-state { text-align:center; padding:24px; }
.spinner { width:40px; height:40px; border:4px solid var(--border); border-top-color:var(--accent); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 16px; }
.success-icon,.error-icon { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; margin:0 auto 12px; }
.success-icon { background:#27ae60; color:white; } .error-icon { background:#e74c3c; color:white; }
.empty-state { text-align:center; padding:32px; color:var(--text-light); }
@keyframes spin { to { transform:rotate(360deg); } }
@keyframes slideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
</style>