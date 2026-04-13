<template>
  <div class="automation-view">
    <div class="tabs">
      <button v-for="t in tabs" :key="t.key" class="tab" :class="{ active: activeTab === t.key }" @click="activeTab = t.key">{{ t.icon }} {{ t.label }}</button>
    </div>

    <section v-show="activeTab==='datasets'" class="card panel">
      <div class="head"><div><h3>参数化数据集</h3><p>上传 CSV / Excel，用 <code>${列名}</code> 驱动接口/平台内 UI/外部脚本调度。</p></div><button class="btn btn-primary" @click="openUpload">+ 上传数据集</button></div>
      <div v-if="loadingDatasets" class="empty-state">加载中...</div>
      <table v-else class="table"><thead><tr><th>ID</th><th>名称</th><th>行数</th><th>列</th><th>操作</th></tr></thead><tbody>
        <tr v-for="item in datasets" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.row_count }}</td><td class="mono ellipsis" :title="(item.columns || []).join(', ')">{{ (item.columns || []).join(', ') || '-' }}</td><td><button class="btn-action btn-info" @click="previewDs(item)">预览</button><button class="btn-action btn-danger" @click="removeDataset(item)">删除</button></td></tr>
        <tr v-if="!datasets.length"><td colspan="5" class="empty-state">暂无参数化数据集</td></tr>
      </tbody></table>
    </section>

    <section v-show="activeTab==='projects'" class="card panel">
      <div class="head"><div><h3>UI用例项目</h3><p>登记 Playwright 仓库与默认命令。</p></div><button class="btn btn-primary" @click="openProjectDialog()">+ 新建项目</button></div>
      <table class="table"><thead><tr><th>ID</th><th>名称</th><th>仓库路径</th><th>默认命令</th><th>操作</th></tr></thead><tbody>
        <tr v-for="item in projects" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td class="mono ellipsis" :title="item.local_repo_path">{{ item.local_repo_path || '-' }}</td><td class="mono ellipsis" :title="item.test_command">{{ item.test_command }}</td><td><button class="btn-action" @click="openProjectDialog(item)">编辑</button><button class="btn-action btn-danger" @click="removeProject(item)">删除</button></td></tr>
        <tr v-if="!projects.length"><td colspan="5" class="empty-state">暂无UI用例项目</td></tr>
      </tbody></table>
    </section>

    <section v-show="activeTab==='suites'" class="card panel">
      <div class="head"><div><h3>UI用例套件</h3><p>配置套件路径和可选的覆盖命令。</p></div><button class="btn btn-primary" @click="openSuiteDialog()" :disabled="!projects.length">+ 新建套件</button></div>
      <table class="table"><thead><tr><th>ID</th><th>名称</th><th>所属项目</th><th>执行路径</th><th>操作</th></tr></thead><tbody>
        <tr v-for="item in suites" :key="item.id"><td>{{ item.id }}</td><td>{{ item.name }}</td><td>{{ item.automation_project_name }}</td><td class="mono">{{ item.suite_path || '-' }}</td><td><button class="btn-action btn-info" @click="openRunDialog(item)">执行</button><button class="btn-action" @click="openSuiteDialog(item)">编辑</button><button class="btn-action btn-danger" @click="removeSuite(item)">删除</button></td></tr>
        <tr v-if="!suites.length"><td colspan="5" class="empty-state">暂无UI用例套件</td></tr>
      </tbody></table>
    </section>

    <section v-show="activeTab==='runs'" class="card panel">
      <div class="head"><div><h3>执行记录</h3><p>查看运行状态、命令和日志路径。</p></div><button class="btn btn-refresh" @click="loadRuns">↻ 刷新</button></div>
      <table class="table"><thead><tr><th>ID</th><th>套件</th><th>状态</th><th>分支</th><th>命令</th><th>日志</th></tr></thead><tbody>
        <tr v-for="item in runs" :key="item.id"><td>{{ item.id }}</td><td><a class="link-text" @click.prevent="viewRun(item.id)">{{ item.suite_name }}</a></td><td><span class="status" :class="'s-'+item.status">{{ item.status }}</span></td><td>{{ item.branch || '-' }}</td><td class="mono ellipsis" :title="item.command">{{ item.command || '-' }}</td><td class="mono ellipsis" :title="item.log_path">{{ item.log_path || '-' }}</td></tr>
        <tr v-if="!runs.length"><td colspan="6" class="empty-state">暂无执行记录</td></tr>
      </tbody></table>
    </section>

    <div v-if="showProjectDialog" class="modal" @click.self="closeProjectDialog"><div class="modal-content modal-medium"><h3>{{ projectEditing ? '编辑UI用例项目' : '新建UI用例项目' }}</h3><div class="form-group"><label>名称</label><input v-model="projectForm.name" /></div><div class="form-group"><label>关联项目</label><select v-model="projectForm.project"><option :value="null">不关联</option><option v-for="p in projectOptions" :key="p.id" :value="p.id">{{ p.name }}</option></select></div><div class="form-group"><label>本地仓库路径</label><input v-model="projectForm.local_repo_path" placeholder="/path/to/playwright-repo" /></div><div class="form-group"><label>默认分支</label><input v-model="projectForm.default_branch" /></div><div class="form-group"><label>安装命令</label><input v-model="projectForm.install_command" /></div><div class="form-group"><label>测试命令</label><input v-model="projectForm.test_command" /></div><div class="actions"><button class="btn" @click="closeProjectDialog">取消</button><button class="btn btn-primary" @click="submitProject">保存</button></div></div></div>

    <div v-if="showSuiteDialog" class="modal" @click.self="closeSuiteDialog"><div class="modal-content modal-medium"><h3>{{ suiteEditing ? '编辑UI用例套件' : '新建UI用例套件' }}</h3><div class="form-group"><label>名称</label><input v-model="suiteForm.name" /></div><div class="form-group"><label>所属UI用例项目</label><select v-model="suiteForm.automation_project"><option v-for="p in projects" :key="p.id" :value="p.id">{{ p.name }}</option></select></div><div class="form-group"><label>执行路径</label><input v-model="suiteForm.suite_path" placeholder="tests/smoke/login.spec.ts" /></div><div class="form-group"><label>覆盖命令</label><input v-model="suiteForm.command_override" placeholder="留空则使用项目默认命令" /></div><div class="actions"><button class="btn" @click="closeSuiteDialog">取消</button><button class="btn btn-primary" @click="submitSuite">保存</button></div></div></div>

    <div v-if="showRunDialog && currentSuite" class="modal" @click.self="closeRunDialog"><div class="modal-content modal-medium"><h3>执行套件：{{ currentSuite.name }}</h3><div class="form-group"><label>环境</label><select v-model="runForm.environment"><option :value="null">不指定环境</option><option v-for="env in environments" :key="env.id" :value="env.id">{{ env.name }}</option></select></div><div class="form-group"><label>分支</label><input v-model="runForm.branch" /></div><div class="form-group"><label>Base URL</label><input v-model="runForm.base_url" placeholder="https://test.example.com" /></div><div class="form-group"><label>执行命令</label><input v-model="runForm.command" placeholder="留空走默认命令" /></div><div class="actions"><button class="btn" @click="closeRunDialog">取消</button><button class="btn btn-primary" @click="submitRun">开始执行</button></div></div></div>

    <div v-if="showUpload" class="modal" @click.self="showUpload = false"><div class="modal-content modal-medium"><h3>上传参数化数据集</h3><div class="form-group"><label>数据集名称</label><input v-model="uploadForm.name" placeholder="如：登录测试数据" /></div><div class="form-group"><label>文件</label><div class="drop-zone" :class="{ 'drop-active': isDragging }" @dragover.prevent="isDragging = true" @dragleave="isDragging = false" @drop.prevent="onDrop" @click="fileInput.click()"><span v-if="uploadForm.file">✅ {{ uploadForm.file.name }}</span><span v-else>点击或拖拽 CSV / Excel 文件到这里</span></div><input ref="fileInput" type="file" accept=".csv,.xlsx,.xls" style="display:none" @change="onFileChange" /></div><div class="actions"><button class="btn" @click="showUpload = false">取消</button><button class="btn btn-primary" @click="doUpload" :disabled="uploading">{{ uploading ? '上传中...' : '确认上传' }}</button></div></div></div>

    <div v-if="previewTarget" class="modal" @click.self="previewTarget = null"><div class="modal-content modal-medium"><h3>预览：{{ previewTarget.name }}</h3><div class="preview-table-wrap"><table class="table"><thead><tr><th>#</th><th v-for="col in previewTarget.columns" :key="col">{{ col }}</th></tr></thead><tbody><tr v-for="(row, i) in (previewTarget.rows || []).slice(0, 10)" :key="i"><td>{{ i + 1 }}</td><td v-for="(val, j) in row" :key="j">{{ val }}</td></tr></tbody></table></div><div class="actions"><button class="btn" @click="previewTarget = null">关闭</button></div></div></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { alert } from '@/composables/useAlert'
import { confirm } from '@/composables/useConfirm'
import { getProjects } from '@/api/project'
import { getEnvironments } from '@/api/suite'
import { getAutomationProjects, createAutomationProject, updateAutomationProject, deleteAutomationProject, getAutomationSuites, createAutomationSuite, updateAutomationSuite, deleteAutomationSuite, runAutomationSuite, getAutomationRuns } from '@/api/automation'
import { getDataSets, uploadDataSet, deleteDataSet } from '@/api/dataset'

const userStore = useUserStore()
const router = useRouter()
const tabs = [
  { key: 'datasets', label: '参数化数据集', icon: '📋' },
  { key: 'projects', label: '外部脚本项目', icon: '📁' },
  { key: 'suites', label: '外部脚本套件', icon: '🧪' },
  { key: 'runs', label: '执行记录', icon: '📈' },
]
const activeTab = ref('datasets')
const projects = ref([]), suites = ref([]), runs = ref([]), projectOptions = ref([]), environments = ref([])
const datasets = ref([])
const loadingDatasets = ref(false)
const previewTarget = ref(null)
const showUpload = ref(false)
const uploading = ref(false)
const isDragging = ref(false)
const fileInput = ref(null)
const uploadForm = ref({ name: '', file: null })
const showProjectDialog = ref(false), showSuiteDialog = ref(false), showRunDialog = ref(false)
const projectEditing = ref(null), suiteEditing = ref(null), currentSuite = ref(null)
const projectForm = ref({ name: '', project: null, local_repo_path: '', default_branch: 'main', install_command: 'npm install', test_command: 'npx playwright test', product_line: null })
const suiteForm = ref({ name: '', automation_project: null, suite_path: '', command_override: '', enabled: true })
const runForm = ref({ environment: null, branch: 'main', base_url: '', command: '' })

const pl = () => userStore.currentProductLine?.id || null
const formatDate = (v) => v ? new Date(v).toLocaleString('zh-CN') : '-'
const resetProject = () => { projectForm.value = { name: '', project: null, local_repo_path: '', default_branch: 'main', install_command: 'npm install', test_command: 'npx playwright test', product_line: pl() } }
const resetSuite = () => { suiteForm.value = { name: '', automation_project: projects.value[0]?.id || null, suite_path: '', command_override: '', enabled: true } }
const resetRun = () => { runForm.value = { environment: null, branch: 'main', base_url: '', command: '' } }

const loadProjects = async () => { const r = await getAutomationProjects({ product_line: pl(), page_size: 100 }); projects.value = r.result?.list || [] }
const loadSuites = async () => { const r = await getAutomationSuites({ product_line: pl(), page_size: 100 }); suites.value = r.result?.list || [] }
const loadRuns = async () => { const r = await getAutomationRuns({ product_line: pl(), page_size: 100 }); runs.value = r.result?.list || [] }
const loadDatasets = async () => {
  loadingDatasets.value = true
  try {
    const r = await getDataSets({})
    datasets.value = r.result?.list || r.result || r || []
  } finally {
    loadingDatasets.value = false
  }
}
const loadAux = async () => { const [pr, env] = await Promise.all([getProjects({ product_line: pl(), page_size: 200 }), getEnvironments({ product_line: pl(), page_size: 200 })]); projectOptions.value = pr.result?.list || []; environments.value = env.result?.list || [] }

const openUpload = () => { uploadForm.value = { name: '', file: null }; showUpload.value = true }
const onFileChange = (e) => { uploadForm.value.file = e.target.files[0] || null }
const onDrop = (e) => { isDragging.value = false; uploadForm.value.file = e.dataTransfer.files[0] || null }
const doUpload = async () => {
  if (!uploadForm.value.file) return alert('请选择要上传的文件')
  const defaultProjectId = projectOptions.value[0]?.id
  if (!defaultProjectId) return alert('当前产品线下没有可用项目，无法上传数据集')
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', uploadForm.value.file)
    fd.append('project', defaultProjectId)
    if (uploadForm.value.name) fd.append('name', uploadForm.value.name)
    await uploadDataSet(fd)
    showUpload.value = false
    await loadDatasets()
  } catch (e) {
    await alert('上传失败：' + (e.response?.data?.message || e.message))
  } finally {
    uploading.value = false
  }
}
const previewDs = (ds) => { previewTarget.value = ds }
const removeDataset = async (item) => { if (!await confirm(`确定删除参数集「${item.name}」吗？`, { type: 'danger' })) return; await deleteDataSet(item.id); await loadDatasets() }

const openProjectDialog = (item = null) => { projectEditing.value = item; item ? projectForm.value = { ...item } : resetProject(); showProjectDialog.value = true }
const closeProjectDialog = () => { showProjectDialog.value = false; projectEditing.value = null; resetProject() }
const submitProject = async () => { if (!projectForm.value.name?.trim()) return alert('项目名称不能为空'); projectForm.value.product_line = pl(); projectEditing.value ? await updateAutomationProject(projectEditing.value.id, projectForm.value) : await createAutomationProject(projectForm.value); closeProjectDialog(); await loadProjects() }
const removeProject = async (item) => { if (!await confirm(`确定删除UI用例项目「${item.name}」吗？`, { type: 'danger' })) return; await deleteAutomationProject(item.id); await Promise.all([loadProjects(), loadSuites(), loadRuns()]) }

const openSuiteDialog = (item = null) => { suiteEditing.value = item; item ? suiteForm.value = { ...item } : resetSuite(); showSuiteDialog.value = true }
const closeSuiteDialog = () => { showSuiteDialog.value = false; suiteEditing.value = null; resetSuite() }
const submitSuite = async () => { if (!suiteForm.value.name?.trim()) return alert('套件名称不能为空'); suiteEditing.value ? await updateAutomationSuite(suiteEditing.value.id, suiteForm.value) : await createAutomationSuite(suiteForm.value); closeSuiteDialog(); await loadSuites() }
const removeSuite = async (item) => { if (!await confirm(`确定删除UI用例套件「${item.name}」吗？`, { type: 'danger' })) return; await deleteAutomationSuite(item.id); await Promise.all([loadSuites(), loadRuns()]) }

const openRunDialog = (suite) => { currentSuite.value = suite; resetRun(); showRunDialog.value = true }
const viewRun = (id) => router.push(`/automation/runs/${id}`)
const closeRunDialog = () => { showRunDialog.value = false; currentSuite.value = null; resetRun() }
const submitRun = async () => { if (!currentSuite.value) return; const res = await runAutomationSuite(currentSuite.value.id, runForm.value); closeRunDialog(); activeTab.value = 'runs'; await loadRuns(); alert(`已提交执行，Run ID: ${res.run_id}`) }

onMounted(async () => { resetProject(); resetSuite(); await Promise.all([loadProjects(), loadSuites(), loadRuns(), loadAux(), loadDatasets()]) })
</script>

<style scoped>
.tabs{display:flex;gap:8px;margin-bottom:16px}.tab{border:none;background:#eef3ff;color:#3556a8;border-radius:10px;padding:10px 16px;font-weight:700;cursor:pointer}.tab.active{background:#2f5fd0;color:#fff}.panel{padding:20px}.head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.head h3{margin:0}.head p{margin:4px 0 0;color:var(--text-light);font-size:12px}.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}.ellipsis{max-width:260px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.status{display:inline-flex;padding:4px 10px;border-radius:999px;font-size:12px;font-weight:700}.s-pending{background:#eef2ff;color:#3949ab}.s-running{background:#fff3e0;color:#ef6c00}.s-passed{background:#e8f7ee;color:#1f8f52}.s-failed,.s-error{background:#fdecec;color:#c0392b}.modal-medium{width:min(720px,92vw)}.form-group{margin-bottom:14px}.form-group label{display:block;margin-bottom:6px;font-size:13px;font-weight:600}.form-group input,.form-group select{width:100%;border:1px solid var(--border);border-radius:8px;padding:10px 12px;font-size:14px}.actions{display:flex;justify-content:flex-end;gap:10px;margin-top:16px}.empty-state{text-align:center;color:var(--text-light);padding:24px}.btn-action{padding:6px 10px;border:none;border-radius:6px;cursor:pointer;background:#eef3ff;color:#3556a8;margin-right:6px}.btn-action.btn-info{background:#e8f7ff;color:#0b70b7}.btn-action.btn-danger{background:#fdecec;color:#c0392b}.drop-zone{border:2px dashed #c0c0c0;border-radius:10px;padding:24px;text-align:center;cursor:pointer;color:#999;font-size:14px;transition:border-color .2s,background .2s}.drop-zone:hover,.drop-active{border-color:#1677ff;background:#f0f7ff;color:#1677ff}.preview-table-wrap{overflow:auto;max-height:60vh}
</style>
