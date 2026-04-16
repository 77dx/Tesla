<template>
  <div class="case-detail-view">

    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回用例列表
      </button>
      <div class="page-header__actions">
        <!-- 运行控制区 -->
        <div class="run-controls">
          <select v-model="selectedRunEnvId" class="run-select" title="选择运行环境">
            <option :value="null">不指定环境</option>
            <option v-for="env in runEnvironments" :key="env.id" :value="env.id">{{ env.name }}</option>
          </select>
          <select v-model="selectedDatasetId" class="run-select" title="参数化数据集（选后将循环执行）">
            <option :value="null">不使用参数集</option>
            <option v-for="ds in runDatasets" :key="ds.id" :value="ds.id">📋 {{ ds.name }}（{{ ds.row_count }}行）</option>
          </select>
        </div>
        <button class="btn btn--success btn--sm" @click="runCase" :disabled="isRunning">
          <PlayCircleOutlined /> {{ isRunning ? '运行中...' : '运行用例' }}
        </button>
        <button class="btn btn--danger-ghost btn--sm" @click="deleteCaseItem">
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
    <div v-if="caseData && !loading" class="detail-content">

      <!-- 基本信息卡片 -->
      <div class="form-card">
        <div class="form-card__header">
          <div class="form-card__title-group">
            <div class="form-card__title-row">
              <div class="form-card__title">{{ caseData.name }}</div>
              <span class="case-id-badge">#{{ caseData.id }}</span>
            </div>
            <div class="form-card__subtitle" v-if="caseData.description">{{ caseData.description }}</div>
          </div>
        </div>
        <div class="form-card__body">
          <div class="info-grid">
            <div class="info-item" v-if="caseData.project_name">
              <label class="info-label">所属项目</label>
              <span class="info-value">
                <span class="project-link" @click="$router.push(`/projects/${caseData.project}`)">
                  {{ caseData.project_name }}
                </span>
              </span>
            </div>
            <div class="info-item" v-if="caseData.endpoint">
              <label class="info-label">关联接口</label>
              <span class="info-value">
                <span class="endpoint-link" @click="$router.push(`/endpoints/${caseData.endpoint.id}`)">
                  {{ caseData.endpoint.name }}
                </span>
              </span>
            </div>
            <div class="info-item" v-if="caseData.product_line_name">
              <label class="info-label">所属产品线</label>
              <div class="info-value">
                <div class="pl-badge">
                  <span class="pl-badge__dot" :style="{ background: plColor }"></span>
                  <span>{{ caseData.product_line_name }}</span>
                </div>
              </div>
            </div>
            <div class="info-item">
              <label class="info-label">创建时间</label>
              <span class="info-value">{{ formatDate(caseData.created_at) }}</span>
            </div>
            <div class="info-item" v-if="caseData.updated_at">
              <label class="info-label">更新时间</label>
              <span class="info-value">{{ formatDate(caseData.updated_at) }}</span>
            </div>
            <div class="info-item" v-if="caseData.created_by_name">
              <label class="info-label">创建人</label>
              <div class="info-value">
                <div class="creator-info">
                  <span class="creator-avatar">{{ caseData.created_by_name.charAt(0).toUpperCase() }}</span>
                  <span>{{ caseData.created_by_name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Allure 标注 -->
          <div v-if="caseData.alluer" class="alluer-block">
            <label class="info-label">Allure 标注</label>
            <pre class="alluer-pre">{{ JSON.stringify(caseData.alluer, null, 2) }}</pre>
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

          <!-- 关联接口 Tab -->
          <div v-show="activeTab === 'endpoint'" class="tab-content">
            <div v-if="caseData.endpoint" class="endpoint-detail-block">
              <div class="endpoint-header">
                <span class="method-badge" :class="`m-${(caseData.endpoint.method || 'GET').toLowerCase()}`">
                  {{ caseData.endpoint.method }}
                </span>
                <div class="endpoint-name">{{ caseData.endpoint.name }}</div>
                <button class="btn btn--primary btn--sm" @click="$router.push(`/endpoints/${caseData.endpoint.id}`)">
                  <ArrowRightOutlined /> 查看详情
                </button>
              </div>
              <div class="endpoint-url-row">
                <span v-if="caseData.endpoint.service_key" class="url-service-tag">{{ caseData.endpoint.service_key }}</span>
                <code class="endpoint-url">{{ caseData.endpoint.url || '-' }}</code>
              </div>
              <!-- 请求参数 -->
              <div v-if="caseData.endpoint.headers && Object.keys(caseData.endpoint.headers).length" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">请求头 Headers</span>
                  <span class="param-count">{{ Object.keys(caseData.endpoint.headers).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div v-for="(v, k) in caseData.endpoint.headers" :key="k" class="kv-display-row">
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>
              <div v-if="caseData.endpoint.params && Object.keys(caseData.endpoint.params).length" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">Query Params</span>
                  <span class="param-count">{{ Object.keys(caseData.endpoint.params).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div class="kv-display-head"><span>Key</span><span>Value</span></div>
                  <div v-for="(v, k) in caseData.endpoint.params" :key="k" class="kv-display-row">
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>
              <div v-if="caseData.endpoint.json && Object.keys(caseData.endpoint.json).length" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">JSON Body</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(caseData.endpoint.json, null, 2) }}</pre>
              </div>
              <div v-if="caseData.endpoint.data && Object.keys(caseData.endpoint.data).length" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">Form Data</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(caseData.endpoint.data, null, 2) }}</pre>
              </div>
            </div>
            <div v-else class="empty-tab">
              <ApiOutlined class="empty-tab__icon" />
              <p>未关联接口</p>
            </div>
          </div>

          <!-- 接口参数 Tab -->
          <div v-show="activeTab === 'params'" class="tab-content">
            <div class="params-display-grid">
              <!-- 用例请求头 -->
              <div v-if="parsedApiArgs?.headers && Object.keys(parsedApiArgs.headers).length" class="param-section">
                <div class="param-section__header">
                  <span class="param-section__title">请求头 Headers</span>
                  <span class="param-count">{{ Object.keys(parsedApiArgs.headers).length }}</span>
                </div>
                <div class="kv-display-table">
                  <div v-for="(v, k) in parsedApiArgs.headers" :key="k" class="kv-display-row">
                    <span class="kv-key">{{ k }}</span>
                    <span class="kv-value">{{ v }}</span>
                  </div>
                </div>
              </div>
              <!-- 用例 json -->
              <div v-if="parsedApiArgs?.json && Object.keys(parsedApiArgs.json).length" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">JSON Body</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(parsedApiArgs.json, null, 2) }}</pre>
              </div>
              <!-- 用例 data -->
              <div v-if="parsedApiArgs?.data && Object.keys(parsedApiArgs.data).length" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">Form Data</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(parsedApiArgs.data, null, 2) }}</pre>
              </div>
              <!-- 用例 params -->
              <div v-if="parsedApiArgs?.params && Object.keys(parsedApiArgs.params).length" class="param-section param-section--full">
                <div class="param-section__header">
                  <span class="param-section__title">Query Params</span>
                </div>
                <pre class="json-display">{{ JSON.stringify(parsedApiArgs.params, null, 2) }}</pre>
              </div>
              <div v-if="(!parsedApiArgs?.headers && !parsedApiArgs?.json && !parsedApiArgs?.data && !parsedApiArgs?.params)" class="empty-tab">
                <FileTextOutlined class="empty-tab__icon" />
                <p>未配置接口参数</p>
              </div>
            </div>
          </div>

          <!-- 数据提取 Tab -->
          <div v-show="activeTab === 'extract'" class="tab-content">
            <div v-if="extractRules.length" class="extract-display">
              <div class="extract-display__header">
                <span>共 <strong>{{ extractRules.length }}</strong> 条提取规则</span>
              </div>
              <div class="kv-display-table kv-display-table--4col">
                <div class="kv-display-head">
                  <span>变量名</span>
                  <span>JSONPath 表达式</span>
                  <span>取第几个</span>
                  <span>引用方式</span>
                </div>
                <div v-for="rule in extractRules" :key="rule.name" class="kv-display-row">
                  <span class="kv-key">{{ rule.name }}</span>
                  <span class="kv-value kv-value--green">{{ rule.expr }}</span>
                  <span class="kv-value">{{ rule.index }}</span>
                  <span><code class="var-ref">${ {{ rule.name }} }</code></span>
                </div>
              </div>
            </div>
            <div v-else class="empty-tab">
              <DownloadOutlined class="empty-tab__icon" />
              <p>未配置数据提取</p>
            </div>
          </div>

          <!-- 断言规则 Tab -->
          <div v-show="activeTab === 'validate'" class="tab-content">
            <div v-if="Array.isArray(caseData.validate) && caseData.validate.length" class="assert-display">
              <div class="assert-display__header">
                <span>共 <strong>{{ caseData.validate.length }}</strong> 条断言规则</span>
              </div>
              <div class="kv-display-table kv-display-table--5col">
                <div class="kv-display-head">
                  <span>#</span><span>断言描述</span><span>类型</span><span>来源</span><span>表达式 / 期望值</span>
                </div>
                <div v-for="(rule, idx) in caseData.validate" :key="idx" class="kv-display-row">
                  <span class="kv-idx">{{ idx + 1 }}</span>
                  <span class="kv-name">{{ rule.name }}</span>
                  <span><code class="type-badge" :class="`type-${rule.type}`">{{ rule.type }}</code></span>
                  <span><code class="source-badge">{{ rule.source }}</code></span>
                  <span class="kv-expr-val">
                    <span class="kv-expr">{{ rule.expr || '-' }}</span>
                    <span class="kv-arrow">→</span>
                    <span class="kv-expect">{{ rule.type === 'exists' ? '(存在即通过)' : rule.expect }}</span>
                  </span>
                </div>
              </div>
            </div>
            <pre v-else-if="caseData.validate && !Array.isArray(caseData.validate)" class="legacy-json">{{ JSON.stringify(caseData.validate, null, 2) }}</pre>
            <div v-else class="empty-tab">
              <CheckCircleOutlined class="empty-tab__icon" />
              <p>未配置断言规则</p>
            </div>
          </div>

          <!-- 用例脚本 Tab -->
          <div v-show="activeTab === 'script'" class="tab-content">
            <div class="script-display">
              <div v-if="caseData.pre_script" class="script-block">
                <div class="script-block__header">
                  <span class="script-badge script-badge--pre">PRE</span>
                  <span class="script-block__title">前置脚本</span>
                </div>
                <pre class="script-pre">{{ caseData.pre_script }}</pre>
              </div>
              <div v-if="caseData.post_script" class="script-block">
                <div class="script-block__header">
                  <span class="script-badge script-badge--post">POST</span>
                  <span class="script-block__title">后置脚本</span>
                </div>
                <pre class="script-pre">{{ caseData.post_script }}</pre>
              </div>
              <div v-if="!caseData.pre_script && !caseData.post_script" class="empty-tab">
                <CodeOutlined class="empty-tab__icon" />
                <p>未配置用例脚本</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 执行日志面板 -->
      <transition name="logpanel">
        <div v-if="runLogs.length" class="run-log-panel">
          <div class="log-panel-header">
            <div class="log-panel-title">
              <span class="log-panel-dot" :class="isRunning ? 'dot-running' : 'dot-idle'"></span>
              执行日志
              <span class="log-panel-count">{{ runLogs.length }} 条记录</span>
            </div>
            <button class="btn btn--ghost btn--sm" @click="loadRunLogs">
              <ReloadOutlined /> 刷新
            </button>
          </div>
          <div class="log-list">
            <div
              v-for="(record, idx) in runLogs"
              :key="record.id"
              class="log-record"
              :class="{ expanded: record.expanded }"
            >
              <div class="log-record-head" @click="record.expanded = !record.expanded">
                <span class="log-expand-icon">{{ record.expanded ? '▾' : '▸' }}</span>
                <span class="log-record-index">#{{ runLogs.length - idx }}</span>
                <span v-if="record.running" class="log-running-badge">
                  <span class="mini-spinner"></span> 运行中
                </span>
                <span v-else :class="record.success ? 'pass-badge' : 'fail-badge'">
                  {{ record.success ? '✓ 通过' : '✗ 失败' }}
                </span>
                <span v-if="!record.running && record.status_code" class="log-meta">{{ record.status_code }}</span>
                <span v-if="!record.running && record.duration" class="log-meta">{{ record.duration }}s</span>
                <span class="log-record-time">{{ record.time }}</span>
                <button class="log-del-btn" @click.stop="removeRunLog(idx)" title="删除">
                  <DeleteOutlined />
                </button>
              </div>

              <div v-if="record.expanded" class="log-record-body">
                <div v-if="record.running" class="log-running-hint">
                  <span class="spinner-sm"></span> 正在执行，请稍候...
                </div>
                <template v-else>
                  <!-- DDT 多行结果 -->
                  <div v-if="record.ddt" class="ddt-summary">
                    <div class="ddt-header">
                      <span class="ddt-title">📋 参数化执行：{{ record.dataset_name }}</span>
                      <span class="ddt-stat pass">✓ {{ record.ddt_passed }} 通过</span>
                      <span v-if="record.ddt_failed" class="ddt-stat fail">✗ {{ record.ddt_failed }} 失败</span>
                      <span class="ddt-stat total">共 {{ record.ddt_total }} 次</span>
                    </div>
                    <div v-for="r in record.ddt_results" :key="r.row_index"
                      class="ddt-row-item" :class="r.success ? 'ddt-pass' : 'ddt-fail'">
                      <span class="ddt-row-idx">第 {{ r.row_index }} 行</span>
                      <span class="ddt-row-badge">{{ r.success ? '✓' : '✗' }}</span>
                      <span class="ddt-row-params">{{ JSON.stringify(r.row_data) }}</span>
                      <span v-if="r.status_code" class="ddt-row-code">{{ r.status_code }}</span>
                      <span v-if="r.duration" class="ddt-row-dur">{{ r.duration }}s</span>
                      <span v-if="r.error" class="ddt-row-err">{{ r.error }}</span>
                    </div>
                  </div>

                  <!-- 错误信息 -->
                  <div v-if="!record.ddt && record.error" class="log-error-msg">⚠ {{ record.error }}</div>

                  <!-- 请求信息 -->
                  <div v-if="!record.ddt && record.request_info" class="log-section">
                    <div class="log-section__title">请求信息</div>
                    <div class="req-line">
                      <span class="req-method" :class="`m-${(record.request_info.method || 'GET').toLowerCase()}`">
                        {{ record.request_info.method }}
                      </span>
                      <code class="req-url">{{ record.request_info.url }}</code>
                    </div>
                    <div v-if="record.request_info.headers && Object.keys(record.request_info.headers).length" class="req-kv-block">
                      <span class="req-kv-label">Headers</span>
                      <pre class="log-json">{{ JSON.stringify(record.request_info.headers, null, 2) }}</pre>
                    </div>
                    <div v-if="record.request_info.params && Object.keys(record.request_info.params).length" class="req-kv-block">
                      <span class="req-kv-label">Query Params</span>
                      <pre class="log-json">{{ JSON.stringify(record.request_info.params, null, 2) }}</pre>
                    </div>
                    <div v-if="record.request_info.json" class="req-kv-block">
                      <span class="req-kv-label">JSON Body</span>
                      <pre class="log-json">{{ JSON.stringify(record.request_info.json, null, 2) }}</pre>
                    </div>
                    <div v-if="record.request_info.data" class="req-kv-block">
                      <span class="req-kv-label">Form Data</span>
                      <pre class="log-json">{{ JSON.stringify(record.request_info.data, null, 2) }}</pre>
                    </div>
                  </div>

                  <!-- 响应信息 -->
                  <div v-if="!record.ddt && record.status_code" class="log-section">
                    <div class="log-section__title">响应信息</div>
                    <div class="resp-status-line">
                      <span class="resp-status" :class="record.status_code < 300 ? 'status-ok' : record.status_code < 400 ? 'status-rd' : 'status-err'">
                        {{ record.status_code }}
                      </span>
                      <span class="resp-duration">{{ record.duration }}s</span>
                    </div>
                    <div v-if="record.response_body !== null" class="req-kv-block">
                      <span class="req-kv-label">Response Body</span>
                      <pre class="log-json">{{ typeof record.response_body === 'object' ? JSON.stringify(record.response_body, null, 2) : record.response_body }}</pre>
                    </div>
                  </div>

                  <!-- 断言明细 -->
                  <div v-if="record.assertions.length" class="log-section">
                    <div class="log-section__title">断言结果</div>
                    <div v-for="a in record.assertions" :key="a.name"
                      class="assert-result-row" :class="a.pass ? 'apass' : 'afail'">
                      <span class="ar-icon">{{ a.pass ? '✓' : '✗' }}</span>
                      <span class="ar-name">{{ a.name }}</span>
                      <span class="ar-detail">期望 <code>{{ a.expect }}</code> 实际 <code>{{ a.actual }}</code></span>
                      <span v-if="a.msg" class="ar-msg">{{ a.msg }}</span>
                    </div>
                  </div>

                  <!-- 提取变量 -->
                  <div v-if="Object.keys(record.extracted).length" class="log-section">
                    <div class="log-section__title">提取变量</div>
                    <div v-for="(val, key) in record.extracted" :key="key" class="extract-result-row">
                      <code class="er-key">${ {{ key }} }</code>
                      <span class="er-eq">=</span>
                      <code class="er-val">{{ val }}</code>
                    </div>
                  </div>

                  <div v-if="!record.error && !record.assertions.length && !record.ddt" class="log-no-assert">
                    执行完成，未配置断言规则
                  </div>
                </template>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeftOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined,
  ReloadOutlined, ArrowRightOutlined, ApiOutlined, FileTextOutlined,
  DownloadOutlined, CheckCircleOutlined, CodeOutlined,
} from '@ant-design/icons-vue'
import { getCase, deleteCase, getEndpoints, runCaseById, createCase, updateCase } from '@/api/case'
import { getEnvironments } from '@/api/suite'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { getDataSets } from '@/api/dataset'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const caseData = ref(null)
const runEnvironments = ref([])
const selectedRunEnvId = ref(null)
const runDatasets = ref([])
const selectedDatasetId = ref(null)
const activeTab = ref('endpoint')
const endpoints = ref([])

const formData = ref({ name: '', endpoint: null, alluer: '' })

const tabs = computed(() => [
  { key: 'endpoint', label: '关联接口', icon: ApiOutlined, count: caseData.value?.endpoint ? 1 : null },
  { key: 'params',   label: '接口参数', icon: FileTextOutlined, count: paramCount.value },
  { key: 'extract',  label: '数据提取', icon: DownloadOutlined, count: extractRules.value.length || null },
  { key: 'validate', label: '断言规则', icon: CheckCircleOutlined, count: Array.isArray(caseData.value?.validate) ? caseData.value.validate.length : null },
  { key: 'script',   label: '用例脚本', icon: CodeOutlined, count: (caseData.value?.pre_script || caseData.value?.post_script) ? 1 : null },
])

const paramCount = computed(() => {
  const args = parsedApiArgs.value
  if (!args) return null
  let n = 0
  if (args.headers && Object.keys(args.headers).length) n += Object.keys(args.headers).length
  if (args.json    && Object.keys(args.json).length)    n++
  if (args.data    && Object.keys(args.data).length)    n++
  if (args.params  && Object.keys(args.params).length)  n++
  return n || null
})

const plColor = computed(() => {
  const name = caseData.value?.product_line_name || ''
  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899']
  let hash = 0
  for (const c of name) hash = (hash * 31 + c.charCodeAt(0)) & 0xffffffff
  return colors[Math.abs(hash) % colors.length]
})

// api_args 兼容 JSON 字符串和对象
const parsedApiArgs = computed(() => {
  const raw = caseData.value?.api_args
  if (!raw) return null
  if (typeof raw === 'object') return raw
  try { return JSON.parse(raw) } catch { return null }
})

const extractRules = computed(() => {
  const ext = caseData.value?.extract
  if (!ext || typeof ext !== 'object') return []
  return Object.entries(ext).map(([name, rule]) => {
    if (Array.isArray(rule)) return { name, expr: rule[1] ?? '', index: rule[2] ?? 0 }
    return { name, expr: String(rule), index: 0 }
  })
})

// ─── 数据加载 ─────────────────────────────────
const loadCase = async () => {
  try {
    const res = await getCase(route.params.id)
    caseData.value = res.result || res
  } catch (e) {
    console.error('加载用例详情失败:', e)
  } finally {
    loading.value = false
  }
}

const loadRunEnvironments = async () => {
  try {
    const params = { page_size: 200 }
    if (userStore.currentProductLine?.id) params.product_line = userStore.currentProductLine.id
    const r = await getEnvironments(params)
    runEnvironments.value = r.result?.list || []
    if (!selectedRunEnvId.value && runEnvironments.value.length) {
      selectedRunEnvId.value = runEnvironments.value[0].id
    }
    const dsRes = await getDataSets({ page_size: 200 })
    runDatasets.value = dsRes.result?.list || []
  } catch (e) {
    console.error('加载运行环境失败:', e)
  }
}

const handleCreate = async () => {
  if (!formData.value.name.trim()) { alert('用例名称不能为空'); return }
  try {
    const res = await createCase({
      name: formData.value.name,
      endpoint: formData.value.endpoint,
      alluer: formData.value.alluer ? JSON.parse(formData.value.alluer) : null,
      project: null,
      product_line: null,
    })
    const newId = res.result?.id || res.id
    if (newId) router.push(`/cases/${newId}`)
    else router.push('/cases')
  } catch (e) {
    alert('创建失败：' + (e.response?.data?.message || e.message))
  }
}

const editingItem = ref(null)

const handleUpdate = async () => {
  if (!formData.value.name.trim()) { alert('用例名称不能为空'); return }
  try {
    await updateCase(route.params.id, {
      name: formData.value.name,
      endpoint: formData.value.endpoint,
      alluer: formData.value.alluer ? JSON.parse(formData.value.alluer) : null,
    })
    alert('保存成功')
    isEditMode.value = false
    router.push(`/cases/${route.params.id}`)
  } catch (e) {
    alert('保存失败：' + (e.response?.data?.message || e.message))
  }
}

const deleteCaseItem = async () => {
  const confirmed = await confirm('确定要删除这个用例吗？此操作不可恢复。', { type: 'danger' })
  if (!confirmed) return
  try {
    await deleteCase(route.params.id)
    router.push('/cases')
  } catch (e) {
    const msg = e.response?.data?.message || e.response?.data?.detail || '删除失败'
    alert(msg)
  }
}

// ─── 运行日志 ─────────────────────────────────
const runLogs = ref([])
const isRunning = computed(() => runLogs.value.some(r => r.running))
let _logId = 0

const getRunLogKey = () => `case_run_log_${route.params.id}`

const persistRunLogs = () => {
  try {
    const logs = runLogs.value.filter(r => !r.running)
    localStorage.setItem(getRunLogKey(), JSON.stringify(logs))
  } catch (_) {}
}

const loadRunLogs = () => {
  try {
    const raw = localStorage.getItem(getRunLogKey())
    if (!raw) { runLogs.value = []; return }
    const logs = JSON.parse(raw)
    runLogs.value = Array.isArray(logs) ? logs : []
    if (runLogs.value.length) {
      _logId = Math.max(...runLogs.value.map(r => Number(r.id) || 0), 0)
    }
  } catch (_) { runLogs.value = [] }
}

const removeRunLog = (idx) => {
  runLogs.value.splice(idx, 1)
  persistRunLogs()
}

const runCase = async () => {
  const caseId = caseData.value?.id
  if (!caseId) return
  const record = {
    id: ++_logId, running: true, expanded: true, success: null,
    status_code: null, duration: null, request_info: null,
    response_body: null, assertions: [], extracted: {}, error: '',
    report_url: null, time: new Date().toLocaleString('zh-CN'),
  }
  runLogs.value = [record]
  persistRunLogs()
  try {
    const res = await runCaseById(caseId, {
      timeout_seconds: 30,
      environment_id: selectedRunEnvId.value || null,
      dataset_id: selectedDatasetId.value || null,
    })
    if (res.ddt) {
      record.running = false
      record.success = res.failed === 0
      record.ddt = true
      record.ddt_total   = res.total
      record.ddt_passed  = res.passed
      record.ddt_failed  = res.failed
      record.ddt_results = res.results || []
      record.dataset_name = res.dataset_name
    } else {
      const r = res.result || res
      record.running      = false
      record.success     = r.success
      record.status_code = r.status_code
      record.duration    = r.duration
      record.request_info   = r.request_info  || null
      record.response_body   = r.response_body !== undefined ? r.response_body : null
      record.assertions = r.assertions || []
      record.extracted  = r.extracted  || {}
      record.error      = r.error      || ''
    }
    persistRunLogs()
  } catch (e) {
    record.running = false
    record.success = false
    record.error   = e.response?.data?.message || e.message || '运行失败'
    persistRunLogs()
  }
}

const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

onMounted(async () => {
  loading.value = true
  await Promise.all([loadCase(), loadRunEnvironments()])
  loadRunLogs()
})
</script>

<style scoped>
/* ─── 页面容器 ─── */
.case-detail-view {
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
  flex-wrap: wrap;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
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

.btn-back:hover { color: #111827; border-color: #d1d5db; background: #f9fafb; }

/* ─── 运行控制 ─── */
.run-controls { display: flex; align-items: center; gap: 8px; }

.run-select {
  padding: 7px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  background: white;
  color: #374151;
  outline: none;
  cursor: pointer;
  max-width: 200px;
  transition: border-color 0.2s;
}

.run-select:focus { border-color: #3B82F6; }

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

/* ─── 按钮系统 ─── */
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
  white-space: nowrap;
}

.btn--primary {
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
}

.btn--primary:hover {
  background: linear-gradient(135deg, #2563EB 0%, #1d4ed8 100%);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
  transform: translateY(-1px);
}

.btn--primary:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3); }

.btn--success {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
}

.btn--success:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.5);
  transform: translateY(-1px);
}

.btn--success:active { transform: translateY(0); }

.btn--success:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn--danger-ghost {
  background: white;
  color: #ef4444;
  border: 1.5px solid #fecaca;
}

.btn--danger-ghost:hover { background: #fef2f2; border-color: #ef4444; }

.btn--sm { padding: 8px 16px; font-size: 13px; border-radius: 8px; }

/* ─── 表单卡片 ─── */
.form-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  transition: box-shadow 0.3s ease;
}

.form-card:hover { box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08); }
.form-card--no-clip { overflow: visible; }

.form-card__header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 24px 28px 20px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-radius: 16px 16px 0 0;
}

.form-card__title-group { flex: 1; min-width: 0; }

.form-card__title-row {
  display: flex;
  align-items: center;
  gap: 14px;
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
  margin-top: 4px;
}

.form-card__body { padding: 24px 28px; }

/* ─── 信息网格 ─── */
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
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.info-item { display: flex; flex-direction: column; gap: 4px; }

.project-link, .endpoint-link {
  color: #3B82F6;
  cursor: pointer;
  font-weight: 600;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.project-link:hover, .endpoint-link:hover { color: #1d4ed8; }

.pl-badge { display: inline-flex; align-items: center; gap: 8px; }
.pl-badge__dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }

.creator-info { display: flex; align-items: center; gap: 8px; }
.creator-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3B82F6, #8B5CF6);
  color: white;
  font-size: 11px;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* ─── Case ID Badge ─── */
.case-id-badge {
  padding: 3px 10px;
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

/* ─── Allure ─── */
.alluer-block { margin-top: 20px; padding-top: 20px; border-top: 1px solid #f0f0f0; }
.alluer-pre {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px 16px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #374151;
  overflow-x: auto;
  margin: 0;
}

/* ─── Tabs ─── */
.tabs-wrapper { background: white; }

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

.tab-btn:hover { color: #111827; background: #f9fafb; }
.tab-btn--active { color: #3B82F6; border-bottom-color: #3B82F6; font-weight: 700; background: white; }
.tab-btn__icon { font-size: 14px; }
.tab-btn__count {
  background: #eff6ff;
  color: #3B82F6;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 700;
}

.tab-content { padding: 20px 24px; }

/* ─── 关联接口区块 ─── */
.endpoint-detail-block { display: flex; flex-direction: column; gap: 16px; }

.endpoint-header {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.endpoint-name { flex: 1; font-size: 16px; font-weight: 700; color: #111827; }

.endpoint-url-row {
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

.endpoint-url {
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  color: #111827;
  font-weight: 500;
}

/* ─── Method Badge ─── */
.method-badge {
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
}

.m-get    { background: #dbeafe; color: #1d4ed8; }
.m-post   { background: #dcfce7; color: #15803d; }
.m-put    { background: #fef3c7; color: #b45309; }
.m-delete { background: #fee2e2; color: #dc2626; }
.m-patch  { background: #f3e8ff; color: #7c3aed; }

/* ─── 请求参数展示 ─── */
.params-display-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 20px;
}

.param-section {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.param-section--full { grid-column: 1 / -1; }

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

.kv-display-table { overflow: hidden; }

.kv-display-table--4col .kv-display-head,
.kv-display-table--4col .kv-display-row { grid-template-columns: 140px 1fr 80px 160px; }

.kv-display-table--5col .kv-display-head,
.kv-display-table--5col .kv-display-row { grid-template-columns: 36px 1fr 80px 100px 1fr; }

.kv-display-head {
  display: grid;
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
  grid-template-columns: 140px 1fr;
  gap: 8px;
  padding: 8px 14px;
  border-top: 1px solid #f0f0f0;
  transition: background 0.1s;
  align-items: center;
}

.kv-display-row:hover { background: #fafbfc; }

.kv-key { font-size: 12px; font-weight: 700; color: #3B82F6; font-family: 'SF Mono', 'Fira Code', monospace; word-break: break-all; }
.kv-value { font-size: 13px; color: #374151; font-family: 'SF Mono', 'Fira Code', monospace; word-break: break-all; }
.kv-value--green { color: #059669; }
.kv-idx { text-align: center; color: #9CA3AF; font-weight: 700; }
.kv-name { font-weight: 500; color: #111827; font-size: 13px; }
.kv-expr-val { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.kv-expr { font-family: 'SF Mono', monospace; font-size: 12px; color: #059669; }
.kv-arrow { color: #9CA3AF; }
.kv-expect { font-family: 'SF Mono', monospace; font-size: 12px; color: #1d4ed8; }

/* JSON 展示 */
.json-display {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 16px 20px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

/* ─── 数据提取 ─── */
.extract-display { display: flex; flex-direction: column; gap: 12px; }
.extract-display__header { font-size: 13px; color: #6b7280; }
.extract-display__header strong { color: #111827; }

.var-ref {
  background: #fffbeb;
  color: #92400e;
  padding: 2px 8px;
  border-radius: 5px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 12px;
}

/* ─── 断言展示 ─── */
.assert-display { display: flex; flex-direction: column; gap: 12px; }
.assert-display__header { font-size: 13px; color: #6b7280; }
.assert-display__header strong { color: #111827; }

.type-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.type-eq           { background: #dbeafe; color: #1d4ed8; }
.type-not_eq       { background: #fff3e0; color: #b45309; }
.type-contains     { background: #f3e8ff; color: #6c3aed; }
.type-not_contains { background: #fce7f3; color: #9d174d; }
.type-exists       { background: #dcfce7; color: #15803d; }
.type-regex        { background: #ecfdf5; color: #065f46; }

.source-badge {
  background: #f3f4f6;
  color: #4b5563;
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 11px;
  font-family: 'SF Mono', 'Fira Code', monospace;
}

.legacy-json {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 16px 20px;
  border-radius: 10px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.6;
  overflow-x: auto;
  margin: 0;
}

/* ─── 脚本展示 ─── */
.script-display { display: flex; flex-direction: column; gap: 20px; }

.script-block { border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; }

.script-block__header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.script-block__title { font-size: 13px; font-weight: 600; color: #374151; }

.script-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 5px;
  font-size: 11px;
  font-weight: 700;
}

.script-badge--pre  { background: #dbeafe; color: #1d4ed8; }
.script-badge--post { background: #d1fae5; color: #065f46; }

.script-pre {
  background: #0f172a;
  color: #e2e8f0;
  padding: 16px 20px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
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

.empty-tab__icon { font-size: 32px; color: #d1d5db; }

/* ─── 执行日志面板 ─── */
.run-log-panel {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

.log-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px;
  background: linear-gradient(180deg, #fafbfc 0%, white 100%);
  border-bottom: 1px solid #f0f0f0;
}

.log-panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 700;
  color: #111827;
}

.log-panel-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.dot-running { background: #f59e0b; animation: pulse 1.2s ease-in-out infinite; }
.dot-idle    { background: #10B981; }

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

.log-panel-count {
  background: #f3f4f6;
  color: #6b7280;
  border-radius: 10px;
  padding: 1px 8px;
  font-size: 11px;
  font-weight: 600;
}

.log-list { display: flex; flex-direction: column; gap: 2px; padding: 12px; }

.log-record {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.log-record.expanded { box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); }

.log-record-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: #f9fafb;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
  flex-wrap: wrap;
}

.log-record-head:hover { background: #f3f4f6; }

.log-expand-icon { color: #9CA3AF; font-size: 12px; width: 12px; flex-shrink: 0; }
.log-record-index { font-family: 'SF Mono', monospace; font-size: 12px; color: #3B82F6; font-weight: 700; min-width: 28px; }

.log-running-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: #fffbeb;
  color: #b45309;
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid #fcd34d44;
}

.pass-badge, .fail-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 700;
}

.pass-badge { background: #dcfce7; color: #15803d; }
.fail-badge { background: #fee2e2; color: #dc2626; }

.log-meta { font-size: 12px; color: #9CA3AF; margin-left: 2px; }
.log-record-time { font-size: 11px; color: #9CA3AF; margin-left: auto; }

.log-del-btn {
  background: none;
  border: none;
  color: #d1d5db;
  cursor: pointer;
  font-size: 14px;
  padding: 2px 6px;
  border-radius: 6px;
  transition: all 0.15s;
  display: inline-flex;
  align-items: center;
}

.log-del-btn:hover { color: #ef4444; background: #fef2f2; }

.log-record-body { padding: 12px 14px 14px 36px; background: #0d1117; }

/* DDT */
.ddt-summary { padding: 10px 0; }
.ddt-header { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; flex-wrap: wrap; }
.ddt-title { font-size: 13px; font-weight: 600; color: #58a6ff; }
.ddt-stat { font-size: 12px; padding: 2px 8px; border-radius: 10px; font-weight: 600; }
.ddt-stat.pass  { background: #1a3a2a; color: #3fb950; }
.ddt-stat.fail  { background: #3a1a1a; color: #f85149; }
.ddt-stat.total { background: #1c2128; color: #8b949e; }

.ddt-row-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  margin-bottom: 4px;
  font-size: 12px;
  flex-wrap: wrap;
}

.ddt-pass { background: #0d1f12; border: 1px solid #1a3a2a; }
.ddt-fail { background: #1f0d0d; border: 1px solid #3a1a1a; }

.ddt-row-idx  { color: #8b949e; min-width: 48px; }
.ddt-row-badge { font-weight: 700; min-width: 16px; }
.ddt-pass .ddt-row-badge { color: #3fb950; }
.ddt-fail .ddt-row-badge { color: #f85149; }
.ddt-row-params { color: #c9d1d9; font-family: monospace; flex: 1; word-break: break-all; }
.ddt-row-code { color: #79c0ff; background: #1c2128; padding: 1px 6px; border-radius: 4px; }
.ddt-row-dur  { color: #8b949e; }
.ddt-row-err  { color: #f85149; font-style: italic; }

/* 日志内容 */
.log-error-msg { color: #f85149; font-size: 12px; font-family: 'SF Mono', monospace; padding: 6px 0 0; }

.log-section { margin: 8px 0 4px; }
.log-section__title {
  font-size: 11px;
  font-weight: 700;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 8px;
  display: block;
}

.req-line { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }

.req-method {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
  flex-shrink: 0;
}

.m-get    { background: #0d2018; color: #3fb950; }
.m-post   { background: #2d1a00; color: #f0883e; }
.m-put    { background: #0d1f3c; color: #58a6ff; }
.m-patch  { background: #1a0d2d; color: #d2a8ff; }
.m-delete { background: #2d1114; color: #f85149; }

.req-url {
  font-family: 'SF Mono', monospace;
  font-size: 12px;
  color: #c9d1d9;
  background: #161b22;
  padding: 3px 10px;
  border-radius: 6px;
  word-break: break-all;
}

.req-kv-block { margin-bottom: 8px; }

.req-kv-label {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 4px;
}

.log-json {
  margin: 0;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 11px;
  line-height: 1.6;
  color: #adbac7;
  background: #161b22;
  border: 1px solid #21262d;
  border-radius: 6px;
  padding: 8px 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}

.resp-status-line { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }

.resp-status {
  display: inline-block;
  padding: 3px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 700;
  font-family: 'SF Mono', monospace;
}

.status-ok  { background: #0d2018; color: #3fb950; }
.status-rd  { background: #1a1a00; color: #e3b341; }
.status-err { background: #2d1114; color: #f85149; }
.resp-duration { font-size: 12px; color: #8b949e; }

/* 断言结果 */
.assert-result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 12px;
  margin-bottom: 3px;
  flex-wrap: wrap;
}

.apass { background: #0d2018; }
.afail { background: #2d1114; }

.ar-icon { font-weight: 700; width: 16px; flex-shrink: 0; text-align: center; }
.apass .ar-icon { color: #3fb950; }
.afail .ar-icon { color: #f85149; }
.ar-name { font-weight: 500; color: #e6edf3; flex: 1; }
.ar-detail { font-size: 11px; color: #8b949e; }
.ar-detail code { background: #21262d; padding: 1px 5px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #79c0ff; }
.ar-msg { font-size: 11px; color: #f85149; }

/* 提取变量 */
.extract-result-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  font-size: 12px;
  border-radius: 6px;
  background: #1a1040;
  margin-bottom: 4px;
}

.er-key { background: #2d1b69; color: #d2a8ff; padding: 1px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; }
.er-eq { color: #8b949e; }
.er-val { background: #0d2018; color: #3fb950; padding: 1px 8px; border-radius: 4px; font-family: monospace; font-size: 12px; }

.log-no-assert { font-size: 12px; color: #8b949e; padding: 6px 0; }
.log-running-hint { display: flex; align-items: center; gap: 8px; color: #f0883e; font-size: 13px; padding: 8px 0; }

.mini-spinner, .spinner-sm {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(245, 158, 11, 0.3);
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.spinner-sm { width: 14px; height: 14px; border-width: 2px; vertical-align: middle; }

@keyframes spin { to { transform: rotate(360deg); } }

/* 动画过渡 */
.logpanel-enter-active, .logpanel-leave-active { transition: all 0.3s ease; }
.logpanel-enter-from, .logpanel-leave-to { opacity: 0; transform: translateY(16px); }
</style>
