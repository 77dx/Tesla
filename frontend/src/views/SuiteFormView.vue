<template>
  <div class="suite-form-view">
    <div class="page-header">
      <button @click="$router.back()" class="btn-back"><span>←</span> 返回</button>
      <div class="page-title-block">
        <h2 class="page-title">新建测试套件</h2>
        <span class="page-subtitle">配置套件基本信息、执行环境及策略</span>
      </div>
    </div>

    <form @submit.prevent="handleSubmit" class="form-body">

      <!-- 基本信息 -->
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">📋</span>
          <h3>基本信息</h3>
        </div>
        <div class="form-row-2">
          <div class="form-group">
            <label>套件名称 <span class="required">*</span></label>
            <input v-model="formData.name" required placeholder="如：用户登录流程测试" />
          </div>
          <div class="form-group">
            <label>所属项目</label>
            <select v-model="formData.project">
              <option :value="null">不指定</option>
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label>描述</label>
          <textarea v-model="formData.description" rows="2" placeholder="可选备注，描述套件的用途"></textarea>
        </div>
      </div>

      <!-- 运行配置 -->
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">⚙️</span>
          <h3>运行配置</h3>
        </div>

        <div class="form-group">
          <label>运行类型 <span class="required">*</span></label>
          <div class="run-type-options">
            <label v-for="t in runTypes" :key="t.value"
              class="run-type-radio" :class="{ active: formData.run_type === t.value, ['rt-'+t.value.toLowerCase()]: true }">
              <input type="radio" v-model="formData.run_type" :value="t.value" hidden />
              <span class="rt-icon">{{ t.icon }}</span>
              <span class="rt-label">
                <span class="rt-name">{{ t.label }}</span>
                <span class="rt-desc">{{ t.desc }}</span>
              </span>
            </label>
          </div>
        </div>

        <div v-if="formData.run_type === 'C'" class="form-group">
          <label>Cron 表达式 <span class="required">*</span></label>
          <div class="cron-presets">
            <span v-for="p in cronPresets" :key="p.value"
              class="preset-tag" :class="{ active: formData.cron === p.value }"
              @click="formData.cron = p.value">{{ p.label }}</span>
          </div>
          <input v-model="formData.cron" placeholder="0 9 * * 1-5" />
          <span class="field-hint">格式：分 时 日 月 周，如 <code>0 */2 * * *</code> 表示每2小时执行</span>
        </div>

        <div v-if="formData.run_type === 'W'" class="form-group">
          <label>WebHook 密钥</label>
          <input v-model="formData.hook_key" placeholder="留空则自动生成" />
          <span class="field-hint">触发地址：<code>POST /api/suite/suite/{id}/webhook/?key={密钥}</code></span>
        </div>

        <div class="form-group">
          <label>运行环境</label>
          <select v-model="formData.environment">
            <option :value="null">不指定环境</option>
            <option v-for="e in environments" :key="e.id" :value="e.id">{{ e.name }}</option>
          </select>
          <span class="field-hint">执行时自动注入环境变量、服务 URL 和全局请求头</span>
        </div>
      </div>

      <!-- 执行策略 -->
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">🎯</span>
          <h3>执行策略</h3>
        </div>
        <div class="form-row-3">
          <div class="form-group">
            <label>用例超时时间<span class="label-hint">超时则标记失败，0=不限制</span></label>
            <div class="input-addon">
              <input v-model.number="formData.timeout_seconds" type="number" min="0" placeholder="0" />
              <span class="addon-unit">秒</span>
            </div>
          </div>
          <div class="form-group">
            <label>失败策略</label>
            <div class="radio-group">
              <label class="radio-opt" :class="{ active: formData.fail_strategy === 'continue' }">
                <input type="radio" v-model="formData.fail_strategy" value="continue" hidden />
                ▶ 继续执行
              </label>
              <label class="radio-opt" :class="{ active: formData.fail_strategy === 'stop' }">
                <input type="radio" v-model="formData.fail_strategy" value="stop" hidden />
                ⏹ 立即停止
              </label>
            </div>
          </div>
          <div class="form-group">
            <label>失败重试<span class="label-hint">失败后自动重试</span></label>
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
        </div>
      </div>

      <!-- 套件变量 -->
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">🔑</span>
          <h3>套件变量</h3>
          <span class="section-hint">优先级高于全局变量，可在用例参数中用 ${变量名} 引用</span>
          <button type="button" class="btn-add-row" @click="suiteVars.push({k:'',v:''})">+ 添加变量</button>
        </div>
        <div class="kv-table">
          <div class="kv-head"><span>变量名</span><span>变量值</span><span></span></div>
          <div v-for="(row, i) in suiteVars" :key="i" class="kv-row-2">
            <input v-model="row.k" placeholder="变量名" class="kv-input" />
            <input v-model="row.v" placeholder="变量值" class="kv-input" />
            <button type="button" class="kv-del" @click="suiteVars.splice(i,1)">✕</button>
          </div>
          <div v-if="!suiteVars.length" class="kv-empty">暂无变量，点击「添加变量」</div>
        </div>
      </div>

      <!-- 套件请求头 -->
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">🌐</span>
          <h3>套件请求头</h3>
          <span class="section-hint">注入到本套件所有请求，优先级高于环境 Headers，支持 ${变量名} 占位符</span>
          <button type="button" class="btn-add-row" @click="suiteHeaders.push({k:'',v:''})">+ 添加请求头</button>
        </div>
        <div class="kv-table">
          <div class="kv-head"><span>Header 名</span><span>Header 值</span><span></span></div>
          <div v-for="(row, i) in suiteHeaders" :key="i" class="kv-row-2">
            <input v-model="row.k" placeholder="如：Authorization" class="kv-input" />
            <input v-model="row.v" placeholder="如：Bearer ${token}" class="kv-input" />
            <button type="button" class="kv-del" @click="suiteHeaders.splice(i,1)">✕</button>
          </div>
          <div v-if="!suiteHeaders.length" class="kv-empty">暂未配置请求头</div>
        </div>
      </div>

      <!-- 操作栏 -->
      <div class="form-actions">
        <button type="button" class="btn btn-ghost" @click="$router.back()">取消</button>
        <button type="submit" class="btn btn-primary btn-submit" :disabled="saving">
          <span v-if="saving" class="spin">◌</span>
          {{ saving ? '创建中...' : '创建套件' }}
        </button>
      </div>

    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { createSuite, getEnvironments } from '@/api/suite'
import { getProjects } from '@/api/project'

const router = useRouter()
const projects     = ref([])
const environments = ref([])
const saving       = ref(false)
const suiteVars    = ref([])
const suiteHeaders = ref([])

const formData = ref({
  name: '', run_type: 'O', project: null, environment: null,
  description: '', cron: '', hook_key: '',
  timeout_seconds: 0, fail_strategy: 'continue', retry_count: 0, retry_delay: 1.0,
})

const runTypes = [
  { value: 'O', label: '手动执行', icon: '▶', desc: '点击按钮手动触发' },
  { value: 'C', label: '定时执行', icon: '🕐', desc: '按 Cron 表达式定时运行' },
  { value: 'W', label: 'WebHook',  icon: '🔗', desc: 'HTTP 请求触发执行' },
]

const cronPresets = [
  { label: '每分钟',   value: '* * * * *' },
  { label: '每小时',   value: '0 * * * *' },
  { label: '每天9点',  value: '0 9 * * *' },
  { label: '每天0点',  value: '0 0 * * *' },
  { label: '工作日9点', value: '0 9 * * 1-5' },
  { label: '每周一0点', value: '0 0 * * 1' },
]

const handleSubmit = async () => {
  saving.value = true
  try {
    const svObj = {}
    for (const r of suiteVars.value) if (r.k?.trim()) svObj[r.k.trim()] = r.v
    const shObj = {}
    for (const r of suiteHeaders.value) if (r.k?.trim()) shObj[r.k.trim()] = r.v
    const res = await createSuite({
      ...formData.value,
      suite_variables: Object.keys(svObj).length ? svObj : null,
      suite_headers: Object.keys(shObj).length ? shObj : null,
    })
    const newId = res.result?.id || res.id
    router.push(newId ? `/suites/${newId}` : '/suites')
  } catch (e) {
    alert('创建失败: ' + (e.response?.data?.message || e.message))
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [pr, er] = await Promise.all([
    getProjects({ page_size: 200 }),
    getEnvironments({ page_size: 200 }),
  ])
  projects.value     = pr.result?.list || []
  environments.value = er.result?.list || []
})
</script>

<style scoped>
.suite-form-view { display: flex; flex-direction: column; gap: 20px; }

/* 页头 */
.page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 4px; }
.btn-back { display: flex; align-items: center; gap: 6px; background: white; border: 1px solid var(--border); color: var(--text); border-radius: 8px; padding: 8px 16px; cursor: pointer; font-size: 13px; transition: all .15s; }
.btn-back:hover { border-color: var(--accent); color: var(--accent); }
.page-title-block { display: flex; flex-direction: column; gap: 2px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--primary); margin: 0; }
.page-subtitle { font-size: 13px; color: var(--text-light); }

/* 表单主体 */
.form-body { display: flex; flex-direction: column; gap: 16px; }

/* 每个分区卡片 */
.form-section { padding: 24px 28px; }
.section-header { display: flex; align-items: center; gap: 10px; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid var(--border); }
.section-icon { font-size: 18px; }
.section-header h3 { font-size: 15px; font-weight: 700; color: var(--primary); margin: 0; flex: 1; }
.section-hint { font-size: 12px; color: var(--text-light); }

/* 表单元素 */
.form-row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-row-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; }
.form-group { margin-bottom: 18px; }
.form-group label { display: flex; align-items: center; gap: 8px; font-size: 13px; font-weight: 600; color: var(--text); margin-bottom: 8px; }
.required { color: var(--danger); }
.label-hint { font-size: 11px; color: var(--text-light); font-weight: 400; }
.field-hint { font-size: 12px; color: var(--text-light); margin-top: 6px; display: block; }
.field-hint code { background: #f5f7fa; padding: 1px 5px; border-radius: 3px; font-family: monospace; }

/* 运行类型选择 */
.run-type-options { display: flex; gap: 10px; flex-wrap: wrap; }
.run-type-radio { display: flex; align-items: center; gap: 10px; padding: 10px 20px; border-radius: 10px; border: 1.5px solid var(--border); cursor: pointer; font-size: 13px; background: white; user-select: none; transition: all .15s; min-width: 140px; }
.run-type-radio:hover { border-color: var(--accent); }
.run-type-radio.active.rt-o { background: #e3f2fd; border-color: #1976d2; }
.run-type-radio.active.rt-c { background: #fff3e0; border-color: #e65100; }
.run-type-radio.active.rt-w { background: #f3e5f5; border-color: #7b1fa2; }
.rt-icon { font-size: 18px; }
.rt-label { display: flex; flex-direction: column; gap: 2px; }
.rt-name { font-weight: 600; font-size: 13px; }
.rt-desc { font-size: 11px; color: var(--text-light); }
.run-type-radio.active .rt-desc { opacity: .8; }

/* Cron 预设 */
.cron-presets { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.preset-tag { padding: 4px 12px; border-radius: 12px; font-size: 12px; background: #f5f7fa; border: 1px solid var(--border); cursor: pointer; transition: all .15s; user-select: none; }
.preset-tag:hover, .preset-tag.active { background: var(--accent); color: white; border-color: var(--accent); }

/* 输入框带单位 */
.input-addon { display: flex; align-items: center; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; background: white; transition: border-color .2s; }
.input-addon:focus-within { border-color: var(--accent); box-shadow: 0 0 0 2px rgba(52,152,219,.1); }
.input-addon input { border: none; outline: none; padding: 9px 12px; flex: 1; font-size: 13px; min-width: 0; background: transparent; }
.addon-unit { padding: 9px 12px; background: #f5f7fa; color: var(--text-light); font-size: 12px; border-left: 1px solid var(--border); white-space: nowrap; }

/* 失败策略单选 */
.radio-group { display: flex; gap: 8px; flex-wrap: wrap; }
.radio-opt { display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px; border: 1.5px solid var(--border); border-radius: 8px; cursor: pointer; font-size: 13px; transition: all .15s; background: white; }
.radio-opt:hover { border-color: var(--accent); }
.radio-opt.active { border-color: var(--accent); background: #e3f2fd; color: var(--accent); font-weight: 600; }

/* 重试行 */
.retry-row { display: flex; align-items: center; gap: 10px; }
.retry-sep { color: var(--text-light); font-size: 13px; white-space: nowrap; }

/* KV 表格 */
.kv-table { border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
.kv-head { display: grid; grid-template-columns: 1fr 1fr 32px; background: var(--primary); color: white; font-size: 11px; font-weight: 600; padding: 8px 12px; gap: 8px; }
.kv-row-2 { display: grid; grid-template-columns: 1fr 1fr 32px; gap: 8px; padding: 7px 12px; border-top: 1px solid var(--border); align-items: center; transition: background .1s; }
.kv-row-2:hover { background: #fafbfc; }
.kv-input { border: 1px solid var(--border); border-radius: 5px; padding: 6px 9px; font-size: 13px; font-family: 'Monaco','Courier New',monospace; outline: none; width: 100%; box-sizing: border-box; transition: border-color .15s; }
.kv-input:focus { border-color: var(--accent); }
.kv-del { background: none; border: none; color: #ccc; cursor: pointer; font-size: 14px; padding: 2px; border-radius: 4px; transition: color .15s; }
.kv-del:hover { color: var(--danger); }
.kv-empty { padding: 16px; text-align: center; color: var(--text-light); font-size: 13px; background: #fafafa; }
.btn-add-row { background: none; border: 1px dashed var(--accent); color: var(--accent); border-radius: 6px; padding: 4px 14px; font-size: 12px; cursor: pointer; transition: background .15s; }
.btn-add-row:hover { background: #e3f2fd; }

/* 操作栏 */
.form-actions { display: flex; justify-content: flex-end; gap: 12px; padding: 20px 28px; background: white; border-radius: 12px; border: 1px solid var(--border); }
.btn-ghost { background: white; border: 1px solid var(--border); color: var(--text); border-radius: 8px; padding: 10px 24px; font-size: 14px; cursor: pointer; transition: all .15s; }
.btn-ghost:hover { border-color: var(--danger); color: var(--danger); }
.btn-submit { min-width: 120px; padding: 10px 28px; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; justify-content: center; }
.spin { animation: spin .8s linear infinite; display: inline-block; }
@keyframes spin { to { transform: rotate(360deg); } }
</style> 