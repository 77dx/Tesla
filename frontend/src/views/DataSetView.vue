<template>
  <div class="dataset-view">
    <div class="toolbar">
      <span class="page-title"><span class="title-icon">📋</span> 参数化数据集</span>
      <span class="page-hint">上传 CSV / Excel，用 <code>${列名}</code> 引用，实现数据驱动测试（DDT）</span>
      <button @click="openUpload" class="btn btn-primary">+ 上传数据集</button>
    </div>

    <div class="example-card card">
      <div class="example-title">示例：如何编写参数化</div>
      <div class="example-text">1）数据集列名：<code>username</code>、<code>password</code>、<code>expected_code</code>；2）在用例参数中写 <code>${username}</code> / <code>${password}</code>；3）断言里写 <code>${expected_code}</code>。</div>
      <pre class="example-code">{
  "json": {
    "username": "${username}",
    "password": "${password}"
  },
  "headers": {
    "X-Trace-Id": "${trace_id}"
  }
}</pre>
    </div>

    <div v-if="loading" class="loading-state">加载中...</div>
    <div v-else-if="!datasets.length" class="empty-state">
      <div class="empty-icon">📂</div>
      <p>暂无数据集，点击「上传数据集」导入 CSV 或 Excel 文件</p>
    </div>
    <div v-else class="ds-grid">
      <div v-for="ds in datasets" :key="ds.id" class="ds-card card">
        <div class="ds-card-header">
          <span class="ds-name">{{ ds.name }}</span>
          <span class="ds-badge">{{ ds.row_count }} 行</span>
        </div>
        <div class="ds-meta">
          <span class="ds-cols">列：{{ (ds.columns || []).join('、') }}</span>
        </div>
        <div class="ds-footer">
          <span class="ds-date">{{ formatDate(ds.created_at) }}</span>
          <div class="ds-actions">
            <button @click="previewDs(ds)" class="btn btn-sm btn-secondary">预览</button>
            <button @click="deleteDs(ds)" class="btn btn-sm btn-danger">删除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传弹框 -->
    <div v-if="showUpload" class="modal-overlay" @click.self="showUpload = false">
      <div class="modal-box">
        <h3>上传参数化数据集</h3>
        <div class="form-group">
          <label>数据集名称（可选，默认文件名）</label>
          <input v-model="uploadForm.name" class="form-input" placeholder="如：登录测试数据"/>
        </div>
        <div class="form-group">
          <label>文件 * <span class="hint">支持 .csv / .xlsx / .xls，第一行为列名</span></label>
          <div
            class="drop-zone"
            :class="{ 'drop-active': isDragging }"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            @drop.prevent="onDrop"
            @click="fileInput.click()"
          >
            <span v-if="uploadForm.file">✅ {{ uploadForm.file.name }}</span>
            <span v-else>点击或拖拽文件到此处</span>
          </div>
          <input ref="fileInput" type="file" accept=".csv,.xlsx,.xls" style="display:none" @change="onFileChange"/>
        </div>
        <div class="modal-footer">
          <button @click="showUpload = false" class="btn btn-secondary">取消</button>
          <button @click="doUpload" class="btn btn-primary" :disabled="uploading">
            {{ uploading ? '上传中...' : '确认上传' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 预览弹框 -->
    <div v-if="previewTarget" class="modal-overlay" @click.self="previewTarget = null">
      <div class="modal-box modal-wide">
        <h3>预览：{{ previewTarget.name }} <span class="ds-badge">共 {{ previewTarget.row_count }} 行</span></h3>
        <div class="preview-hint">仅显示前 10 行。用 <code>${列名}</code> 在用例/套件中引用该列值。</div>
        <div class="preview-table-wrap">
          <table class="preview-table">
            <thead>
              <tr>
                <th>#</th>
                <th v-for="col in previewTarget.columns" :key="col"><code>${{ '{' }}{{ col }}{{ '}' }}</code></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, i) in (previewTarget.rows || []).slice(0, 10)" :key="i">
                <td class="row-num">{{ i + 1 }}</td>
                <td v-for="(val, j) in row" :key="j">{{ val }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="modal-footer">
          <button @click="previewTarget = null" class="btn btn-secondary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { getDataSets, uploadDataSet, deleteDataSet } from '@/api/dataset'
import { getProjects } from '@/api/project'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'

const userStore     = useUserStore()
const datasets      = ref([])
const projects      = ref([])
const loading       = ref(false)
const showUpload    = ref(false)
const uploading     = ref(false)
const isDragging    = ref(false)
const previewTarget = ref(null)
const fileInput     = ref(null)
const uploadForm    = ref({ name: '', file: null })

const load = async () => {
  loading.value = true
  try {
    const res = await getDataSets({})
    datasets.value = res.result?.list || res.result || res || []
  } finally {
    loading.value = false
  }
}

const loadProjects = async () => {
  const params = { page_size: 200 }
  if (userStore.currentProductLine?.id) params.product_line = userStore.currentProductLine.id
  const res = await getProjects(params)
  projects.value = res.result?.list || res.result || res || []
}

onMounted(() => { load(); loadProjects() })

const openUpload = () => {
  uploadForm.value = { name: '', file: null }
  showUpload.value = true
}

const onFileChange = (e) => { uploadForm.value.file = e.target.files[0] || null }
const onDrop = (e) => { isDragging.value = false; uploadForm.value.file = e.dataTransfer.files[0] || null }

const doUpload = async () => {
  if (!uploadForm.value.file) return alert('请选择要上传的文件')
  const defaultProjectId = projects.value[0]?.id
  if (!defaultProjectId) return alert('当前产品线下没有可用项目，无法上传数据集')
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', uploadForm.value.file)
    fd.append('project', defaultProjectId)
    if (uploadForm.value.name) fd.append('name', uploadForm.value.name)
    await uploadDataSet(fd)
    showUpload.value = false
    await load()
  } catch (e) {
    await alert('上传失败：' + (e.response?.data?.message || e.message))
  } finally {
    uploading.value = false
  }
}

const previewDs = (ds) => { previewTarget.value = ds }

const deleteDs = async (ds) => {
  const ok = await confirm(`确定删除参数集「${ds.name}」吗？`, { type: 'danger' })
  if (!ok) return
  try {
    await deleteDataSet(ds.id)
    await load()
  } catch (e) {
    await alert('删除失败：' + (e.response?.data?.message || e.message))
  }
}

const formatDate = (s) => s ? new Date(s).toLocaleString('zh-CN', { hour12: false }).slice(0, 16) : '-'
</script>

<style scoped>
.dataset-view { padding: 24px; }
.toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.page-title { font-size: 20px; font-weight: 700; color: var(--text, #1a1a1a); display:flex; align-items:center; gap:6px; }
.title-icon { font-size: 22px; }
.page-hint  { flex: 1; font-size: 13px; color: var(--text-light, #888); }
.page-hint code { background:#f0f0f0; padding:1px 5px; border-radius:4px; font-size:12px; }

.filter-bar { margin-bottom: 18px; }
.filter-select { padding: 6px 12px; border-radius: 8px; border: 1px solid var(--border,#ddd); font-size:13px; }

.loading-state, .empty-state { text-align:center; padding:60px 0; color:var(--text-light,#999); }
.empty-icon { font-size: 48px; margin-bottom: 12px; }

.ds-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }
.ds-card { padding: 18px 20px; border-radius: 12px; border: 1px solid var(--border,#e8e8e8); background:#fff; transition: box-shadow .2s; }
.ds-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,.08); }
.ds-card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:8px; }
.ds-name { font-size:15px; font-weight:600; color:var(--text,#1a1a1a); }
.ds-badge { background:#e8f4ff; color:#1677ff; font-size:12px; padding:2px 8px; border-radius:20px; font-weight:600; }
.ds-meta { display:flex; flex-direction:column; gap:4px; margin-bottom:12px; }
.ds-project { font-size:12px; color:#888; }
.ds-cols { font-size:12px; color:#555; word-break:break-all; }
.ds-footer { display:flex; align-items:center; justify-content:space-between; }
.ds-date { font-size:12px; color:#aaa; }
.ds-actions { display:flex; gap:8px; }
.btn-sm { padding: 4px 10px !important; font-size: 12px !important; }

.modal-overlay { position:fixed; inset:0; background:rgba(0,0,0,.45); display:flex; align-items:center; justify-content:center; z-index:1000; }
.modal-box { background:#fff; border-radius:14px; padding:28px; width:90%; max-width:480px; max-height:85vh; overflow-y:auto; box-shadow:0 8px 32px rgba(0,0,0,.18); animation: slideUp .22s ease; }
.modal-wide { max-width: 780px; }
.modal-box h3 { margin:0 0 20px; font-size:17px; font-weight:700; display:flex; align-items:center; gap:10px; }
.form-group { margin-bottom: 14px; }
.form-group label { display:block; font-size:13px; color:#555; margin-bottom:6px; }
.form-input { width:100%; padding:8px 12px; border-radius:8px; border:1px solid var(--border,#ddd); font-size:14px; box-sizing:border-box; }
.hint { font-size:11px; color:#999; }
.drop-zone { border:2px dashed #c0c0c0; border-radius:10px; padding:24px; text-align:center; cursor:pointer; color:#999; font-size:14px; transition:border-color .2s,background .2s; }
.drop-zone:hover, .drop-active { border-color:#1677ff; background:#f0f7ff; color:#1677ff; }
.modal-footer { display:flex; justify-content:flex-end; gap:10px; margin-top:20px; }
.preview-hint { font-size:13px; color:#888; margin-bottom:12px; }
.preview-hint code { background:#f0f0f0; padding:1px 5px; border-radius:4px; }
.preview-table-wrap { overflow-x:auto; }
.preview-table { width:100%; border-collapse:collapse; font-size:13px; }
.preview-table th { background:#f5f7fa; padding:8px 12px; border:1px solid #e8e8e8; text-align:left; }
.preview-table td { padding:7px 12px; border:1px solid #e8e8e8; }
.preview-table th code { background:#e8f4ff; color:#1677ff; padding:1px 6px; border-radius:4px; font-size:12px; }
.row-num { color:#bbb; font-size:12px; text-align:center; width:36px; }
@keyframes slideUp { from { opacity:0; transform:translateY(20px) } to { opacity:1; transform:translateY(0) } }
</style>
