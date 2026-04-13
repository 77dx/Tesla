<template>
  <div class="ui-case-detail">
    <div class="detail-header">
      <button class="btn btn-back" @click="goBack">← 返回</button>
      <div class="header-actions">
        <button v-if="caseId" class="btn btn-success" @click="openRunDialog" :disabled="running">{{ running ? '执行中...' : '执行用例' }}</button>
        <button class="btn btn-primary" @click="save">保存</button>
        <button v-if="caseId" class="btn btn-danger" @click="remove">删除</button>
      </div>
    </div>

    <div class="card form-card">
      <div v-if="runResult" ref="runResultPanelRef" class="run-result-panel" :class="runResult.success ? 'is-pass' : 'is-fail'">
        <div class="run-result-head">
          <strong>最近一次执行结果</strong>
          <span class="run-result-badge">{{ runResult.success ? '通过' : '失败' }}</span>
        </div>
        <div class="run-result-grid">
          <div><label>耗时</label><span>{{ runResult.duration || 0 }}s</span></div>
          <div><label>重试次数</label><span>{{ runResult.retry_count || 0 }}</span></div>
          <div><label>提取变量</label><span>{{ Object.keys(runResult.extracted || {}).length }}</span></div>
          <div><label>断言数</label><span>{{ (runResult.assertions || []).length }}</span></div>
        </div>
        <div v-if="runResult.error" class="run-result-error">
          <div class="run-error-head">
            <strong>{{ errorSummary(runResult.error) }}</strong>
            <button v-if="hasVerboseError(runResult.error)" class="btn-action btn-info" @click="showFullError = !showFullError">{{ showFullError ? '收起详情' : '展开详情' }}</button>
          </div>
          <pre v-if="showFullError && hasVerboseError(runResult.error)" class="run-error-detail">{{ runResult.error }}</pre>
        </div>
        <div v-if="runResult.assertions?.filter(item => item.pass).length" class="result-section">
          <div class="result-title">断言结果</div>
          <div class="assertion-list">
            <div v-for="(item, idx) in runResult.assertions.filter(item => item.pass)" :key="idx" class="assertion-item ok">
              <strong>{{ item.name || item.type }}</strong>
              <span>通过</span>
            </div>
          </div>
        </div>
        <div v-if="runResult.screenshots?.length" class="result-section">
          <div class="result-title">执行截图</div>
          <div class="shot-grid">
            <a v-for="(shot, idx) in runResult.screenshots" :key="idx" :href="resolveHistoryShotUrl(runResult.history_id || 0, idx)" target="_blank" rel="noreferrer" class="shot-link">
              <img :src="resolveHistoryShotUrl(runResult.history_id || 0, idx)" :alt="`截图 ${idx + 1}`" class="shot-img" />
            </a>
          </div>
        </div>
        <div v-if="runResult.execution_logs?.length" class="result-section">
          <div class="result-title">执行日志</div>
          <div class="log-list">
            <div v-for="(log, idx) in runResult.execution_logs" :key="`run-log-${idx}`" class="log-item">{{ log }}</div>
          </div>
        </div>
      </div>
      <div class="tab-nav">
        <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">{{ tab }}</button>
      </div>

      <div v-show="activeTab === '基本信息'" class="tab-panel">
        <div class="form-row-2">
          <div class="form-group">
            <label>名称</label>
            <input v-model="form.name" />
          </div>
          <div class="form-group">
            <label>平台</label>
            <select v-model="form.platform">
              <option value="web">Web</option>
              <option value="app">App</option>
            </select>
          </div>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>项目</label>
            <select v-model="form.project">
              <option :value="null">不指定</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>产品线</label>
            <select v-model="form.product_line">
              <option :value="null">不指定</option>
              <option v-for="pl in productLines" :key="pl.id" :value="pl.id">{{ pl.name }}</option>
            </select>
          </div>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>迭代</label>
            <select v-model="form.sprint" @change="loadRequirements">
              <option :value="null">不指定</option>
              <option v-for="s in sprints" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>需求</label>
            <select v-model="form.requirement">
              <option :value="null">不指定</option>
              <option v-for="r in requirements" :key="r.id" :value="r.id">{{ r.title }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>入口地址</label>
          <input v-model="form.entry_url" placeholder="/login 或 https://example.com/login" />
        </div>
      </div>

      <div v-show="activeTab === '步骤'" class="tab-panel">
        <div class="section-actions">
          <button class="btn btn-sm" @click="collapseAllSteps(false)">全部展开</button>
          <button class="btn btn-sm" @click="collapseAllSteps(true)">全部折叠</button>
          <button class="btn btn-sm" @click="addStep">+ 添加步骤</button>
        </div>
        <div v-for="(step, idx) in steps" :key="idx" class="step-card" :class="{ collapsed: isStepCollapsed(idx) }">
          <div class="step-head">
            <div class="step-head-main" @click="toggleStepCollapsed(idx)">
              <span class="step-index">步骤 {{ idx + 1 }}</span>
              <strong>{{ step.name || actionLabel(step.action) || '未命名步骤' }}</strong>
              <span class="step-summary">{{ stepSummary(step) }}</span>
            </div>
            <div class="step-tools">
              <button class="btn-action" @click="toggleStepCollapsed(idx)">{{ isStepCollapsed(idx) ? '展开' : '收起' }}</button>
              <button class="btn-action" @click="duplicateStep(idx)">复制</button>
              <button class="btn-action" :disabled="idx===0" @click="moveStep(idx, -1)">上移</button>
              <button class="btn-action" :disabled="idx===steps.length-1" @click="moveStep(idx, 1)">下移</button>
              <button class="btn-action btn-danger" @click="steps.splice(idx, 1)">删除</button>
            </div>
          </div>
          <div v-if="!isStepCollapsed(idx)" class="step-body">
            <div class="form-row-2">
              <div class="form-group"><label>名称</label><input v-model="step.name" /></div>
              <div class="form-group"><label>动作</label><select v-model="step.action"><option v-for="action in actionOptions" :key="action.value" :value="action.value">{{ action.label }}</option></select></div>
            </div>
            <div class="form-row-2" v-if="stepUsesLocator(step.action) || stepUsesValue(step.action)">
              <div v-if="stepUsesLocator(step.action)" class="form-group">
                <label>定位方式</label>
                <select v-model="step.locator_type">
                  <option value="css">CSS</option>
                  <option value="xpath">XPath</option>
                  <option value="text">Text</option>
                  <option value="id">ID</option>
                </select>
              </div>
              <div v-if="stepUsesLocator(step.action)" class="form-group"><label>定位符</label><input v-model="step.locator" placeholder="css/xpath/text" /></div>
              <div v-if="stepUsesValue(step.action)" class="form-group"><label>值</label><input v-model="step.value" placeholder="支持 ${var}" /></div>
            </div>
            <div class="form-row-2" v-if="stepUsesTarget(step.action) || stepUsesSaveAs(step.action) || stepUsesAttr(step.action) || stepUsesStorageKey(step.action)">
              <div v-if="stepUsesTarget(step.action)" class="form-group"><label>目标地址</label><input v-model="step.target" placeholder="goto 使用" /></div>
              <div v-if="stepUsesSaveAs(step.action)" class="form-group"><label>保存变量名</label><input v-model="step.save_as" placeholder="extract_* 使用" /></div>
              <div v-if="stepUsesAttr(step.action)" class="form-group"><label>属性名</label><input v-model="step.attr" placeholder="如 data-id" /></div>
              <div v-if="stepUsesStorageKey(step.action)" class="form-group"><label>Storage Key</label><input v-model="step.key" placeholder="如 token" /></div>
            </div>
          </div>
        </div>
      </div>

      <div v-show="activeTab === '脚本与断言'" class="tab-panel">
        <div class="form-group">
          <label>前置脚本</label>
          <textarea v-model="form.pre_script" rows="6" placeholder="ctx['token'] = 'xxx'" />
        </div>
        <div class="form-group">
          <label>后置脚本</label>
          <textarea v-model="form.post_script" rows="6" placeholder="ctx['order_no'] = ctx.get('order_no', '')" />
        </div>

        <div class="editor-section">
          <div class="editor-section-header">
            <label>用例级断言</label>
            <button class="btn btn-sm" @click="addValidate">+ 添加断言</button>
          </div>
          <div v-if="validations.length" class="mini-list">
            <div v-for="(rule, idx) in validations" :key="`validate-${idx}`" class="mini-card">
              <div class="mini-card-head">
                <strong>断言 {{ idx + 1 }}</strong>
                <button class="btn-action btn-danger" @click="validations.splice(idx, 1)">删除</button>
              </div>
              <div class="form-row-3">
                <div class="form-group">
                  <label>类型</label>
                  <select v-model="rule.type">
                    <option value="url_contains">url_contains</option>
                    <option value="text_contains">text_contains</option>
                    <option value="visible">visible</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>名称</label>
                  <input v-model="rule.name" placeholder="可选" />
                </div>
                <div class="form-group">
                  <label>期望值</label>
                  <input v-model="rule.expected" placeholder="如 /dashboard" />
                </div>
              </div>
              <div class="form-group" v-if="rule.type !== 'url_contains'">
                <label>定位符</label>
                <input v-model="rule.locator" placeholder="如 .order-no" />
              </div>
            </div>
          </div>
          <div v-else class="inline-empty">暂无断言</div>
        </div>

        <div class="editor-section">
          <div class="editor-section-header">
            <label>用例级提取</label>
            <button class="btn btn-sm" @click="addExtract">+ 添加提取</button>
          </div>
          <div v-if="extractRules.length" class="mini-list">
            <div v-for="(rule, idx) in extractRules" :key="`extract-${idx}`" class="mini-card">
              <div class="mini-card-head">
                <strong>提取 {{ idx + 1 }}</strong>
                <button class="btn-action btn-danger" @click="extractRules.splice(idx, 1)">删除</button>
              </div>
              <div class="form-row-3">
                <div class="form-group">
                  <label>类型</label>
                  <select v-model="rule.type">
                    <option value="text">text</option>
                    <option value="value">value</option>
                    <option value="attr">attr</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>变量名</label>
                  <input v-model="rule.name" placeholder="如 order_no" />
                </div>
                <div class="form-group">
                  <label>属性名</label>
                  <input v-model="rule.attr" :disabled="rule.type !== 'attr'" placeholder="如 data-id" />
                </div>
              </div>
              <div class="form-group">
                <label>定位符</label>
                <input v-model="rule.locator" placeholder="如 .order-no" />
              </div>
            </div>
          </div>
          <div v-else class="inline-empty">暂无提取规则</div>
        </div>
      </div>
    </div>

    <div v-if="caseId" class="card form-card history-card">
      <div class="history-head">
        <strong>最近执行历史</strong>
        <button class="btn btn-sm" @click="loadHistory">刷新</button>
      </div>
      <div v-if="normalizedHistoryItems.length" class="history-list">
        <div v-for="item in normalizedHistoryItems" :key="item.id" class="history-item" :class="item.success ? 'ok' : 'bad'">
          <div class="history-main">
            <div class="history-title-row">
              <span class="history-badge">{{ item.success ? '通过' : '失败' }}</span>
              <strong>#{{ item.id }}</strong>
              <span>{{ formatDate(item.created_at) }}</span>
            </div>
            <div class="history-meta">环境：{{ item.environment_name || '未指定' }}　耗时：{{ Number(item.duration || 0).toFixed(3) }}s　重试：{{ item.retry_count || 0 }}</div>
            <div v-if="item.error" class="history-error">{{ errorSummary(item.error) }}</div>
            <div v-if="expandedHistoryId === item.id" class="history-detail">
              <pre v-if="item.error && hasVerboseError(item.error)" class="history-detail-error">{{ item.error }}</pre>
              <div v-if="passedAssertions(item).length" class="result-section">
                <div class="result-title">断言结果</div>
                <div class="assertion-list">
                  <div v-for="(assertion, idx) in passedAssertions(item)" :key="`history-${item.id}-assertion-${idx}`" class="assertion-item ok">
                    <strong>{{ assertion.name || assertion.type }}</strong>
                    <span>通过</span>
                  </div>
                </div>
              </div>
              <div v-if="item.screenshots?.length" class="result-section">
                <div class="result-title">执行截图</div>
                <div class="shot-grid">
                  <template v-for="(_, idx) in item.screenshots" :key="`history-${item.id}-shot-${idx}`">
                    <a v-if="resolveHistoryShotUrl(item.id, idx)" :href="resolveHistoryShotUrl(item.id, idx)" target="_blank" rel="noreferrer" class="shot-link">
                      <img :src="resolveHistoryShotUrl(item.id, idx)" :alt="`历史截图 ${idx + 1}`" class="shot-img" />
                    </a>
                    <div v-else class="shot-loading">截图加载中...</div>
                  </template>
                </div>
              </div>
              <div v-if="item.execution_logs?.length" class="result-section">
                <div class="result-title">执行日志</div>
                <div class="log-list">
                  <div v-for="(log, idx) in item.execution_logs" :key="`history-${item.id}-log-${idx}`" class="log-item">{{ log }}</div>
                </div>
              </div>
            </div>
          </div>
          <button class="btn-action btn-info" @click="toggleHistoryDetail(item)">{{ expandedHistoryId === item.id ? '收起' : '查看' }}</button>
        </div>
      </div>
      <div v-else class="inline-empty">暂无执行历史</div>
    </div>

    <div v-if="showRunDialog" class="modal" @click.self="showRunDialog = false">
      <div class="modal-content modal-medium">
        <h3>执行 UI 用例</h3>
        <div class="form-group">
          <label>运行环境</label>
          <select v-model="selectedEnvironmentId">
            <option :value="null">不指定环境</option>
            <option v-for="env in environments" :key="env.id" :value="env.id">{{ env.name }}</option>
          </select>
          <div v-if="selectedEnvironment" class="env-tip">Base URL：{{ selectedEnvironment.base_url || '未配置' }}</div>
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showRunDialog = false">取消</button>
          <button class="btn btn-success" @click="runCase" :disabled="running">{{ running ? '执行中...' : '开始执行' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getUICase, createUICase, updateUICase, runUICase, getUICaseHistory, getUICaseHistoryScreenshot, deleteUICase } from '@/api/uiCase'
import { getProjects } from '@/api/project'
import { getSprints, getRequirements } from '@/api/sprint'
import { getEnvironments } from '@/api/suite'
import { getMyProductLines } from '@/api/productLine'
import { alert } from '@/composables/useAlert'
import { confirm } from '@/composables/useConfirm'

const route = useRoute()
const router = useRouter()
const caseId = computed(() => route.params.id && route.params.id !== 'new' ? route.params.id : null)
const activeTab = ref('基本信息')
const tabs = ['基本信息', '步骤', '脚本与断言']
const stepUsesLocator = (action) => ['click', 'fill', 'press', 'select', 'wait_for_selector', 'assert_text', 'assert_visible', 'extract_text', 'extract_value', 'extract_attr'].includes(action)
const stepUsesValue = (action) => ['fill', 'press', 'select', 'wait_for_text', 'assert_text', 'assert_url', 'set_local_storage', 'set_session_storage'].includes(action)
const stepUsesTarget = (action) => ['goto'].includes(action)
const stepUsesSaveAs = (action) => ['extract_text', 'extract_value', 'extract_attr'].includes(action)
const stepUsesAttr = (action) => ['extract_attr'].includes(action)
const stepUsesStorageKey = (action) => ['set_local_storage', 'set_session_storage'].includes(action)
const projects = ref([])
const sprints = ref([])
const requirements = ref([])
const productLines = ref([])
const environments = ref([])
const showRunDialog = ref(false)
const selectedEnvironmentId = ref(null)
const running = ref(false)
const actionOptions = [
  { value: 'goto', label: 'goto（跳转）' },
  { value: 'reload', label: 'reload（刷新）' },
  { value: 'click', label: 'click（点击）' },
  { value: 'fill', label: 'fill（输入）' },
  { value: 'press', label: 'press（按键）' },
  { value: 'select', label: 'select（选择）' },
  { value: 'wait_for_selector', label: 'wait_for_selector（等待元素）' },
  { value: 'wait_for_text', label: 'wait_for_text（等待文本）' },
  { value: 'assert_text', label: 'assert_text（断言文本）' },
  { value: 'assert_visible', label: 'assert_visible（断言可见）' },
  { value: 'assert_url', label: 'assert_url（断言地址）' },
  { value: 'extract_text', label: 'extract_text（提取文本）' },
  { value: 'extract_value', label: 'extract_value（提取输入值）' },
  { value: 'extract_attr', label: 'extract_attr（提取属性）' },
  { value: 'set_local_storage', label: 'set_local_storage（写本地存储）' },
  { value: 'set_session_storage', label: 'set_session_storage（写会话存储）' },
  { value: 'screenshot', label: 'screenshot（截图）' },
]

const form = ref({ name: '', project: null, product_line: null, sprint: null, requirement: null, platform: 'web', entry_url: '', pre_script: '', post_script: '', validate: [], extract: [], steps: [] })
const runResult = ref(null)
const showFullError = ref(false)
const historyItems = ref([])
const expandedHistoryId = ref(null)
const collapsedSteps = ref({})
const historyScreenshotUrls = ref({})
const screenshotBlobUrls = ref([])

const revokeScreenshotBlobUrls = () => {
  screenshotBlobUrls.value.forEach((url) => {
    try { URL.revokeObjectURL(url) } catch (_) {}
  })
  screenshotBlobUrls.value = []
}

const resetHistoryScreenshotUrls = () => {
  revokeScreenshotBlobUrls()
  historyScreenshotUrls.value = {}
}

const loadHistoryScreenshots = async (historyId, count) => {
  if (!caseId.value || !historyId || !count) return
  const current = { ...(historyScreenshotUrls.value || {}) }
  if (Array.isArray(current[historyId]) && current[historyId].length === count && current[historyId].every(Boolean)) {
    return
  }
  const next = []
  for (let idx = 0; idx < count; idx += 1) {
    try {
      const blob = await getUICaseHistoryScreenshot(caseId.value, historyId, idx)
      const url = URL.createObjectURL(blob)
      screenshotBlobUrls.value.push(url)
      next.push(url)
    } catch (error) {
      next.push('')
    }
  }
  historyScreenshotUrls.value = { ...current, [historyId]: next }
}

const steps = ref([])
const validations = ref([])
const extractRules = ref([])
const normalizedHistoryItems = computed(() => Array.isArray(historyItems.value) ? historyItems.value : [])

const extractHistoryList = (payload) => {
  if (Array.isArray(payload)) return payload
  if (!payload || typeof payload !== 'object') return []
  if (Array.isArray(payload.result)) return payload.result
  if (Array.isArray(payload.list)) return payload.list
  return []
}

const loadRequirements = async () => {
  const res = await getRequirements(form.value.sprint ? { sprint: form.value.sprint, page_size: 500 } : { page_size: 500 })
  requirements.value = res.result?.list || res.result || []
}

const loadDetail = async () => {
  if (!caseId.value) return
  const res = await getUICase(caseId.value)
  const data = res.result || res
  form.value = { ...form.value, ...data }
  steps.value = Array.isArray(data.steps) ? data.steps : []
  validations.value = Array.isArray(data.validate) ? data.validate : []
  extractRules.value = Array.isArray(data.extract) ? data.extract : []
  await loadRequirements()
}

const normalizeHistoryItems = (items) => (Array.isArray(items) ? items : []).map(item => ({
  ...item,
  assertions: Array.isArray(item?.assertions) ? item.assertions : [],
  screenshots: Array.isArray(item?.screenshots) ? item.screenshots : [],
  execution_logs: Array.isArray(item?.execution_logs) ? item.execution_logs : [],
}))

const loadHistory = async () => {
  if (!caseId.value) return
  resetHistoryScreenshotUrls()
  const res = await getUICaseHistory(caseId.value)
  const level1 = extractHistoryList(res?.result?.result)
  const level2 = extractHistoryList(res?.result)
  const level3 = extractHistoryList(res)
  historyItems.value = normalizeHistoryItems(level1.length ? level1 : (level2.length ? level2 : level3))
}

const addStep = () => steps.value.push({ name: '', action: 'goto', locator_type: 'css', locator: '', value: '', target: '', save_as: '', enabled: true })
const addValidate = () => validations.value.push({ type: 'url_contains', name: '', expected: '', locator: '' })
const addExtract = () => extractRules.value.push({ type: 'text', name: '', locator: '', attr: '' })
const selectedEnvironment = computed(() => environments.value.find(env => env.id === selectedEnvironmentId.value) || null)
const isStepCollapsed = (idx) => !!collapsedSteps.value[idx]
const toggleStepCollapsed = (idx) => { collapsedSteps.value = { ...collapsedSteps.value, [idx]: !collapsedSteps.value[idx] } }
const collapseAllSteps = (collapsed) => { const next = {}; steps.value.forEach((_, idx) => { next[idx] = collapsed }); collapsedSteps.value = next }
const duplicateStep = (idx) => { steps.value.splice(idx + 1, 0, JSON.parse(JSON.stringify(steps.value[idx] || {}))) }
const moveStep = (idx, delta) => { const next = idx + delta; if (next < 0 || next >= steps.value.length) return; [steps.value[idx], steps.value[next]] = [steps.value[next], steps.value[idx]] }
const actionLabel = (value) => actionOptions.find(item => item.value === value)?.label || value || ''
const stepSummary = (step) => {
  if (!step) return ''
  const action = step.action || ''
  if (action === 'goto') return `跳转到 ${step.target || form.value.entry_url || '-'}`
  if (step.locator && step.value) return `${step.locator_type || 'css'} · ${step.locator} · ${step.value}`
  if (step.locator) return `${step.locator_type || 'css'} · ${step.locator}`
  if (step.value) return String(step.value)
  if (step.target) return String(step.target)
  return '点击展开编辑详细参数'
}
const goBack = () => router.push('/ui-cases')

const save = async () => {
  try {
    const payload = {
      ...form.value,
      steps: steps.value,
      validate: validations.value,
      extract: extractRules.value,
    }
    if (!payload.name?.trim()) return alert('名称不能为空')
    if (caseId.value) await updateUICase(caseId.value, payload)
    else {
      const res = await createUICase(payload)
      const id = res.result?.id || res.id
      router.replace(`/ui-cases/${id}`)
    }
    alert('保存成功', 'success')
  } catch (e) {
    alert(e.response?.data?.message || e.message || '保存失败')
  }
}

const remove = async () => {
  if (!caseId.value) return
  const ok = await confirm('确定删除该 UI 用例吗？', { type: 'danger' })
  if (!ok) return
  await deleteUICase(caseId.value)
  router.push('/ui-cases')
}

const openRunDialog = () => {
  selectedEnvironmentId.value = null
  showRunDialog.value = true
}

const toggleHistoryDetail = async (item) => {
  const nextId = expandedHistoryId.value === item.id ? null : item.id
  expandedHistoryId.value = nextId
  if (nextId && item?.screenshots?.length) {
    await loadHistoryScreenshots(nextId, item.screenshots.length)
  }
}

const formatDate = (value) => value ? new Date(value).toLocaleString('zh-CN') : '-'
const hasVerboseError = (value) => String(value || '').includes('\n') || String(value || '').length > 180
const errorSummary = (value) => String(value || '').split('\n')[0] || '执行失败'
const passedAssertions = (item) => (item?.assertions || []).filter(assertion => assertion?.pass)
const resolveHistoryShotUrl = (historyId, index) => historyScreenshotUrls.value?.[historyId]?.[index] || ''

watch(expandedHistoryId, async (historyId) => {
  if (!historyId) return
  const item = normalizedHistoryItems.value.find(entry => entry.id === historyId)
  if (item?.screenshots?.length) {
    await loadHistoryScreenshots(historyId, item.screenshots.length)
  }
})

onBeforeUnmount(() => {
  revokeScreenshotBlobUrls()
})

const runCase = async () => {
  if (!caseId.value) return
  running.value = true
  try {
    const payload = {}
    if (selectedEnvironmentId.value) payload.environment = selectedEnvironmentId.value
    const res = await runUICase(caseId.value, payload)
    const result = res.result?.result || res.result || res
    showFullError.value = false
    runResult.value = result
    await loadHistory()
    if (result?.history_id && result?.screenshots?.length) {
      await loadHistoryScreenshots(result.history_id, result.screenshots.length)
    }
    showRunDialog.value = false
    activeTab.value = '基本信息'
    if (result.success) await alert('执行通过', 'success')
    else await alert(`执行失败：${result.error || '未知错误'}`)
  } catch (e) {
    runResult.value = null
    await alert(e.response?.data?.message || e.message || '执行失败')
  } finally {
    running.value = false
  }
}

onMounted(async () => {
  const [projectRes, sprintRes, plRes, envRes] = await Promise.all([
    getProjects({ page_size: 500 }),
    getSprints({ page_size: 500 }),
    getMyProductLines(),
    getEnvironments({ page_size: 500 }),
  ])
  projects.value = projectRes.result?.list || projectRes.result || []
  sprints.value = sprintRes.result?.list || sprintRes.result || []
  productLines.value = plRes.result || plRes || []
  environments.value = envRes.result?.list || envRes.result || []
  await loadRequirements()
  await loadDetail()
  await loadHistory()
})
</script>

<style scoped>
.ui-case-detail { display:flex; flex-direction:column; gap:16px; }
.detail-header { display:flex; justify-content:space-between; align-items:center; }
.header-actions { display:flex; gap:10px; }
.form-card { padding:24px; }
.run-result-panel { border:1px solid var(--border); border-radius:14px; padding:16px; margin-bottom:18px; background:#fbfdff; }
.run-result-panel.is-pass { border-color:#cae9d5; background:#f4fbf6; }
.run-result-panel.is-fail { border-color:#f3c9c9; background:#fff7f7; }
.run-result-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.run-result-badge { padding:4px 10px; border-radius:999px; background:#e8eefc; color:#2c57ad; font-size:12px; font-weight:700; }
.run-result-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin-bottom:12px; }
.run-result-grid label { display:block; font-size:12px; color:var(--text-light); margin-bottom:4px; }
.run-result-error { padding:10px 12px; border-radius:10px; background:#fff0f0; color:#b42318; margin-bottom:12px; }
.run-error-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; }
.run-error-detail { margin:10px 0 0; padding:10px 12px; border-radius:8px; background:rgba(255,255,255,.7); border:1px solid #f3c9c9; color:#7a271a; font-size:12px; line-height:1.5; max-height:260px; overflow:auto; white-space:pre-wrap; word-break:break-word; }
.result-section { margin-top:12px; }
.result-title { font-size:13px; font-weight:700; margin-bottom:8px; }
.assertion-list { display:flex; flex-direction:column; gap:8px; }
.assertion-item { display:flex; justify-content:space-between; align-items:center; border:1px solid var(--border); border-radius:10px; padding:10px 12px; background:white; }
.assertion-item.ok { border-color:#cae9d5; }
.assertion-item.bad { border-color:#f3c9c9; }
.shot-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(180px,1fr)); gap:12px; }
.shot-link { display:block; }
.shot-img { width:100%; height:auto; max-height:320px; object-fit:contain; border-radius:10px; border:1px solid var(--border); background:#f6f8fb; }
.shot-loading { min-height:140px; border-radius:10px; display:flex; align-items:center; justify-content:center; background:#f6f8fb; color:#7a869a; font-size:13px; border:1px solid var(--border); }
.history-card { margin-top:16px; }
.history-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.history-list { display:flex; flex-direction:column; gap:10px; }
.history-item { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; border:1px solid var(--border); border-radius:12px; padding:12px 14px; background:#fff; }
.history-item.ok { border-color:#cae9d5; }
.history-item.bad { border-color:#f3c9c9; }
.history-main { display:flex; flex-direction:column; gap:6px; min-width:0; }
.history-title-row { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.history-badge { display:inline-flex; padding:2px 8px; border-radius:999px; background:#eef3ff; color:#3556a8; font-size:11px; font-weight:700; }
.history-meta { font-size:12px; color:var(--text-light); }
.history-error { font-size:12px; color:#b42318; }
.history-detail { margin-top:10px; display:flex; flex-direction:column; gap:12px; }
.history-detail-error { margin:0; padding:10px 12px; border-radius:8px; background:#fff7f7; border:1px solid #f3c9c9; color:#7a271a; font-size:12px; line-height:1.5; max-height:220px; overflow:auto; white-space:pre-wrap; word-break:break-word; }
.log-list { display:flex; flex-direction:column; gap:8px; }
.log-item { font-size:12px; line-height:1.6; color:#44526b; background:#f6f8fc; border:1px solid #dfe6f2; border-radius:8px; padding:8px 10px; word-break:break-word; }
.modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px; }
.modal-content { background:white; border-radius:12px; padding:24px; width:min(520px,92vw); }
.modal-medium { max-width:520px; }
.modal-actions { display:flex; justify-content:flex-end; gap:10px; margin-top:16px; }
.env-tip { margin-top:8px; font-size:12px; color:var(--accent); background:#eef4ff; padding:8px 10px; border-radius:8px; }
.tab-nav { display:flex; gap:8px; border-bottom:1px solid var(--border); margin-bottom:18px; }
.tab-btn { border:none; background:none; padding:10px 14px; cursor:pointer; color:var(--text-light); }
.tab-btn.active { color:var(--accent); border-bottom:2px solid var(--accent); font-weight:700; }
.tab-panel { display:flex; flex-direction:column; gap:12px; }
.form-row-2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.form-row-3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }
.form-group { display:flex; flex-direction:column; gap:8px; }
.form-group input,.form-group select,.form-group textarea { border:1px solid var(--border); border-radius:8px; padding:10px 12px; font-size:14px; }
.section-actions { display:flex; justify-content:flex-end; gap:8px; flex-wrap:wrap; }
.editor-section { border:1px solid var(--border); border-radius:12px; padding:16px; background:#fcfdff; }
.editor-section-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.mini-list { display:flex; flex-direction:column; gap:12px; }
.mini-card { border:1px solid #e5ecf7; border-radius:10px; padding:14px; background:white; }
.mini-card-head { display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; }
.inline-empty { color:var(--text-light); font-size:13px; }
.step-card { border:1px solid var(--border); border-radius:12px; padding:16px; background:#fafcff; }
.step-card.collapsed { padding-bottom:12px; }
.step-head { display:flex; justify-content:space-between; align-items:flex-start; gap:12px; margin-bottom:12px; }
.step-head-main { display:flex; flex-direction:column; gap:6px; min-width:0; cursor:pointer; }
.step-index { display:inline-flex; align-self:flex-start; padding:2px 8px; border-radius:999px; background:#eef3ff; color:#3556a8; font-size:11px; font-weight:700; }
.step-summary { color:var(--text-light); font-size:12px; word-break:break-all; }
.step-tools { display:flex; gap:6px; flex-wrap:wrap; justify-content:flex-end; }
.step-body { display:flex; flex-direction:column; gap:12px; }
</style>
