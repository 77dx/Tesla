<template>
  <div class="case-form-view">

    <!-- 顶部返回栏 -->
    <div class="page-header">
      <button class="btn-back" @click="$router.back()">
        <ArrowLeftOutlined /> 返回用例列表
      </button>
    </div>

    <!-- 基本信息卡片 -->
    <div class="form-card">
      <div class="form-card__header">
        <div class="form-card__title-group">
          <div class="form-card__title">基本信息</div>
        </div>
      </div>
      <div class="form-card__body">
        <div class="form-row-2">
          <!-- 用例名称 -->
          <div class="form-group">
            <label class="form-label">
              用例名称 <span class="required">*</span>
            </label>
            <input
              v-model="formData.name"
              class="form-input"
              :class="{ 'form-input--error': errors.name }"
              placeholder="输入用例名称"
              maxlength="100"
            />
            <span v-if="errors.name" class="field-error">
              <ExclamationCircleOutlined /> {{ errors.name }}
            </span>
          </div>
          <!-- 关联接口 -->
          <div class="form-group">
            <label class="form-label">关联接口</label>
            <select v-model="formData.endpoint" class="form-select">
              <option :value="null">不指定接口</option>
              <option v-for="e in endpoints" :key="e.id" :value="e.id">
                {{ e.method }} {{ e.name }}
              </option>
            </select>
          </div>
        </div>
        <!-- Allure 标注 -->
        <div class="form-group">
          <label class="form-label">Allure 标注 <span class="field-hint-tag">可选</span></label>
          <textarea
            v-model="formData.alluer"
            class="form-input form-textarea"
            placeholder='{"feature": "用户模块", "story": "登录", "severity": "normal"}'
            rows="2"
          ></textarea>
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

        <!-- ── 请求参数 Tab ── -->
        <div v-show="activeTab === 'params'" class="tab-content">

          <!-- 参数区：Headers / Query Params / Body -->
          <div class="req-sections">

            <!-- Params -->
            <div class="req-section">
              <div class="req-section__head" @click="toggleSection('params')">
                <span class="req-section__icon"><LinkOutlined /></span>
                <span class="req-section__name">Params</span>
                <span v-if="validQueryRows" class="req-section__badge">{{ validQueryRows }}</span>
                <span class="req-section__arrow" :class="{ open: openSections.params }"><RightOutlined /></span>
              </div>
              <div v-show="openSections.params" class="req-section__body">
                <div class="kv-rows">
                  <div class="kv-rows__head">
                    <span>Key</span>
                    <span>Value</span>
                    <span></span>
                  </div>
                  <div v-for="(row, idx) in formData.queryRows" :key="idx" class="kv-rows__row">
                    <input v-model="row.k" class="kv-field" placeholder="param" />
                    <input v-model="row.v" class="kv-field" placeholder="value" />
                    <button class="kv-remove" @click="formData.queryRows.splice(idx, 1)">
                      <CloseOutlined />
                    </button>
                  </div>
                  <button class="kv-add-btn" @click="formData.queryRows.push({ k: '', v: '' })">
                    <PlusOutlined /> Add Parameter
                  </button>
                </div>
              </div>
            </div>

            <!-- Headers -->
            <div class="req-section">
              <div class="req-section__head" @click="toggleSection('headers')">
                <span class="req-section__icon"><AimOutlined /></span>
                <span class="req-section__name">Headers</span>
                <span v-if="validHeaderRows" class="req-section__badge">{{ validHeaderRows }}</span>
                <span class="req-section__arrow" :class="{ open: openSections.headers }"><RightOutlined /></span>
              </div>
              <div v-show="openSections.headers" class="req-section__body">
                <div class="kv-rows">
                  <div class="kv-rows__head">
                    <span>Key</span>
                    <span>Value</span>
                    <span></span>
                  </div>
                  <div v-for="(row, idx) in formData.headerRows" :key="idx" class="kv-rows__row">
                    <input v-model="row.k" class="kv-field" placeholder="Content-Type" />
                    <input v-model="row.v" class="kv-field" placeholder="application/json" />
                    <button class="kv-remove" @click="formData.headerRows.splice(idx, 1)">
                      <CloseOutlined />
                    </button>
                  </div>
                  <button class="kv-add-btn" @click="formData.headerRows.push({ k: '', v: '' })">
                    <PlusOutlined /> Add Header
                  </button>
                </div>
              </div>
            </div>

            <!-- Body -->
            <div class="req-section req-section--open">
              <div class="req-section__head">
                <span class="req-section__icon"><FileTextOutlined /></span>
                <span class="req-section__name">Body</span>
                <div class="body-toggle" @click.stop>
                  <button
                    v-for="bt in bodyTypes"
                    :key="bt.value"
                    class="body-toggle__btn"
                    :class="{ active: formData.paramType === bt.value }"
                    @click="formData.paramType = bt.value"
                  >{{ bt.label }}</button>
                </div>
              </div>
              <div class="req-section__body">

                <!-- KV 模式：JSON / Form -->
                <div v-if="formData.paramType === 'json' || formData.paramType === 'form'" class="kv-rows">
                  <div class="kv-rows__head">
                    <span>Key</span>
                    <span>Value</span>
                    <span></span>
                  </div>
                  <div v-for="(row, idx) in currentBodyRows" :key="idx" class="kv-rows__row">
                    <input v-model="row.k" class="kv-field" placeholder="field_name" />
                    <input v-model="row.v" class="kv-field" placeholder="field_value" />
                    <button class="kv-remove" @click="currentBodyRows.splice(idx, 1)">
                      <CloseOutlined />
                    </button>
                  </div>
                  <button class="kv-add-btn" @click="currentBodyRows.push({ k: '', v: '' })">
                    <PlusOutlined /> Add Field
                  </button>
                </div>

                <!-- Raw 模式 -->
                <div v-if="formData.paramType === 'raw'" class="raw-editor">
                  <textarea
                    v-model="formData.api_args"
                    class="raw-editor__input"
                    :class="{ error: rawJsonError }"
                    placeholder='{"key": "value"}'
                    spellcheck="false"
                  ></textarea>
                  <div v-if="rawJsonError" class="raw-editor__error">
                    <ExclamationCircleOutlined /> Invalid JSON
                  </div>
                </div>

                <div v-if="formData.paramType === 'none'" class="req-section__empty">
                  This request does not have a body
                </div>
              </div>
            </div>

          </div>
        </div>

        <!-- ── 数据提取 Tab ── -->
        <div v-show="activeTab === 'extract'" class="tab-content">
          <div class="kv-table">
            <div class="kv-table__head">
              <span class="col-key">变量名</span>
              <span class="col-val">JSONPath 表达式</span>
              <span style="width: 80px; text-align:center">取第几个</span>
              <span class="col-op"></span>
            </div>
            <div v-for="(rule, idx) in editExtractRules" :key="idx" class="kv-table__row">
              <input v-model="rule.name" class="kv-input" placeholder="token" />
              <input v-model="rule.expr" class="kv-input" placeholder="$.data.access_token" />
              <input v-model.number="rule.index" class="kv-input" type="number" min="0" placeholder="0" />
              <button class="kv-del-btn" @click="editExtractRules.splice(idx, 1)">
                <DeleteOutlined />
              </button>
            </div>
          </div>
          <button class="add-row-btn" @click="editExtractRules.push({ name: '', expr: '', index: 0 })">
            <PlusOutlined /> 添加提取规则
          </button>
          <div v-if="!editExtractRules.length" class="empty-tab">
            <DownloadOutlined class="empty-tab__icon" />
            <p>暂无提取规则，添加后可从响应中提取变量供后续用例使用</p>
          </div>
        </div>

        <!-- ── 断言规则 Tab ── -->
        <div v-show="activeTab === 'validate'" class="tab-content">
          <!-- 工具栏 -->
          <div class="assert-toolbar">
            <span class="assert-count">共 {{ editAssertRules.length }} 条规则</span>
            <div class="assert-add-btns">
              <button type="button" class="btn-add-assert" @click="editAssertRules.push({ name: '状态码断言', type: 'eq', source: 'status_code', expr: '', expect: '200' })">+ 状态码</button>
              <button type="button" class="btn-add-assert" @click="editAssertRules.push({ name: 'JSONPath断言', type: 'eq', source: 'jsonpath', expr: '$.code', expect: '0' })">+ JSONPath</button>
              <button type="button" class="btn-add-assert" @click="editAssertRules.push({ name: '响应文本断言', type: 'contains', source: 'text', expr: '', expect: '' })">+ 响应文本</button>
            </div>
          </div>

          <div class="kv-table">
            <div class="kv-table__head">
              <span style="width: 32px; text-align:center; flex-shrink:0"></span>
              <span style="flex:1">描述</span>
              <span style="width: 90px; flex-shrink:0">类型</span>
              <span style="width: 90px; flex-shrink:0">来源</span>
              <span style="flex:1">表达式</span>
              <span style="flex:1">期望值</span>
              <span style="width: 36px; flex-shrink:0"></span>
            </div>

            <div v-for="(rule, idx) in editAssertRules" :key="idx" class="kv-table__row">
              <span class="row-num">{{ idx + 1 }}</span>
              <input v-model="rule.name" class="kv-input" placeholder="断言描述" />
              <select v-model="rule.type" class="kv-input">
                <option value="eq">eq</option>
                <option value="not_eq">not_eq</option>
                <option value="contains">contains</option>
                <option value="not_contains">not_contains</option>
                <option value="regex">regex</option>
                <option value="exists">exists</option>
              </select>
              <select v-model="rule.source" class="kv-input">
                <option value="status_code">状态码</option>
                <option value="jsonpath">JSONPath</option>
                <option value="text">响应文本</option>
              </select>
              <input
                v-if="rule.source !== 'status_code'"
                v-model="rule.expr"
                class="kv-input"
                :placeholder="rule.source === 'jsonpath' ? '$.data.code' : '正则表达式'"
              />
              <span v-else class="kv-placeholder">HTTP 状态码</span>
              <input
                v-if="rule.type !== 'exists'"
                v-model="rule.expect"
                class="kv-input"
                placeholder="期望值"
              />
              <span v-else class="kv-placeholder">存在即通过</span>
              <button class="kv-del-btn" @click="editAssertRules.splice(idx, 1)">
                <DeleteOutlined />
              </button>
            </div>
          </div>

          <button class="add-row-btn" @click="editAssertRules.push({ name: '', type: 'eq', source: 'jsonpath', expr: '', expect: '' })">
            <PlusOutlined /> 添加断言
          </button>

          <div v-if="!editAssertRules.length" class="empty-tab">
            <CheckCircleOutlined class="empty-tab__icon" />
            <p>暂无断言规则，点击上方按钮快速添加</p>
          </div>
        </div>

        <!-- ── 前后置脚本 Tab ── -->
        <div v-show="activeTab === 'script'" class="tab-content">
          <!-- 前后置脚本卡片 -->
          <div class="script-cards">
            <!-- 前置脚本 -->
            <div class="script-card">
              <div class="script-card__header">
                <div class="script-card__icon script-card__icon--pre">
                  <RocketOutlined />
                </div>
                <div class="script-card__info">
                  <div class="script-card__title">前置脚本</div>
                  <div class="script-card__sub">Pre-request Script · 请求发送前执行</div>
                </div>
              </div>
              <div class="code-editor-wrap">
                <textarea
                  v-model="formData.pre_script"
                  class="code-editor"
                  placeholder="// 在请求发送前执行&#10;// 可从 pm.variables 获取已提取的变量&#10;// 可修改 pm.request.headers / params / body&#10;&#10;// 示例：添加时间戳&#10;pm.variables.set('timestamp', Date.now())&#10;&#10;// 示例：基于已提取的 token 拼接请求&#10;const token = pm.variables.get('access_token')&#10;pm.request.headers.add({ key: 'Authorization', value: `Bearer ${token}` })"
                  spellcheck="false"
                ></textarea>
              </div>
            </div>

            <!-- 后置脚本 -->
            <div class="script-card">
              <div class="script-card__header">
                <div class="script-card__icon script-card__icon--post">
                  <FileProtectOutlined />
                </div>
                <div class="script-card__info">
                  <div class="script-card__title">后置脚本</div>
                  <div class="script-card__sub">Post-response Script · 响应返回后执行</div>
                </div>
              </div>
              <div class="code-editor-wrap">
                <textarea
                  v-model="formData.post_script"
                  class="code-editor"
                  placeholder="// 在响应返回后执行&#10;// pm.response 包含响应信息&#10;// 可在 pm.variables 中保存变量供后续用例使用&#10;&#10;// 示例：从 JSON 响应中提取 token&#10;const json = pm.response.json()&#10;pm.variables.set('access_token', json.data.access_token)&#10;&#10;// 示例：打印日志（可在运行日志中查看）&#10;console.log('响应状态码:', pm.response.code)&#10;console.log('响应体:', pm.response.text())"
                  spellcheck="false"
                ></textarea>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- 底部操作栏 -->
    <div class="action-bar">
      <div class="action-bar__inner">
        <button type="button" class="btn btn--ghost" @click="$router.back()">
          <CloseOutlined /> 取消
        </button>
        <button type="submit" class="btn btn--primary" :disabled="saving" @click="handleSubmit">
          <template v-if="saving">
            <LoadingOutlined /> 保存中...
          </template>
          <template v-else>
            <CheckOutlined />
            {{ isEdit ? '保存修改' : '创建用例' }}
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  createCase, updateCase, getCase, getEndpoints,
} from '@/api/case'
import {
  ArrowLeftOutlined, ApiOutlined, FileTextOutlined,
  KeyOutlined, MenuOutlined, DownloadOutlined,
  CheckCircleOutlined, CodeOutlined, RocketOutlined, FileProtectOutlined,
  CheckOutlined, CloseOutlined, DeleteOutlined,
  PlusOutlined, LoadingOutlined, ExclamationCircleOutlined, DownOutlined,
  LinkOutlined, AimOutlined, RightOutlined,
} from '@ant-design/icons-vue'

const router = useRouter()
const route = useRoute()

const isEdit = computed(() => !!route.params.id)
const activeTab = ref('params')

// ─── 折叠状态 ────────────────────────────────────
const openSections = reactive({ params: true, headers: false })
const toggleSection = (key) => { openSections[key] = !openSections[key] }

// ─── 表单数据 ───────────────────────────────────
const formData = reactive({
  name: '',
  endpoint: null,
  alluer: '',
  paramType: 'raw',
  jsonRows: [],
  formRows: [],
  queryRows: [],
  headerRows: [],
  api_args: '',
  pre_script: '',
  post_script: '',
})

const errors = reactive({ name: '' })
const saving = ref(false)
const endpoints = ref([])
const rawJsonError = ref(false)

// ─── Tab 配置 ───────────────────────────────────
const tabs = computed(() => [
  { key: 'params',   label: '请求参数',  icon: ApiOutlined },
  { key: 'extract',  label: '数据提取',  icon: DownloadOutlined },
  { key: 'validate', label: '断言规则',  icon: CheckCircleOutlined },
  { key: 'script',   label: '前后置脚本',  icon: CodeOutlined },
])

// ─── Body 类型 ───────────────────────────────────
const bodyTypes = [
  { value: 'none', label: 'none' },
  { value: 'raw',  label: 'Raw' },
  { value: 'json', label: 'JSON' },
  { value: 'form', label: 'Form' },
]

const currentBodyRows = computed(() =>
  formData.paramType === 'json' ? formData.jsonRows : formData.formRows
)

// ─── 有效行数 ───────────────────────────────────
const validHeaderRows = computed(() => formData.headerRows.filter(r => r.k?.trim()).length)
const validQueryRows = computed(() => formData.queryRows.filter(r => r.k?.trim()).length)

// ─── 提取规则 ───────────────────────────────────
const editExtractRules = ref([])

// ─── 断言规则 ────────────────────────────────────
const editAssertRules = ref([])

// ─── 校验 ────────────────────────────────────────
const validate = () => {
  errors.name = ''
  if (!formData.name.trim()) {
    errors.name = '用例名称不能为空'
    return false
  }
  if (formData.paramType === 'raw' && formData.api_args.trim()) {
    try {
      JSON.parse(formData.api_args)
      rawJsonError.value = false
    } catch {
      rawJsonError.value = true
      message.error('原始 JSON 格式错误，请检查')
      return false
    }
  }
  return true
}

// ─── 辅助函数 ────────────────────────────────────
const rowsToObj = (rows) => {
  const obj = {}
  for (const r of rows) if (r.k?.trim()) obj[r.k.trim()] = r.v
  return Object.keys(obj).length ? obj : null
}

const buildApiArgs = () => {
  if (formData.paramType === 'none') return null
  if (formData.paramType === 'raw')
    return formData.api_args ? JSON.parse(formData.api_args) : null
  const obj = {}
  if (formData.paramType === 'json') { const d = rowsToObj(formData.jsonRows); if (d) obj.json = d }
  else if (formData.paramType === 'form') { const d = rowsToObj(formData.formRows); if (d) obj.data = d }
  const headers = rowsToObj(formData.headerRows)
  if (headers) obj.headers = headers
  const params = rowsToObj(formData.queryRows)
  if (params) obj.params = params
  return Object.keys(obj).length ? obj : null
}

const buildExtractObj = () => {
  const obj = {}
  for (const r of editExtractRules.value)
    if (r.name?.trim()) obj[r.name.trim()] = ['json', r.expr?.trim() || '', r.index ?? 0]
  return Object.keys(obj).length ? obj : null
}

const buildAssertList = () =>
  editAssertRules.value
    .filter(r => r.name?.trim())
    .map(r => {
      const rule = { name: r.name.trim(), type: r.type, source: r.source || 'jsonpath' }
      if (r.type !== 'exists') rule.expect = r.expect
      if (r.source !== 'status_code') rule.expr = r.expr
      return rule
    })

const parseAssertList = (validate) => {
  if (!validate) return []
  if (Array.isArray(validate)) {
    return validate.map(r => ({
      name: r.name || '', type: r.type || 'eq', source: r.source || 'jsonpath',
      expr: r.expr || '', expect: r.expect != null ? String(r.expect) : '',
    }))
  }
  const rows = []
  for (const [k, v] of Object.entries(validate)) {
    if (k === 'status_code') { rows.push({ name: '状态码', type: 'eq', source: 'status_code', expr: '', expect: String(v) }); continue }
    if (typeof v === 'object' && v !== null) {
      for (const [desc, item] of Object.entries(v)) {
        rows.push({ name: desc, type: k === 'equals' ? 'eq' : k, source: 'jsonpath', expect: String(Array.isArray(item) ? item[0] : '') })
      }
    }
  }
  return rows
}

const objToRows = (obj) =>
  obj ? Object.entries(obj).map(([k, v]) => ({ k, v: String(v) })) : []

const parseApiArgs = (api_args) => {
  if (!api_args) return { paramType: 'none', jsonRows: [], formRows: [], queryRows: [], headerRows: [], api_args: '' }
  const params = objToRows(api_args.params)
  const headers = objToRows(api_args.headers)
  if (api_args.json) return { paramType: 'json', jsonRows: objToRows(api_args.json), formRows: [], queryRows: params, headerRows: headers, api_args: '' }
  if (api_args.data) return { paramType: 'form', formRows: objToRows(api_args.data), jsonRows: [], queryRows: params, headerRows: headers, api_args: '' }
  return { paramType: 'raw', api_args: JSON.stringify(api_args, null, 2), jsonRows: [], formRows: [], queryRows: params, headerRows: headers }
}

// ─── 提交 ────────────────────────────────────────
const handleSubmit = async () => {
  if (!validate()) return
  saving.value = true
  try {
    const api_args = buildApiArgs()
    const data = {
      name: formData.name.trim(),
      endpoint: formData.endpoint,
      alluer: formData.alluer.trim() ? JSON.parse(formData.alluer) : null,
      api_args,
      extract: buildExtractObj(),
      validate: buildAssertList().length ? buildAssertList() : null,
      pre_script: formData.pre_script || '',
      post_script: formData.post_script || '',
    }
    if (isEdit.value) {
      await updateCase(route.params.id, data)
      message.success('用例更新成功')
    } else {
      await createCase(data)
      message.success('用例创建成功')
    }
    router.push('/cases')
  } catch (e) {
    const detail = e.response?.data?.detail || e.response?.data?.message || ''
    message.error('保存失败' + (detail ? '：' + detail : ''))
  } finally {
    saving.value = false
  }
}

// ─── 加载数据 ────────────────────────────────────
const loadEndpoints = async () => {
  try {
    const res = await getEndpoints({ page_size: 200 })
    endpoints.value = res.result?.list || res.results || res || []
  } catch (e) {
    console.error('加载接口列表失败', e)
  }
}

const loadCase = async () => {
  try {
    const res = await getCase(route.params.id)
    const c = res.result || res
    formData.name = c.name || ''
    formData.endpoint = c.endpoint?.id || c.endpoint || null
    formData.alluer = c.alluer ? JSON.stringify(c.alluer, null, 2) : ''
    formData.pre_script = c.pre_script || ''
    formData.post_script = c.post_script || ''

    const parsed = parseApiArgs(c.api_args)
    formData.paramType = parsed.paramType
    formData.jsonRows = parsed.jsonRows
    formData.formRows = parsed.formRows
    formData.queryRows = parsed.queryRows
    formData.headerRows = parsed.headerRows
    formData.api_args = parsed.api_args

    editExtractRules.value = c.extract
      ? Object.entries(c.extract).map(([name, rule]) =>
          Array.isArray(rule) ? { name, expr: rule[1] ?? '', index: rule[2] ?? 0 } : { name, expr: String(rule), index: 0 })
      : []
    editAssertRules.value = parseAssertList(c.validate)
  } catch (e) {
    message.error('加载用例信息失败')
    router.push('/cases')
  }
}

onMounted(async () => {
  await loadEndpoints()
  if (isEdit.value) await loadCase()
})
</script>

<style scoped>
/* ─── 页面整体 ─── */
.case-form-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1100px;
  margin: 0 auto;
}

/* ─── 顶部返回栏 ─── */
.page-header {
  display: flex;
  align-items: center;
  padding: 0 4px;
}

.btn-back {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  color: var(--color-text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  color: var(--color-text-primary);
  border-color: var(--color-primary);
  background: #f0f7ff;
}

/* ─── Tab 切换区 ─── */
.tabs-wrapper {
  border-radius: 14px;
  overflow: hidden;
}

.tabs-nav {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 10px 16px 0;
  border-bottom: 1px solid #f0f0f0;
  background: #fafbfc;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px 11px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary, #9CA3AF);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border-radius: 8px 8px 0 0;
  transition: all 0.15s;
  position: relative;
}

.tab-btn:hover {
  color: var(--color-text-primary);
  background: #f0f0f0;
}

.tab-btn--active {
  color: var(--color-primary);
  background: white;
  border-bottom: 2px solid var(--color-primary);
  margin-bottom: -1px;
}

.tab-btn__icon {
  font-size: 13px;
}

.tab-btn__count {
  background: var(--color-primary);
  color: white;
  font-size: 11px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.tab-content {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: white;
  min-height: 200px;
}

/* ─── 请求参数区（Postman 风格）── */

.req-sections {
  display: flex;
  flex-direction: column;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
}

.req-section {
  border-bottom: 1px solid #f0f0f0;
}

.req-section:last-child { border-bottom: none; }

.req-section__head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #fafbfc;
  cursor: pointer;
  user-select: none;
  transition: background 0.15s;
}

.req-section:not(.req-section--open) .req-section__head:hover {
  background: #f3f4f6;
}

.req-section--open .req-section__head {
  cursor: default;
  background: white;
  border-bottom: 1px solid #f0f0f0;
}

.req-section__icon {
  color: #9CA3AF;
  font-size: 13px;
  display: flex;
  align-items: center;
}

.req-section__name {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  flex: 1;
}

.req-section__badge {
  font-size: 11px;
  font-weight: 600;
  color: white;
  background: #d1d5db;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
  transition: background 0.15s;
}

.req-section__badge:not([style]) { background: #d1d5db; }

.req-section__head:hover .req-section__badge { background: #9CA3AF; }

.req-section__arrow {
  color: #9CA3AF;
  font-size: 10px;
  display: flex;
  align-items: center;
  transition: transform 0.2s;
}

.req-section__arrow.open { transform: rotate(90deg); }

.req-section__body {
  background: white;
}

.req-section__empty {
  padding: 20px;
  text-align: center;
  font-size: 13px;
  color: #9CA3AF;
}

.body-toggle {
  display: flex;
  gap: 2px;
  padding: 2px;
  background: #f3f4f6;
  border-radius: 7px;
}

.body-toggle__btn {
  padding: 4px 12px;
  border-radius: 5px;
  border: none;
  background: transparent;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.body-toggle__btn.active {
  background: white;
  color: var(--color-primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* ─── KV 行 ─── */
.kv-rows {
  padding: 0 0 12px;
}

.kv-rows__head {
  display: grid;
  grid-template-columns: 1fr 1fr 36px;
  gap: 8px;
  padding: 8px 16px 6px;
  font-size: 11px;
  font-weight: 600;
  color: #9CA3AF;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.kv-rows__row {
  display: grid;
  grid-template-columns: 1fr 1fr 36px;
  gap: 8px;
  padding: 2px 16px;
  align-items: center;
}

.kv-field {
  padding: 8px 10px;
  border: 1.5px solid #e5e7eb;
  border-radius: 7px;
  font-size: 13px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  width: 100%;
}

.kv-field:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.kv-field::placeholder { color: #c4c9d4; }

.kv-remove {
  width: 34px;
  height: 34px;
  border-radius: 7px;
  border: 1px solid #fecaca;
  background: white;
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.kv-remove:hover { background: #fef2f2; border-color: #ef4444; }

.kv-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin: 6px 16px 0;
  padding: 7px 12px;
  border-radius: 7px;
  border: 1.5px dashed #d1d5db;
  background: transparent;
  color: #9CA3AF;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.kv-add-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: #f0f7ff;
}

/* ─── Raw 编辑器 ─── */
.raw-editor {
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
  margin: 0 16px 12px;
}

.raw-editor__input {
  width: 100%;
  min-height: 140px;
  background: #1e1e1e;
  color: #d4d4d4;
  border: none;
  outline: none;
  padding: 14px 16px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', monospace;
  line-height: 1.65;
  resize: vertical;
  box-sizing: border-box;
}

.raw-editor__input::placeholder { color: #5a5a5a; }

.raw-editor__input.error { background: #2a1212; color: #f87171; }

.raw-editor__error {
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  border-top: 1px solid rgba(239, 68, 68, 0.2);
}

/* ─── 断言规则 ─── */
.assert-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}

.assert-count {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

.assert-add-btns { display: flex; gap: 6px; flex-wrap: wrap; }

.btn-add-assert {
  font-size: 12px;
  padding: 5px 14px;
  border: 1.5px dashed #10B981;
  border-radius: 8px;
  background: white;
  color: #10B981;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.btn-add-assert:hover { background: #f0fdf4; }

.kv-placeholder {
  font-size: 12px;
  color: #9CA3AF;
  padding: 0 4px;
}

/* ─── KV 表格 ─── */
.kv-table {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.kv-table__head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 4px;
  font-size: 12px;
  font-weight: 600;
  color: #9CA3AF;
}

.kv-table__row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kv-table__row--sub {
  background: #fafbfc;
  border-radius: 8px;
  padding: 6px 0;
}

.col-key { flex: 1; }
.col-val { flex: 1; }
.col-op  { width: 36px; text-align: center; }

.row-num {
  width: 32px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--color-primary);
  flex-shrink: 0;
}

.kv-input {
  flex: 1;
  padding: 9px 12px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.kv-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.kv-input::placeholder { color: #c4c9d4; }

.kv-del-btn {
  width: 34px;
  height: 34px;
  border-radius: 7px;
  border: 1px solid #fecaca;
  background: white;
  color: #ef4444;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
  flex-shrink: 0;
}

.kv-del-btn:hover {
  background: #fef2f2;
  border-color: #ef4444;
}

.kv-del-btn--sm {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  margin-left: auto;
}

.add-row-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 7px 14px;
  border-radius: 8px;
  border: 1.5px dashed #d1d5db;
  background: white;
  color: #6b7280;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
  align-self: flex-start;
}

.add-row-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background: #f0f7ff;
}

/* ─── 代码编辑器 ─── */
.code-editor-wrap {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #1e1e1e;
}

.code-editor {
  width: 100%;
  min-height: 140px;
  background: #1e1e1e;
  color: #d4d4d4;
  border: none;
  outline: none;
  padding: 14px 16px;
  font-size: 13px;
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  line-height: 1.65;
  resize: vertical;
}

.code-editor::placeholder { color: #5a5a5a; }

.code-editor--error { background: #2a1212; color: #f87171; }

.code-error {
  padding: 6px 14px;
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  color: #9CA3AF;
  font-size: 13px;
}

/* ─── 脚本区块（前后置脚本）── */
.script-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.script-card {
  background: white;
  border: 1.5px solid #e5e7eb;
  border-radius: 12px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.script-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.07);
}

.script-card__header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background: #fafbfc;
  border-bottom: 1px solid #f0f0f0;
}

.script-card__icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
  flex-shrink: 0;
}

.script-card__icon--pre {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.script-card__icon--post {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.script-card__info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.script-card__title {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.script-card__sub {
  font-size: 11px;
  color: #9CA3AF;
}

.script-card .code-editor-wrap {
  border: none;
  border-radius: 0;
}

.script-card .code-editor {
  min-height: 160px;
}

/* ─── 空状态 & 提示 ─── */
.empty-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 32px;
  color: #9CA3AF;
  text-align: center;
}

.empty-tab__icon {
  font-size: 28px;
  opacity: 0.5;
}

.empty-tab p {
  margin: 0;
  font-size: 13px;
  max-width: 280px;
  line-height: 1.6;
}

/* ─── 表单基础样式 ─── */
.form-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}

.form-card--no-clip {
  overflow: visible;
}

.form-card__header {
  padding: 16px 22px;
  border-bottom: 1px solid #f0f0f0;
  background: linear-gradient(to bottom, #fafbfc, white);
}

.form-card__title-group {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.form-card__title {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-text-primary);
}

.form-card__body {
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.required {
  color: var(--color-primary);
}

.field-hint-tag {
  font-size: 11px;
  font-weight: 400;
  color: #9CA3AF;
  background: #f3f4f6;
  padding: 1px 6px;
  border-radius: 4px;
}

.form-input {
  padding: 10px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
}

.form-input--sm {
  padding: 7px 10px;
  font-size: 13px;
  border-radius: 7px;
}

.form-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input--error {
  border-color: #ef4444 !important;
}

.form-textarea {
  resize: vertical;
  min-height: 72px;
  line-height: 1.6;
  font-family: 'SF Mono', 'Fira Code', monospace;
  font-size: 13px;
  background: #fafbfc;
}

.form-select {
  padding: 10px 14px;
  border: 1.5px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  color: var(--color-text-primary);
  background: white;
  outline: none;
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-select--sm {
  padding: 7px 10px;
  font-size: 13px;
  border-radius: 7px;
}

.form-select:focus {
  border-color: var(--color-primary);
}

.field-error {
  font-size: 12px;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ─── 底部操作栏 ─── */
.action-bar {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 16px 24px;
  box-shadow: 0 -2px 8px rgba(0,0,0,0.04);
}

.action-bar__inner {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
}

/* ─── 按钮 ─── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 24px;
  border: 1.5px solid transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  outline: none;
}

.btn:disabled { opacity: 0.5; cursor: not-allowed; }

.btn--primary {
  background: linear-gradient(135deg, var(--color-primary), #2563EB);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
}

.btn--primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563EB, #1d4ed8);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  transform: translateY(-1px);
}

.btn--ghost {
  background: white;
  color: var(--color-text-secondary);
  border-color: #e5e7eb;
}

.btn--ghost:hover:not(:disabled) {
  color: var(--color-text-primary);
  border-color: #d1d5db;
  background: #f9fafb;
}

/* ─── 响应式 ─── */
@media (max-width: 768px) {
  .form-row-2 {
    grid-template-columns: 1fr;
  }

  .tabs-nav {
    flex-wrap: wrap;
  }

  .action-bar__inner {
    flex-direction: column-reverse;
  }

  .btn {
    width: 100%;
  }
}
</style>
