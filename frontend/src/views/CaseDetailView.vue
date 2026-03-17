<template>
  <div class="case-detail">
    <!-- 详情模式 -->
    <template v-if="!editMode">
      <div class="detail-header">
        <button @click="$router.back()" class="btn btn-back">← 返回</button>
        <div class="header-actions">
          <button @click="enterEdit" class="btn btn-primary">编辑用例</button>
          <button @click="runCase" class="btn btn-success">运行用例</button>
          <button @click="deleteCaseItem" class="btn btn-danger">删除用例</button>
        </div>
      </div>

      <div v-if="caseData" class="info-card card">
        <h2>{{ caseData.name }}</h2>
        <div class="info-grid">
          <div class="info-item"><label>用例ID</label><span>{{ caseData.id }}</span></div>
          <div class="info-item"><label>所属项目</label><span>{{ caseData.project_name || `项目 #${caseData.project}` }}</span></div>
          <div class="info-item"><label>关联接口</label><span>{{ caseData.endpoint?.name || '-' }}</span></div>
          <div class="info-item"><label>创建时间</label><span>{{ formatDate(caseData.created_at) }}</span></div>
        </div>

        <div class="params-section">
          <!-- 关联接口信息（只读） -->
          <div v-if="caseData.endpoint" class="param-block endpoint-block">
            <h4><span class="block-icon">🔗</span> 关联接口</h4>
            <div class="endpoint-info-grid">
              <div class="endpoint-info-row">
                <span class="ep-label">名称</span>
                <span class="ep-value">
                  <a @click.prevent="router.push(`/endpoints/${caseData.endpoint.id}`)" class="ep-link">{{ caseData.endpoint.name }} ↗</a>
                </span>
              </div>
              <div class="endpoint-info-row">
                <span class="ep-label">请求方式</span>
                <span class="ep-method" :class="'method-' + (caseData.endpoint.method || '').toLowerCase()">{{ caseData.endpoint.method }}</span>
              </div>
              <div class="endpoint-info-row">
                <span class="ep-label">URL</span>
                <code class="ep-url">{{ caseData.endpoint.url }}</code>
              </div>
              <div v-if="caseData.endpoint.headers && Object.keys(caseData.endpoint.headers).length" class="endpoint-info-row">
                <span class="ep-label">请求头</span>
                <pre class="ep-json">{{ JSON.stringify(caseData.endpoint.headers, null, 2) }}</pre>
              </div>
              <div v-if="caseData.endpoint.params && Object.keys(caseData.endpoint.params).length" class="endpoint-info-row">
                <span class="ep-label">Query 参数</span>
                <pre class="ep-json">{{ JSON.stringify(caseData.endpoint.params, null, 2) }}</pre>
              </div>
              <div v-if="caseData.endpoint.json && Object.keys(caseData.endpoint.json).length" class="endpoint-info-row">
                <span class="ep-label">JSON Body</span>
                <pre class="ep-json">{{ JSON.stringify(caseData.endpoint.json, null, 2) }}</pre>
              </div>
              <div v-if="caseData.endpoint.data && Object.keys(caseData.endpoint.data).length" class="endpoint-info-row">
                <span class="ep-label">Form Data</span>
                <pre class="ep-json">{{ JSON.stringify(caseData.endpoint.data, null, 2) }}</pre>
              </div>
              <div v-if="caseData.endpoint.cookies && Object.keys(caseData.endpoint.cookies).length" class="endpoint-info-row">
                <span class="ep-label">Cookies</span>
                <pre class="ep-json">{{ JSON.stringify(caseData.endpoint.cookies, null, 2) }}</pre>
              </div>
            </div>
          </div>

          <div v-if="caseData.alluer" class="param-block">
            <h4>Allure 标注</h4>
            <pre>{{ JSON.stringify(caseData.alluer, null, 2) }}</pre>
          </div>
          <div v-if="caseData.api_args" class="param-block">
            <h4>接口参数</h4>
            <pre v-if="apiArgsBody">{{ JSON.stringify(apiArgsBody, null, 2) }}</pre>
            <div v-else class="empty-hint">未配置接口参数</div>
          </div>
          <div class="param-block extract-block">
            <h4><span class="block-icon">⬇</span> 数据提取 <span class="block-hint">执行后从响应中提取变量</span></h4>
            <div v-if="extractRules.length" class="extract-table">
              <div class="extract-row extract-header">
                <span>变量名</span><span>JSONPath 表达式</span><span>取第几个</span><span>引用方式</span>
              </div>
              <div v-for="rule in extractRules" :key="rule.name" class="extract-row">
                <span class="var-name">{{ rule.name }}</span>
                <span class="var-expr">{{ rule.expr }}</span>
                <span class="var-index">{{ rule.index }}</span>
                <span class="var-ref"><code>${{ '{' }}{{ rule.name }}{{ '}' }}</code></span>
              </div>
            </div>
            <div v-else class="empty-hint">未配置数据提取</div>
          </div>
          <div v-if="caseData.validate" class="param-block assert-block">
            <h4><span class="block-icon">✓</span> 断言规则 <span class="block-hint">共 {{ (Array.isArray(caseData.validate) ? caseData.validate : []).length }} 条</span></h4>
            <div v-if="Array.isArray(caseData.validate) && caseData.validate.length" class="assert-view-table">
              <div class="assert-view-header">
                <span>#</span><span>断言描述</span><span>类型</span><span>来源</span><span>表达式</span><span>期望值</span>
              </div>
              <div v-for="(rule, idx) in caseData.validate" :key="idx" class="assert-view-row">
                <span class="av-idx">{{ idx + 1 }}</span>
                <span class="av-name">{{ rule.name }}</span>
                <span><code class="av-type" :class="'type-' + rule.type">{{ rule.type }}</code></span>
                <span><code class="av-source">{{ rule.source }}</code></span>
                <span class="av-expr">{{ rule.expr || '-' }}</span>
                <span class="av-expect">{{ rule.type === 'exists' ? '(存在即通过)' : rule.expect }}</span>
              </div>
            </div>
            <pre v-else class="assert-legacy-pre">{{ JSON.stringify(caseData.validate, null, 2) }}</pre>
          </div>
        </div>

        <!-- 执行日志区块 -->
        <div v-if="runLogs.length" ref="logPanelRef" class="param-block run-log-block">
          <h4>
            <span class="log-panel-dot" :class="isRunning ? 'dot-running' : 'dot-idle'"></span>
            执行日志
            <span class="block-hint">共 {{ runLogs.length }} 条记录</span>
            <button class="log-clear-btn" @click="runLogs = []">✕ 清空</button>
          </h4>
          <div class="log-list">
            <div v-for="(record, idx) in runLogs" :key="record.id" class="log-record">
              <div class="log-record-head" @click="record.expanded = !record.expanded">
                <span class="log-expand-icon">{{ record.expanded ? '▾' : '▸' }}</span>
                <span class="log-record-index">#{{ runLogs.length - idx }}</span>
                <span v-if="record.running" class="log-running-badge">
                  <span class="mini-spinner"></span> 运行中
                </span>
                <span v-else :class="record.returncode === 0 ? 'pass-badge' : 'fail-badge'">
                  {{ record.returncode === 0 ? '✓ 通过' : '✗ 失败' }}
                </span>
                <span class="log-record-time">{{ record.time }}</span>
                <span v-if="record.report_url" class="log-report-link" @click.stop>
                  <a :href="record.report_url" target="_blank">📊 报告</a>
                </span>
                <button class="log-del-btn" @click.stop="runLogs.splice(idx, 1)" title="删除">🗑</button>
              </div>
              <div v-if="record.expanded" class="log-record-body">
                <div v-if="record.running" class="log-running-hint">
                  <span class="spinner-sm"></span> 正在执行，请稍候...
                </div>
                <pre v-else class="log-pre">{{ record.stdout || '（无输出）' }}</pre>
                <div v-if="record.error" class="log-error-msg">{{ record.error }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 编辑模式（全屏 Tab 页）-->
    <template v-else>
      <div class="edit-header">
        <div class="edit-title">
          <button @click="cancelEdit" class="btn btn-back">← 取消</button>
          <span class="edit-label">编辑用例：{{ caseData?.name }}</span>
        </div>
        <button @click="handleSubmit" class="btn btn-primary">保存</button>
      </div>

      <div class="edit-body card">
        <!-- Tab 导航 -->
        <div class="tab-nav">
          <button
            v-for="tab in tabs" :key="tab.key"
            class="tab-btn" :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >{{ tab.label }}</button>
        </div>

        <div class="tab-content">
          <!-- Tab 1: 基本信息 -->
          <div v-show="activeTab === 'basic'">
            <div class="form-group">
              <label>用例名称 *</label>
              <input v-model="formData.name" required placeholder="用例名称" />
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>所属项目 *</label>
                <select v-model="formData.project" required>
                  <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
                </select>
              </div>
              <div class="form-group">
                <label>关联接口 *</label>
                <select v-model="formData.endpoint" required>
                  <option v-for="e in endpoints" :key="e.id" :value="e.id">{{ e.name }}</option>
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
                <div class="param-hint">发送 <code>application/json</code>，值可用 <code>${变量名}</code></div>
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
                <div class="param-hint">发送 <code>application/x-www-form-urlencoded</code>，值可用 <code>${变量名}</code></div>
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
                <div class="param-hint">附加到 URL 的查询参数，值可用 <code>${变量名}</code></div>
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
                <div class="param-hint">完整 api_args JSON，手动填写（高级用法）</div>
                <textarea v-model="formData.api_args" rows="8" placeholder='{"json":{"key":"value"}}'></textarea>
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
                <span>变量名</span>
                <span>JSONPath 表达式（如 $.data.token）</span>
                <span class="col-index">取第几个</span>
                <span></span>
              </div>
              <div v-for="(rule, idx) in editExtractRules" :key="idx" class="extract-editor-row">
                <input v-model="rule.name" placeholder="token" class="rule-input" />
                <input v-model="rule.expr" placeholder="$.data.token" class="rule-input" />
                <input v-model.number="rule.index" type="number" min="0" placeholder="0" class="rule-input rule-index" title="有多个匹配时取第几个（从0开始）" />
                <button type="button" class="btn-remove-rule" @click="removeExtractRule(idx)">✕</button>
              </div>
            </div>
            <div v-else class="empty-hint" style="padding: 24px 0">暂无提取规则，点击「+ 添加规则」新增</div>
          </div>

          <!-- Tab 4: 断言 -->
          <div v-show="activeTab === 'validate'">
            <div class="assert-tip">
              按顺序执行所有断言规则，支持状态码、JSONPath、响应文本等来源。
            </div>
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
                <!-- 序号 -->
                <span class="assert-idx">{{ idx + 1 }}</span>

                <!-- 断言描述 -->
                <input v-model="rule.name" placeholder="断言描述" class="assert-input assert-name" />

                <!-- 断言类型 -->
                <select v-model="rule.type" class="assert-select assert-type">
                  <option value="eq">等于 (eq)</option>
                  <option value="not_eq">不等于 (not_eq)</option>
                  <option value="contains">包含 (contains)</option>
                  <option value="not_contains">不包含 (not_contains)</option>
                  <option value="exists">存在 (exists)</option>
                  <option value="regex">正则匹配 (regex)</option>
                </select>

                <!-- 来源 -->
                <select v-model="rule.source" class="assert-select assert-source">
                  <option value="status_code">状态码</option>
                  <option value="jsonpath">JSONPath</option>
                  <option value="text">响应文本</option>
                </select>

                <!-- 表达式（source!=status_code 时显示） -->
                <input
                  v-if="rule.source !== 'status_code'"
                  v-model="rule.expr"
                  :placeholder="rule.source === 'jsonpath' ? '$.data.code' : '正则表达式'"
                  class="assert-input assert-expr"
                />
                <span v-else class="assert-expr-placeholder">HTTP 状态码</span>

                <!-- 期望值（exists 不需要） -->
                <input
                  v-if="rule.type !== 'exists'"
                  v-model="rule.expect"
                  placeholder="期望值"
                  class="assert-input assert-expect"
                />
                <span v-else class="assert-expr-placeholder assert-exists-hint">值存在且非空即通过</span>

                <!-- 删除 -->
                <button type="button" class="btn-remove-rule" @click="editAssertRules.splice(idx, 1)">✕</button>
              </div>
            </div>
            <div v-else class="empty-hint" style="padding: 24px 0">
              暂无断言规则，点击上方按钮添加
            </div>

            <!-- 预览 -->
            <div v-if="editAssertRules.length" class="assert-preview">
              <span class="assert-preview-label">JSON 预览</span>
              <pre class="assert-preview-code">{{ JSON.stringify(buildAssertList(), null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
    </template>
    <!-- 底部日志面板 -->
    <transition name="logpanel">
      <div v-if="runLogs.length" class="run-log-panel">
        <div class="log-panel-header">
          <span class="log-panel-title">
            <span class="log-panel-dot" :class="isRunning ? 'dot-running' : 'dot-idle'"></span>
            执行日志
            <span class="log-panel-count">{{ runLogs.length }} 条记录</span>
          </span>
          <button class="log-panel-close" @click="runLogs = []">✕ 清空</button>
        </div>
        <div class="log-list">
          <div v-for="(record, idx) in runLogs" :key="record.id" class="log-record" :class="{ expanded: record.expanded }">
            <!-- 记录行头 -->
            <div class="log-record-head" @click="record.expanded = !record.expanded">
              <span class="log-expand-icon">{{ record.expanded ? '▾' : '▸' }}</span>
              <span class="log-record-index">#{{ runLogs.length - idx }}</span>
              <span v-if="record.running" class="log-running-badge">
                <span class="mini-spinner"></span> 运行中
              </span>
              <span v-else :class="record.success ? 'pass-badge' : 'fail-badge'">
                {{ record.success ? '✓ 通过' : '✗ 失败' }}
              </span>
              <span v-if="!record.running && record.status_code" class="log-meta">状态码 {{ record.status_code }}</span>
              <span v-if="!record.running && record.duration" class="log-meta">{{ record.duration }}s</span>
              <span class="log-record-time">{{ record.time }}</span>
              <button class="log-del-btn" @click.stop="runLogs.splice(idx, 1)" title="删除">🗑</button>
            </div>
            <!-- 展开的详情 -->
            <div v-if="record.expanded" class="log-record-body">
              <div v-if="record.running" class="log-running-hint">
                <span class="spinner-sm"></span> 正在执行，请稍候...
              </div>
              <template v-else>
                <!-- 错误信息 -->
                <div v-if="record.error" class="log-error-msg">⚠ {{ record.error }}</div>
                <!-- 断言明细 -->
                <div v-if="record.assertions.length" class="log-section">
                  <div class="log-section-title">断言明细</div>
                  <div v-for="a in record.assertions" :key="a.name" class="assert-result-row" :class="a.pass ? 'apass' : 'afail'">
                    <span class="ar-icon">{{ a.pass ? '✓' : '✗' }}</span>
                    <span class="ar-name">{{ a.name }}</span>
                    <span class="ar-detail">期望 <code>{{ a.expect }}</code> 实际 <code>{{ a.actual }}</code></span>
                    <span v-if="a.msg" class="ar-msg">{{ a.msg }}</span>
                  </div>
                </div>
                <!-- 提取变量 -->
                <div v-if="Object.keys(record.extracted).length" class="log-section">
                  <div class="log-section-title">提取变量</div>
                  <div v-for="(val, key) in record.extracted" :key="key" class="extract-result-row">
                    <code class="er-key">{{ '${'  + key + '}' }}</code>
                    <span class="er-eq">=</span>
                    <code class="er-val">{{ val }}</code>
                  </div>
                </div>
                <!-- 无断言无错误时提示 -->
                <div v-if="!record.error && !record.assertions.length" class="log-no-assert">
                  执行完成，未配置断言规则
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCase, updateCase, deleteCase, getEndpoints, runCaseById } from '@/api/case'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'

const route = useRoute()
const router = useRouter()

const caseData = ref(null)
const projects = ref([])
const endpoints = ref([])
const editMode = ref(false)
const activeTab = ref('basic')

const tabs = [
  { key: 'basic',    label: '基本信息' },
  { key: 'params',   label: '接口参数' },
  { key: 'extract',  label: '数据提取' },
  { key: 'validate', label: '断言规则' },
]

const formData = ref({
  name: '', project: null, endpoint: null,
  alluer: '', api_args: '', validate: '',
  paramType: 'json', jsonRows: [], formRows: [], queryRows: []
})

// kv 行 <-> 对象 互转
const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}
const objToRows = (obj) =>
  obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []

const buildApiArgs = () => {
  if (formData.value.paramType === 'raw')
    return formData.value.api_args ? JSON.parse(formData.value.api_args) : null
  const obj = {}
  if (formData.value.paramType === 'json') { const d = rowsToObj(formData.value.jsonRows);  if (d) obj.json   = d }
  if (formData.value.paramType === 'form') { const d = rowsToObj(formData.value.formRows);  if (d) obj.data   = d }
  if (formData.value.paramType === 'query'){ const d = rowsToObj(formData.value.queryRows); if (d) obj.params = d }
  return Object.keys(obj).length ? obj : null
}

const parseApiArgs = (api_args) => {
  if (!api_args) return { paramType: 'json', jsonRows: [], formRows: [], queryRows: [], api_args: '' }
  if (api_args.json)   return { paramType: 'json',  jsonRows: objToRows(api_args.json),    formRows: [], queryRows: [], api_args: '' }
  if (api_args.data)   return { paramType: 'form',  formRows: objToRows(api_args.data),    jsonRows: [], queryRows: [], api_args: '' }
  if (api_args.params) return { paramType: 'query', queryRows: objToRows(api_args.params), jsonRows: [], formRows: [],  api_args: '' }
  return { paramType: 'raw', api_args: JSON.stringify(api_args, null, 2), jsonRows: [], formRows: [], queryRows: [] }
}

// api_args 中除 headers 之外的参数部分（用于只读展示，兼容旧数据）
const apiArgsBody = computed(() => {
  const args = caseData.value?.api_args
  if (!args || typeof args !== 'object') return null
  const { headers, ...rest } = args
  return Object.keys(rest).length ? rest : null
})

const extractRules = computed(() => {
  const ext = caseData.value?.extract
  if (!ext || typeof ext !== 'object') return []
  return Object.entries(ext).map(([name, rule]) => {
    if (Array.isArray(rule)) return { name, expr: rule[1] ?? '', index: rule[2] ?? 0 }
    return { name, expr: String(rule), index: 0 }
  })
})

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

// validate 数据 -> 编辑行
const parseAssertList = (validate) => {
  if (!validate) return []
  // 新格式：list
  if (Array.isArray(validate)) {
    return validate.map(r => ({
      name:   r.name   || '',
      type:   r.type   || 'eq',
      source: r.source || 'jsonpath',
      expr:   r.expr   || '',
      expect: r.expect != null ? String(r.expect) : '',
    }))
  }
  // 旧格式：dict，转为新行（尽力解析）
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
        rows.push({ name: desc, type: k === 'equals' ? 'eq' : k === 'not_equals' ? 'not_eq' : k,
                    source: 'jsonpath', expr, expect: String(expected) })
      }
    }
  }
  return rows
}

const loadCase = async () => {
  try {
    const res = await getCase(route.params.id)
    caseData.value = res.result
    const c = caseData.value
    const parsed = parseApiArgs(c.api_args)
    formData.value = {
      name:     c.name,
      project:  c.project,
      endpoint: c.endpoint?.id || c.endpoint,
      alluer:   c.alluer   ? JSON.stringify(c.alluer,   null, 2) : '',
      ...parsed
    }
    editExtractRules.value = c.extract
      ? Object.entries(c.extract).map(([name, rule]) =>
          Array.isArray(rule)
            ? { name, expr: rule[1] ?? '', index: rule[2] ?? 0 }
            : { name, expr: String(rule), index: 0 }
        )
      : []
    editAssertRules.value = parseAssertList(c.validate)
  } catch (e) { console.error('加载用例详情失败:', e) }
}

const loadProjects = async () => {
  try { const r = await getProjects({ page_size: 100 }); projects.value = r.result?.list || [] }
  catch (e) { console.error(e) }
}
const loadEndpoints = async () => {
  try { const r = await getEndpoints({ page_size: 100 }); endpoints.value = r.result?.list || [] }
  catch (e) { console.error(e) }
}

const enterEdit = () => { activeTab.value = 'basic'; editMode.value = true }
const cancelEdit = () => { editMode.value = false }

const handleSubmit = async () => {
  try {
    const api_args = buildApiArgs()
    const assertList = buildAssertList()
    const data = {
      name:     formData.value.name,
      project:  formData.value.project,
      endpoint: formData.value.endpoint,
      alluer:   formData.value.alluer ? JSON.parse(formData.value.alluer) : null,
      api_args,
      extract:  buildExtractObj(),
      validate: assertList.length ? assertList : null,
    }
    await updateCase(route.params.id, data)
    editMode.value = false
    loadCase()
  } catch (e) {
    console.error('更新失败:', e)
    alert('保存失败，请检查格式是否正确')
  }
}

const deleteCaseItem = async () => {
  const confirmed = await confirm('确定要删除这个用例吗？', { type: 'danger' })
  if (confirmed) {
    try { await deleteCase(route.params.id); router.push('/cases') }
    catch (e) { console.error('删除失败:', e) }
  }
}

// ---- 运行日志面板 ----
const runLogs = ref([])  // 最新在最前
const isRunning = computed(() => runLogs.value.some(r => r.running))
const logPanelRef = ref(null)
let _logId = 0

const runCase = async () => {
  const caseId = caseData.value?.id
  if (!caseId) return
  const record = {
    id: ++_logId,
    running: true,
    expanded: true,
    success: null,
    status_code: null,
    duration: null,
    assertions: [],
    extracted: {},
    error: '',
    report_url: null,
    time: new Date().toLocaleString('zh-CN'),
  }
  runLogs.value.unshift(record)
  await nextTick()
  logPanelRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  try {
    const res = await runCaseById(caseId)
    const r = res.result || res
    record.running     = false
    record.success     = r.success
    record.status_code = r.status_code
    record.duration    = r.duration
    record.assertions  = r.assertions  || []
    record.extracted   = r.extracted   || {}
    record.error       = r.error       || ''
  } catch (e) {
    record.running = false
    record.success = false
    record.error   = e.response?.data?.message || e.message || '运行失败'
  }
}
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'

onMounted(() => { loadCase(); loadProjects(); loadEndpoints() })
</script>

<style scoped>
.detail-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.header-actions { display: flex; gap: 12px; }
.btn-back { background: white; border: 1px solid var(--border); color: var(--text); }
.btn-success { background: #27ae60; color: white; }
.btn-success:hover { background: #229954; }

.info-card { margin-bottom: 32px; }
.info-card h2 { font-size: 26px; font-weight: 700; margin-bottom: 24px; color: var(--primary); }
.info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap: 20px; margin-bottom: 24px; }
.info-item { display: flex; flex-direction: column; gap: 6px; }
.info-item label { font-size: 12px; color: var(--text-light); font-weight: 500; }
.info-item span  { font-size: 14px; color: var(--text); }
.params-section { display: grid; gap: 14px; }
.param-block h4 { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text); display: flex; align-items: center; gap: 8px; }
.param-block pre { background: var(--bg); padding: 14px; border-radius: 8px; font-family: 'Monaco','Courier New',monospace; font-size: 13px; line-height: 1.6; overflow-x: auto; color: var(--text); }

.edit-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.edit-title { display: flex; align-items: center; gap: 14px; }
.edit-label { font-size: 16px; font-weight: 600; color: var(--text); }

.edit-body { padding: 0; overflow: hidden; }
.tab-nav { display: flex; border-bottom: 2px solid var(--border); padding: 0 24px; gap: 4px; background: #fafafa; }
.tab-btn { padding: 14px 22px; border: none; background: none; font-size: 14px; font-weight: 500; color: var(--text-light); cursor: pointer; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: color .2s, border-color .2s; }
.tab-btn:hover { color: var(--primary); }
.tab-btn.active { color: var(--primary); border-bottom-color: var(--primary); font-weight: 600; }
.tab-content { padding: 28px 28px 20px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; margin-bottom: 8px; font-weight: 500; color: var(--text); }
.form-group input, .form-group select, .form-group textarea { width: 100%; box-sizing: border-box; }
.field-hint { font-size: 12px; font-weight: 400; color: var(--text-light); margin-left: 6px; }
.field-hint code { background: #fff3e0; color: #e65100; padding: 1px 5px; border-radius: 4px; font-size: 11px; }

.extract-block { border: 1px solid #e3f2fd; border-radius: 10px; padding: 16px; background: #f8fcff; }
.block-icon { color: #3498db; }
.block-hint { font-size: 12px; font-weight: 400; color: var(--text-light); }
.extract-table { border-radius: 8px; overflow: hidden; border: 1px solid #d0e8f8; }
.extract-row { display: grid; grid-template-columns: 130px 1fr 80px 140px; }
.extract-header { background: #e3f2fd; font-size: 12px; font-weight: 600; color: #1565c0; }
.extract-header span, .extract-row span { padding: 8px 14px; border-right: 1px solid #d0e8f8; }
.extract-header span:last-child, .extract-row span:last-child { border-right: none; }
.extract-row:not(.extract-header) { background: white; border-top: 1px solid #e8f4fd; font-size: 13px; }
.extract-row:not(.extract-header):hover { background: #f0f8ff; }
.var-name { font-family: 'Monaco','Courier New',monospace; color: #1565c0; font-weight: 600; }
.var-expr { font-family: 'Monaco','Courier New',monospace; color: #2e7d32; }
.var-index { text-align: center; color: #7b1fa2; font-family: 'Monaco','Courier New',monospace; font-size: 13px; }
.var-ref code { background: #fff3e0; color: #e65100; padding: 2px 7px; border-radius: 4px; font-family: 'Monaco','Courier New',monospace; font-size: 12px; }
.empty-hint { color: var(--text-light); font-size: 13px; padding: 6px 0; }

.extract-tip { background: #f0f8ff; border-left: 3px solid #3498db; padding: 10px 14px; border-radius: 4px; font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.extract-tip code { background: #fff3e0; color: #e65100; padding: 1px 5px; border-radius: 4px; font-size: 12px; }
.extract-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
.extract-count { font-size: 13px; color: var(--text-light); }
.btn-add-rule { font-size: 13px; padding: 6px 16px; border: 1px solid #3498db; color: #3498db; background: white; border-radius: 6px; cursor: pointer; }
.btn-add-rule:hover { background: #e3f2fd; }
.extract-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; }
.extract-editor-header { display: grid; grid-template-columns: 160px 1fr 80px 36px; background: #e3f2fd; font-size: 12px; font-weight: 600; color: #1565c0; padding: 8px 12px; gap: 8px; }
.extract-editor-row { display: grid; grid-template-columns: 160px 1fr 80px 36px; gap: 8px; padding: 8px 12px; border-top: 1px solid #e8f4fd; align-items: center; background: white; }
.extract-editor-row:hover { background: #f8fcff; }
.rule-input { border: 1px solid #d0e8f8; border-radius: 4px; padding: 5px 8px; font-size: 13px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; }
.rule-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.15); }
.rule-index { text-align: center; font-family: inherit; }
.col-index { text-align: center; }
.btn-remove-rule { border: none; background: none; color: #e74c3c; cursor: pointer; font-size: 15px; padding: 2px 4px; border-radius: 4px; }
.btn-remove-rule:hover { background: #fdecea; }

/* ===== 断言编辑器 ===== */
.assert-tip { background: #f0faf4; border-left: 3px solid #27ae60; padding: 10px 14px; border-radius: 4px; font-size: 13px; color: var(--text-light); margin-bottom: 16px; }
.assert-label-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
.assert-count { font-size: 13px; color: var(--text-light); }
.assert-add-btns { display: flex; gap: 8px; }
.btn-add-assert { font-size: 12px; padding: 5px 14px; border: 1px solid #27ae60; color: #27ae60; background: white; border-radius: 6px; cursor: pointer; transition: all .18s; }
.btn-add-assert:hover { background: #e8f5e9; }

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

/* ===== 只读断言表格 ===== */
.assert-block { border: 1px solid #d5e8d4; border-radius: 10px; padding: 16px; background: #f6fdf6; }
.assert-view-table { border: 1px solid #d5e8d4; border-radius: 8px; overflow: hidden; }
.assert-view-header { display: grid; grid-template-columns: 32px 1fr 90px 110px 1fr 130px; background: #e8f5e9; font-size: 12px; font-weight: 600; color: #2e7d32; padding: 8px 14px; gap: 8px; }
.assert-view-row { display: grid; grid-template-columns: 32px 1fr 90px 110px 1fr 130px; gap: 8px; padding: 8px 14px; border-top: 1px solid #e8f5e9; background: white; font-size: 13px; align-items: center; }
.assert-view-row:hover { background: #f6fdf6; }
.av-idx { text-align: center; color: #aaa; font-size: 12px; font-weight: 600; }
.av-name { font-weight: 500; color: var(--text); }
.av-type { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 700; font-family: monospace; }
.type-eq { background: #e3f2fd; color: #1565c0; }
.type-not_eq { background: #fff3e0; color: #e65100; }
.type-contains { background: #f3e5f5; color: #6a1b9a; }
.type-not_contains { background: #fce4ec; color: #880e4f; }
.type-exists { background: #e8f5e9; color: #1b5e20; }
.type-regex { background: #f1f8e9; color: #33691e; }
.av-source { background: #eceff1; color: #455a64; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-family: monospace; }
.av-expr { font-family: 'Monaco','Courier New',monospace; color: #2e7d32; font-size: 12px; }
.av-expect { font-family: 'Monaco','Courier New',monospace; color: #1565c0; font-size: 12px; }
.assert-legacy-pre { background: var(--bg); padding: 14px; border-radius: 8px; font-family: monospace; font-size: 13px; overflow-x: auto; }

/* ===== 关联接口块 ===== */
.endpoint-block { border: 1px solid #e0e7ff; border-radius: 10px; padding: 16px; background: #f5f7ff; }
.endpoint-info-grid { display: flex; flex-direction: column; gap: 0; border: 1px solid #dde4f8; border-radius: 8px; overflow: hidden; }
.endpoint-info-row { display: grid; grid-template-columns: 100px 1fr; align-items: start; gap: 12px; padding: 10px 14px; background: white; border-bottom: 1px solid #eef1fb; }
.endpoint-info-row:last-child { border-bottom: none; }
.endpoint-info-row:hover { background: #f8f9ff; }
.ep-label { font-size: 12px; font-weight: 600; color: #7c8db5; text-transform: uppercase; letter-spacing: .04em; padding-top: 2px; }
.ep-value { font-size: 14px; color: var(--text); }
.ep-link { color: #3498db; cursor: pointer; text-decoration: none; font-weight: 500; font-size: 14px; }
.ep-link:hover { text-decoration: underline; }
.ep-method { display: inline-block; padding: 2px 10px; border-radius: 4px; font-size: 12px; font-weight: 700; font-family: monospace; }
.method-get    { background: #e8f5e9; color: #2e7d32; }
.method-post   { background: #fff3e0; color: #e65100; }
.method-put    { background: #e3f2fd; color: #1565c0; }
.method-patch  { background: #f3e5f5; color: #6a1b9a; }
.method-delete { background: #ffebee; color: #c62828; }
.ep-url { font-family: 'Monaco','Courier New',monospace; font-size: 13px; color: #1a237e; background: #eef1fb; padding: 2px 8px; border-radius: 4px; word-break: break-all; }
.ep-json { margin: 4px 0 0; font-family: 'Monaco','Courier New',monospace; font-size: 12px; line-height: 1.6; color: var(--text); background: #f0f4ff; border-radius: 6px; padding: 8px 12px; overflow-x: auto; }

/* ===== 执行日志区块 ===== */
.run-log-block { border: 1px solid #30363d; border-radius: 10px; padding: 16px; background: #0d1117; }
.run-log-block h4 { color: #c9d1d9; display: flex; align-items: center; gap: 8px; margin-bottom: 12px; font-family: 'Monaco','Courier New',monospace; font-size: 13px; }
.log-panel-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; flex-shrink: 0; }
.dot-running { background: #f0883e; animation: pulse 1.2s ease-in-out infinite; }
.dot-idle    { background: #3fb950; }
@keyframes pulse { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:.4; transform:scale(.8); } }
.log-clear-btn { margin-left: auto; background: none; border: 1px solid #30363d; color: #8b949e; font-size: 12px; padding: 2px 10px; border-radius: 4px; cursor: pointer; transition: all .18s; }
.log-clear-btn:hover { background: #21262d; color: #e74c3c; border-color: #e74c3c; }
.log-list { display: flex; flex-direction: column; gap: 4px; }
.log-record { border: 1px solid #21262d; border-radius: 6px; overflow: hidden; }
.log-record-head { display: flex; align-items: center; gap: 10px; padding: 7px 12px; cursor: pointer; user-select: none; background: #161b22; transition: background .15s; }
.log-record-head:hover { background: #1c2128; }
.log-expand-icon { color: #8b949e; font-size: 12px; width: 12px; flex-shrink: 0; }
.log-record-index { font-size: 12px; color: #58a6ff; font-family: 'Monaco','Courier New',monospace; font-weight: 700; min-width: 28px; }
.log-running-badge { display: inline-flex; align-items: center; gap: 5px; background: #2d2208; color: #f0883e; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 10px; border: 1px solid #f0883e44; }
.log-record-time { font-size: 11px; color: #8b949e; margin-left: 2px; }
.log-report-link a { font-size: 11px; color: #58a6ff; text-decoration: none; padding: 2px 6px; border-radius: 4px; border: 1px solid #1f6feb; transition: background .15s; }
.log-report-link a:hover { background: #1f6feb33; }
.log-del-btn { margin-left: auto; background: none; border: none; color: #6e7681; cursor: pointer; font-size: 13px; padding: 2px 6px; border-radius: 4px; transition: all .15s; }
.log-del-btn:hover { color: #e74c3c; background: #2d1b1b; }
.log-record-body { padding: 8px 12px 10px 34px; background: #0d1117; }
.log-pre { margin: 0; font-family: 'Monaco','Courier New',monospace; font-size: 12px; line-height: 1.65; color: #c9d1d9; white-space: pre-wrap; word-break: break-all; max-height: 300px; overflow-y: auto; }
.log-running-hint { display: flex; align-items: center; gap: 8px; padding: 8px 0; color: #f0883e; font-size: 13px; }
.log-error-msg { color: #f85149; font-size: 12px; font-family: 'Monaco','Courier New',monospace; padding: 6px 0 0; }
.log-meta { font-size: 12px; color: #8b949e; margin-left: 2px; }
.log-section { margin: 8px 0 4px; }
.log-section-title { font-size: 10px; font-weight: 700; color: #8b949e; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
.assert-result-row { display: flex; align-items: center; gap: 8px; padding: 5px 8px; border-radius: 5px; font-size: 12px; margin-bottom: 3px; }
.assert-result-row.apass { background: #0d2018; }
.assert-result-row.afail { background: #2d1114; }
.ar-icon { font-weight: 700; width: 14px; flex-shrink: 0; }
.apass .ar-icon { color: #3fb950; }
.afail .ar-icon { color: #f85149; }
.ar-name { font-weight: 500; color: #e6edf3; flex: 1; }
.ar-detail { font-size: 11px; color: #8b949e; }
.ar-detail code { background: #21262d; padding: 1px 4px; border-radius: 3px; font-family: monospace; font-size: 11px; color: #79c0ff; }
.ar-msg { font-size: 11px; color: #f85149; }
.extract-result-row { display: flex; align-items: center; gap: 8px; padding: 4px 8px; font-size: 12px; border-radius: 5px; background: #1a1040; margin-bottom: 3px; }
.er-key { background: #2d1b69; color: #d2a8ff; padding: 1px 6px; border-radius: 3px; font-family: monospace; font-size: 11px; }
.er-eq { color: #8b949e; }
.er-val { background: #0d2018; color: #3fb950; padding: 1px 6px; border-radius: 3px; font-family: monospace; font-size: 11px; }
.log-no-assert { font-size: 12px; color: #8b949e; padding: 6px 0; }
.mini-spinner { display: inline-block; width: 10px; height: 10px; border: 2px solid #f0883e44; border-top-color: #f0883e; border-radius: 50%; animation: spin .8s linear infinite; }
.spinner-sm { display: inline-block; width: 14px; height: 14px; border: 2px solid #f0883e44; border-top-color: #f0883e; border-radius: 50%; animation: spin .8s linear infinite; vertical-align: middle; }
@keyframes spin { to { transform: rotate(360deg); } }
.param-type-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
.param-type-tabs { display: flex; gap: 4px; }
.param-type-btn { padding: 4px 12px; font-size: 12px; border: 1px solid #d0e8f8; background: white; color: var(--text-light); border-radius: 4px; cursor: pointer; }
.param-type-btn:hover { background: #f0f8ff; color: var(--primary); }
.param-type-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
.param-hint { font-size: 12px; color: var(--text-light); margin-bottom: 8px; }
.param-hint code { background: #f0f4ff; color: #3a56c9; padding: 1px 5px; border-radius: 3px; font-size: 11px; }

/* ===== KV 编辑器 ===== */
.kv-editor { border: 1px solid #d0e8f8; border-radius: 8px; overflow: hidden; margin-bottom: 8px; }
.kv-header { display: grid; grid-template-columns: 1fr 1fr 32px; background: #e3f2fd; font-size: 11px; font-weight: 600; color: #1565c0; padding: 6px 10px; gap: 6px; }
.kv-row { display: grid; grid-template-columns: 1fr 1fr 32px; gap: 6px; padding: 6px 10px; border-top: 1px solid #e8f4fd; align-items: center; background: white; }
.kv-row:hover { background: #f8fcff; }
.kv-input { border: 1px solid #d0e8f8; border-radius: 4px; padding: 4px 7px; font-size: 12px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; }
.kv-input:focus { border-color: #3498db; box-shadow: 0 0 0 2px rgba(52,152,219,.12); }
</style>