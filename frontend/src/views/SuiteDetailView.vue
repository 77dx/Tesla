<template>
  <div class="suite-detail">
    <div class="detail-header">
      <button @click="$router.push('/suites')" class="btn btn-back">← 返回</button>
      <div class="header-actions">
        <button v-if="!editing" @click="goToResults" class="btn btn-refresh">执行结果</button>
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
            <div class="info-item"><label>所属产品线</label><span>{{ suite.product_line_name || '-' }}</span></div>
            <div class="info-item">
              <label>运行类型</label>
              <span class="type-badge" :class="'type-' + suite.run_type">{{ { O:'手动执行', C:'定时执行', W:'WebHook' }[suite.run_type] }}</span>
            </div>
            <div v-if="suite.cron" class="info-item"><label>Cron</label><code>{{ suite.cron }}</code></div>
            <div v-if="suite.run_type === 'C'" class="info-item"><label>下次执行</label><span>{{ formatDate(suite.cron_next_run_at) }}</span></div>
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
            <div class="phase-header-right">
              <button @click="openAddCaseDialog('API','setup')" class="btn btn-sm phase-add-btn">+ API</button>
              <button @click="openAddCaseDialog('UI','setup')" class="btn btn-sm">+ UI</button>
            </div>
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
            <div class="phase-header-right">
              <button @click="openAddCaseDialog('API','teardown')" class="btn btn-sm phase-add-btn">+ API</button>
              <button @click="openAddCaseDialog('UI','teardown')" class="btn btn-sm">+ UI</button>
            </div>
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

      <!-- Tab: 执行日志 -->
      <div v-show="activeTab === 'logs'" class="card execution-log-card">
        <div class="execution-log-header">
          <div>
            <div class="execution-log-title">执行日志</div>
            <div class="execution-log-hint">定时执行按同一策略聚合统计，手动立即执行单独记录。</div>
          </div>
          <div class="execution-log-toolbar">
            <label class="mini-check">
              <input type="checkbox" v-model="showFailedLogsOnly" />
              <span>仅看失败策略</span>
            </label>
            <select v-model="logSortMode" class="log-sort-select">
              <option value="risk">失败优先</option>
              <option value="recent">最近执行优先</option>
            </select>
            <button class="btn btn-sm" @click="loadExecutionLogs">刷新</button>
          </div>
        </div>
        <div v-if="visibleExecutionLogs.length" class="execution-log-list">
          <div v-for="log in visibleExecutionLogs" :key="log.id" class="execution-log-item" :class="{ collapsed: isLogCollapsed(log.id) }">
            <div class="execution-log-main">
              <div class="execution-log-topline">
                <span class="execution-log-type" :class="'type-' + log.strategy_type">{{ getStrategyTypeText(log.strategy_type) }}</span>
                <strong class="execution-log-label">{{ log.strategy_label || '-' }}</strong>
                <button class="collapse-toggle-btn" @click="toggleLogCollapsed(log.id)">{{ isLogCollapsed(log.id) ? '展开摘要' : '折叠摘要' }}</button>
              </div>
              <template v-if="!isLogCollapsed(log.id)">
              <div class="execution-log-metrics">
                <span class="metric-chip metric-total">总计 {{ log.execution_count || 0 }}</span>
                <span class="metric-chip metric-pass">通过 {{ log.pass_count || 0 }}</span>
                <span class="metric-chip metric-fail">失败 {{ log.fail_count || 0 }}</span>
                <span class="metric-chip metric-rate">成功率 {{ getPassRateText(log) }}</span>
              </div>
              <div class="execution-log-meta">
                <span>策略：{{ getStrategyHint(log) }}</span>
                <span>首次执行：{{ formatDate(log.first_triggered_at) }}</span>
                <span>最近执行：{{ formatDate(log.last_triggered_at) }}</span>
              </div>
              <div v-if="log.latest_failed_result?.id" class="execution-log-failure">
                最近失败：
                <button class="inline-result-link" @click="viewResult(log.latest_failed_result.id)">#{{ log.latest_failed_result.id }}</button>
                <span>{{ formatDate(log.latest_failed_result.created_at) }}</span>
                <span class="failure-time-tag">{{ formatRelativeTime(log.latest_failed_result.created_at) }}</span>
              </div>
              <div v-if="getLogRiskHint(log)" class="risk-banner" :class="'risk-' + getLogRiskHint(log).level">
                {{ getLogRiskHint(log).text }}
              </div>
              <div v-if="log.failure_summary" class="execution-log-summary" v-html="highlightFailureSummary(log.failure_summary)"></div>
              <div v-if="log.recent_results?.length" class="execution-log-results">
                <button v-for="item in log.recent_results" :key="item.id" class="result-link-chip" @click="viewResult(item.id)">
                  #{{ item.id }} · {{ item.trigger_source === 'cron' ? '定时' : item.trigger_source === 'manual' ? '手动' : item.trigger_source || '-' }} · {{ formatDate(item.created_at) }}
                </button>
              </div>
              <div class="execution-log-actions-row">
                <button class="btn btn-sm" @click="toggleLogHistory(log)">{{ isLogExpanded(log.id) ? '收起历史结果' : '展开完整历史' }}</button>
                <button v-if="log.latest_failed_result?.id" class="btn btn-sm btn-danger-soft" @click="viewResult(log.latest_failed_result.id)">跳到最近失败</button>
                <span v-if="getFailureStreak(log) >= 2" class="streak-chip">连续失败 {{ getFailureStreak(log) }} 次</span>
              </div>
              <div v-if="isLogExpanded(log.id)" class="execution-log-history">
                <div class="history-filter-bar">
                  <span>历史筛选</span>
                  <button class="mini-filter-btn" :class="{ active: historyStatusFilter === 'all' }" @click="historyStatusFilter = 'all'">全部</button>
                  <button class="mini-filter-btn" :class="{ active: historyStatusFilter === 'fail' }" @click="historyStatusFilter = 'fail'">仅失败</button>
                  <button class="mini-filter-btn" :class="{ active: historyStatusFilter === 'pass' }" @click="historyStatusFilter = 'pass'">仅通过</button>
                </div>
                <div v-if="getFilteredLogHistoryItems(log.id).length" class="execution-log-history-list">
                  <button v-for="item in getFilteredLogHistoryItems(log.id)" :key="item.id" class="history-result-row" @click="viewResult(item.id)">
                    <span class="history-result-id">#{{ item.id }}</span>
                    <span>{{ item.trigger_source === 'cron' ? '定时' : item.trigger_source === 'manual' ? '手动' : item.trigger_source || '-' }}</span>
                    <span>{{ item.status === 4 ? (item.is_pass ? '通过' : '失败') : getStatusText(item.status) }}</span>
                    <span class="history-time-block">
                      <strong>{{ formatDate(item.created_at) }}</strong>
                      <em>{{ formatRelativeTime(item.created_at) }}</em>
                    </span>
                  </button>
                  <div class="history-pagination-bar">
                    <span>已加载 {{ getLogHistoryState(log.id).items.length }} / {{ getLogHistoryState(log.id).itemCount }} 条</span>
                    <button v-if="getLogHistoryState(log.id).page < getLogHistoryState(log.id).pageCount" class="btn btn-sm" :disabled="isLogHistoryLoading(log.id)" @click="loadMoreLogHistory(log)">{{ isLogHistoryLoading(log.id) ? '加载中...' : '加载更多' }}</button>
                  </div>
                </div>
                <div v-else class="empty-state">{{ isLogHistoryLoading(log.id) ? '加载中...' : '当前筛选下暂无历史结果' }}</div>
              </div>
              </template>
              <div v-else class="collapsed-log-summary">
                <span>最近执行：{{ formatDate(log.last_triggered_at) }}</span>
                <span>成功率：{{ getPassRateText(log) }}</span>
                <span v-if="log.fail_count > 0">失败 {{ log.fail_count }} 次</span>
              </div>
            </div>
            <div class="execution-log-side">
              <button v-if="log.latest_result?.id" class="btn btn-primary btn-sm" @click="viewResult(log.latest_result.id)">查看最新结果</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">暂无执行日志</div>
      </div>

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
      <div class="selected-count source-hint">{{ addingCaseType === 'UI' ? '来源：平台内 UI 用例库' : '来源：接口用例库' }}</div>
      <div class="add-case-layout">
        <div class="case-tree-panel" v-if="addingCaseType !== 'UI'">
          <div class="case-tree-header">用例层级</div>
          <div class="case-tree-body" v-if="caseTree">
            <div
              v-for="n in visibleCaseTreeNodes"
              :key="n.id"
              class="case-tree-row"
              :class="{ active: n.id === selectedFolderId }"
              :style="{ paddingLeft: (n.level * 16 + 8) + 'px' }"
              @click="selectCaseTreeNode(n)"
            >
              <span class="case-tree-toggle" @click.stop="toggleCaseTreeFolder(n)">
                {{ n.node_type === 'folder' ? (isCaseTreeExpanded(n.id) ? '▾' : '▸') : '' }}
              </span>
              <span>{{ n.node_type === 'folder' ? '📁' : '📄' }} {{ displayTreeNodeName(n) }}</span>
            </div>
          </div>
        </div>

        <div class="case-select-panel">
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
                <div class="avail-topline">
                  <span class="avail-name">{{ c.name }}</span>
                  <span class="avail-type">{{ addingCaseType }}</span>
                </div>
                <span class="avail-endpoint">{{ c.endpoint?.name || c.platform || '' }}</span>
                <span v-if="c.entry_url" class="avail-meta">入口：{{ c.entry_url }}</span>
                <span class="avail-meta">产品线：{{ c.product_line_name || '未设置' }}　项目：{{ c.project_name || '未设置' }}</span>
                <span class="avail-meta">ID：#{{ c.id }}</span>
              </div>
            </div>
            <div v-if="!filteredAvailableCases.length" class="empty-state">当前层级暂无可用用例</div>
          </div>
        </div>
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
      <!-- 参数集选择（提交前） -->
      <div v-if="!runResult.loading && !runResult.success && !runResult.error" class="run-pre-form">
        <div class="form-group">
          <label>参数化数据集（可选）</label>
          <select v-model="selectedDatasetId" class="form-select">
            <option :value="null">不使用参数集（普通执行）</option>
            <option v-for="ds in suiteDatasets" :key="ds.id" :value="ds.id">📋 {{ ds.name }}（{{ ds.row_count }} 行）</option>
          </select>
          <div v-if="selectedDatasetId" class="ds-hint">将循环执行 {{ suiteDatasets.find(d=>d.id===selectedDatasetId)?.row_count }} 行数据，每行执行一遍所有用例</div>
        </div>
        <div class="modal-actions">
          <button @click="showRunDialog=false" class="btn">取消</button>
          <button @click="doRunSuite" class="btn btn-success">▶ 开始执行</button>
        </div>
      </div>
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
  getSuiteDetail, updateSuite, deleteSuite, runSuite as runSuiteApi, getRunResults, getSuiteExecutionLogs,
  getSuiteCaseItems, batchAddCaseItems, deleteCaseItem, updateCaseItem, reorderCaseItems,
  getEnvironments
} from '@/api/suite'
import { getCases, getCaseTree } from '@/api/case'
import { getUICases } from '@/api/uiCase'
import { confirm } from '@/composables/useConfirm'
import { alert } from '@/composables/useAlert'
import { useUserStore } from '@/stores/user'
import { getMyProductLines } from '@/api/productLine'

const userStore = useUserStore()

const route   = useRoute()
const router  = useRouter()
const suiteId = route.params.id

const suite        = ref(null)
const caseItems    = ref([])
const results      = ref([])
const executionLogs = ref([])
const showFailedLogsOnly = ref(false)
const logSortMode = ref('risk')
const historyStatusFilter = ref('all')
const collapsedLogIds = ref(new Set())
const expandedLogIds = ref(new Set())
const logHistoryMap = ref({})
const logHistoryLoadingIds = ref(new Set())
const environments = ref([])
const orderChanged = ref(false)
const editing      = ref(false)
const saving       = ref(false)
const editVars     = ref([])
const activeTab    = ref('info')
const mainTabs = [
  { id: 'info',    label: '基本信息', icon: '📋' },
  { id: 'cases',   label: '执行用例', icon: '▶' },
  { id: 'logs',    label: '执行日志', icon: '🗂' },
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
const suiteDatasets     = ref([])
const caseTree = ref(null)
const selectedFolderId = ref(null)
const caseTreeExpandedFolders = ref(new Set())
const selectedDatasetId = ref(null)
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

const displayTreeNodeName = (node) => node?.name?.trim() || '无名称'
const formatDate = (d) => d ? new Date(d).toLocaleString('zh-CN') : '-'
const formatRelativeTime = (d) => {
  if (!d) return '-'
  const diff = Date.now() - new Date(d).getTime()
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)} 分钟前`
  if (diff < day) return `${Math.floor(diff / hour)} 小时前`
  return `${Math.floor(diff / day)} 天前`
}

const visibleCaseTreeNodes = computed(() => {
  const list = []
  const walk = (node, level = 0) => {
    if (!node) return
    list.push({ ...node, level })
    if (node.node_type === 'folder' && caseTreeExpandedFolders.value.has(node.id)) {
      ;(node.children || []).forEach(c => walk(c, level + 1))
    }
  }
  walk(caseTree.value, 0)
  return list
})

const isCaseTreeExpanded = (id) => caseTreeExpandedFolders.value.has(id)

const toggleCaseTreeFolder = (node) => {
  if (node.node_type !== 'folder') return
  const s = new Set(caseTreeExpandedFolders.value)
  if (s.has(node.id)) s.delete(node.id)
  else s.add(node.id)
  caseTreeExpandedFolders.value = s
}

const selectCaseTreeNode = (node) => {
  if (node.node_type === 'folder') selectedFolderId.value = node.id
}

const loadCaseTree = async () => {
  const res = await getCaseTree()
  const root = res.result || res
  caseTree.value = root
  if (root) {
    const prev = new Set(caseTreeExpandedFolders.value)
    prev.add(root.id)
    caseTreeExpandedFolders.value = prev
    if (!selectedFolderId.value) selectedFolderId.value = root.id
  }
}

const filteredAvailableCases = computed(() => {
  let list = availableCases.value

  if (selectedFolderId.value && caseTree.value) {
    const caseIds = new Set()
    const collectCaseIds = (node) => {
      if (!node) return
      if (node.node_type === 'case' && node.item?.id) {
        caseIds.add(node.item.id)
      }
      ;(node.children || []).forEach(collectCaseIds)
    }
    const findNode = (node, id) => {
      if (!node) return null
      if (node.id === id) return node
      for (const child of (node.children || [])) {
        const found = findNode(child, id)
        if (found) return found
      }
      return null
    }
    const selectedNode = findNode(caseTree.value, selectedFolderId.value)
    if (selectedNode) collectCaseIds(selectedNode)
    list = list.filter(c => caseIds.has(c.id))
  }

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
const getLogSortScore = (log) => {
  const latestFailedAt = log.latest_failed_result?.created_at ? new Date(log.latest_failed_result.created_at).getTime() : 0
  const lastTriggeredAt = log.last_triggered_at ? new Date(log.last_triggered_at).getTime() : 0
  if (logSortMode.value === 'recent') return lastTriggeredAt
  return ((log.fail_count || 0) > 0 ? 10 ** 15 : 0) + latestFailedAt + (getFailureStreak(log) * 10 ** 12)
}
const visibleExecutionLogs = computed(() => {
  const base = showFailedLogsOnly.value ? executionLogs.value.filter(log => (log.fail_count || 0) > 0) : executionLogs.value
  return [...base].sort((a, b) => getLogSortScore(b) - getLogSortScore(a))
})

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

const loadExecutionLogs = async () => {
  const res = await getSuiteExecutionLogs({ suite: suiteId, page_size: 50 })
  executionLogs.value = res.result?.list || res.list || []
}

const isLogExpanded = (id) => expandedLogIds.value.has(id)
const isLogCollapsed = (id) => collapsedLogIds.value.has(id)
const toggleLogCollapsed = (id) => {
  const next = new Set(collapsedLogIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  collapsedLogIds.value = next
}
const isRunResultPass = (item) => item?.status === 4 && !!item?.is_pass
const isRunResultFail = (item) => !isRunResultPass(item)
const getLogHistoryState = (id) => logHistoryMap.value[id] || { items: [], page: 0, pageCount: 1, itemCount: 0 }
const getFilteredLogHistoryItems = (id) => {
  const items = getLogHistoryState(id).items || []
  if (historyStatusFilter.value === 'fail') return items.filter(isRunResultFail)
  if (historyStatusFilter.value === 'pass') return items.filter(isRunResultPass)
  return items
}
const getFailureStreak = (log) => {
  const items = log.recent_results || []
  let streak = 0
  for (const item of items) {
    if (isRunResultFail(item)) streak += 1
    else break
  }
  return streak
}
const getLogRiskHint = (log) => {
  const items = log.recent_results || []
  if (!items.length) return null
  const sample = items.slice(0, 5)
  const failCount = sample.filter(isRunResultFail).length
  if (sample.length >= 3 && failCount === sample.length) {
    return { level: 'danger', text: `高风险：最近 ${sample.length} 次全部失败` }
  }
  if (isRunResultPass(items[0]) && items.slice(1).some(isRunResultFail)) {
    return { level: 'success', text: '已恢复：最近一次执行已通过' }
  }
  if (failCount >= 2) {
    return { level: 'warn', text: `注意：最近 ${sample.length} 次中有 ${failCount} 次失败` }
  }
  return null
}
const isLogHistoryLoading = (id) => logHistoryLoadingIds.value.has(id)
const loadLogHistoryPage = async (log, page = 1, append = false) => {
  const loading = new Set(logHistoryLoadingIds.value)
  loading.add(log.id)
  logHistoryLoadingIds.value = loading
  try {
    const res = await getRunResults({ execution_log: log.id, page, page_size: 10 })
    const list = res.result?.list || res.list || []
    const nextState = {
      items: append ? [...(logHistoryMap.value[log.id]?.items || []), ...list] : list,
      page: res.result?.page || page,
      pageCount: res.result?.pageCount || 1,
      itemCount: res.result?.itemCount || list.length,
    }
    logHistoryMap.value = { ...logHistoryMap.value, [log.id]: nextState }
  } finally {
    const next = new Set(logHistoryLoadingIds.value)
    next.delete(log.id)
    logHistoryLoadingIds.value = next
  }
}
const toggleLogHistory = async (log) => {
  const next = new Set(expandedLogIds.value)
  if (next.has(log.id)) {
    next.delete(log.id)
    expandedLogIds.value = next
    return
  }
  if (!logHistoryMap.value[log.id]) {
    await loadLogHistoryPage(log, 1, false)
  }
  next.add(log.id)
  expandedLogIds.value = next
}
const loadMoreLogHistory = async (log) => {
  const state = getLogHistoryState(log.id)
  if (state.page >= state.pageCount) return
  await loadLogHistoryPage(log, state.page + 1, true)
}

const startEdit = () => {
  const s = suite.value
  formData.value = {
    name:            s.name,
    description:     s.description || '',
    run_type:        s.run_type || 'O',
    cron:            s.cron || '',
    hook_key:        s.hook_key || '',
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
    await updateSuite(suiteId, { ...suite.value, project: null, product_line: suite.value?.product_line || userStore.currentProductLine?.id || null, suite_headers: shObj })
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
    await updateSuite(suiteId, { ...suite.value, project: null, product_line: suite.value?.product_line || userStore.currentProductLine?.id || null, suite_headers: Object.keys(shObj).length ? shObj : null })
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
    await updateSuite(suiteId, { ...suite.value, project: null, product_line: suite.value?.product_line || userStore.currentProductLine?.id || null, suite_variables: svObj })
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
    await updateSuite(suiteId, { ...suite.value, project: null, product_line: suite.value?.product_line || userStore.currentProductLine?.id || null, suite_variables: Object.keys(svObj).length ? svObj : null })
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
      project: null,
      product_line: suite.value?.product_line || userStore.currentProductLine?.id || null,
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
  // 先加载参数集列表，再显示弹框
  try {
    const { getDataSets } = await import('@/api/dataset')
    const suiteDetail = await getSuiteDetail(suiteId)
    const projectId = suiteDetail.result?.project || suiteDetail.project
    const dsRes = await getDataSets({ page_size: 200, project: projectId })
    suiteDatasets.value = dsRes.result?.list || dsRes.result || dsRes || []
  } catch (e) { suiteDatasets.value = [] }
  selectedDatasetId.value = null
  runResult.value = { loading: false, success: false, error: null, result_id: null }
  showRunDialog.value = true
}

const doRunSuite = async () => {
  runResult.value = { loading: true, success: false, error: null, result_id: null }
  try {
    const payload = {}
    if (selectedDatasetId.value) payload.dataset_id = selectedDatasetId.value
    const res = await runSuiteApi(suiteId, payload)
    const resultId = res.result?.result_id || res.result_id
    runResult.value = { loading: false, success: true, error: null, result_id: resultId }
    setTimeout(() => {
      loadResults()
      loadExecutionLogs()
    }, 1500)
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
  addingProductLine.value = caseType === 'UI' ? null : (userStore.currentProductLine?.id || null)
  showAddCaseDialog.value = true

  if (caseType === 'UI') {
    caseTree.value = null
    selectedFolderId.value = null
  } else {
    await loadCaseTree()
  }

  // 加载所有产品线供切换筛选
  if (!addingProductLines.value.length) {
    try {
      const pr = await getMyProductLines()
      addingProductLines.value = pr.result || pr || []
    } catch (e) { console.error(e) }
  }
  // 加载全部用例（不按产品线过滤，允许跨产品线选择）
  if (caseType === 'UI') {
    availableCases.value = []
    caseTree.value = null
    const res = await getUICases({ page_size: 500 })
    availableCases.value = res.result?.list || res.result || []
  } else {
    const res = await getCases({ page_size: 500 })
    availableCases.value = res.result?.list || []
  }
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

const goToResults = () => router.push(`/results?suite=${suiteId}`)
const viewResult = (id) => { showRunDialog.value = false; router.push(`/results/${id}`) }
const getStrategyTypeText = (type) => ({ manual: '手动立即执行', cron: '定时策略', webhook: 'Webhook' }[type] || type || '-')
const getStrategyHint = (log) => {
  if (log.strategy_type === 'cron') return log.strategy_payload?.cron || log.strategy_key || '-'
  if (log.strategy_type === 'webhook') return log.strategy_payload?.hook_key || log.strategy_key || '-'
  return '每次手动执行独立记录'
}
const getPassRateText = (log) => `${Number(log.pass_rate || 0).toFixed(log.pass_rate % 1 === 0 ? 0 : 2)}%`
const escapeHtml = (text) => String(text ?? '')
  .replaceAll('&', '&amp;')
  .replaceAll('<', '&lt;')
  .replaceAll('>', '&gt;')
  .replaceAll('"', '&quot;')
  .replaceAll("'", '&#39;')
const highlightFailureSummary = (text) => {
  const safe = escapeHtml(text || '')
  if (!safe) return ''
  return safe.replace(/(ASSERT|ERROR|FAILED|EXCEPTION)/gi, '<mark>$1</mark>')
}
const getStatusClass = (s) => ({ 0:'status-init', 1:'status-ready', 2:'status-running', 3:'status-reporting', 4:'status-done', '-1':'status-error' })[s] || 'status-init'
const getStatusText  = (s) => ({ 0:'初始化', 1:'准备开始', 2:'正在执行', 3:'生成报告', 4:'执行完毕', '-1':'执行出错' })[s] || '未知'

onMounted(async () => {
  const [, , , , er] = await Promise.all([
    loadSuite(), loadCaseItems(), loadResults(), loadExecutionLogs(),
    getEnvironments({ page_size: 200 }),
  ])
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
.execution-log-card { padding: 20px; }
.execution-log-header { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; margin-bottom:16px; }
.execution-log-toolbar { display:flex; align-items:center; gap:12px; }
.log-sort-select { border:1px solid var(--border); border-radius:8px; padding:6px 10px; font-size:12px; color:var(--text); background:#fff; }
.mini-check { display:inline-flex; align-items:center; gap:8px; font-size:12px; color:var(--text-light); user-select:none; }
.mini-check input { accent-color: var(--accent); }
.execution-log-title { font-size:18px; font-weight:700; color:var(--primary); }
.execution-log-hint { font-size:12px; color:var(--text-light); margin-top:4px; }
.execution-log-list { display:flex; flex-direction:column; gap:12px; }
.execution-log-item { display:flex; justify-content:space-between; gap:16px; padding:16px; border:1px solid var(--border); border-radius:12px; background:linear-gradient(180deg,#fff,#fbfcff); }
.execution-log-item.collapsed { background:linear-gradient(180deg,#fff,#f7f9fc); }
.execution-log-main { min-width:0; flex:1; display:flex; flex-direction:column; gap:10px; }
.execution-log-topline { display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.collapse-toggle-btn { margin-left:auto; border:none; background:#eef4ff; color:#2458b8; border-radius:999px; padding:5px 10px; font-size:12px; font-weight:700; cursor:pointer; }
.collapse-toggle-btn:hover { background:#dfeaff; }
.execution-log-type { display:inline-flex; align-items:center; padding:4px 10px; border-radius:999px; font-size:12px; font-weight:700; }
.execution-log-type.type-manual { background:#e8f4ff; color:#1565c0; }
.execution-log-type.type-cron { background:#fff3e0; color:#ef6c00; }
.execution-log-type.type-webhook { background:#f3e5f5; color:#7b1fa2; }
.execution-log-label { font-size:14px; color:var(--text); }
.execution-log-meta { display:flex; flex-wrap:wrap; gap:10px 16px; color:var(--text-light); font-size:12px; }
.execution-log-metrics { display:flex; flex-wrap:wrap; gap:8px; }
.metric-chip { display:inline-flex; align-items:center; border-radius:999px; padding:4px 10px; font-size:12px; font-weight:700; }
.metric-total { background:#eef2ff; color:#3949ab; }
.metric-pass { background:#e8f7ee; color:#1f8f52; }
.metric-fail { background:#fdecec; color:#c0392b; }
.metric-rate { background:#fff5e8; color:#ef6c00; }
.execution-log-failure { display:flex; align-items:center; gap:8px; font-size:12px; color:#c0392b; }
.failure-time-tag { display:inline-flex; align-items:center; padding:2px 8px; border-radius:999px; background:#fff1f0; color:#c0392b; font-size:11px; font-weight:700; }
.risk-banner { padding:10px 12px; border-radius:10px; font-size:12px; font-weight:700; }
.risk-banner.risk-danger { background:#fff1f1; color:#b42318; border:1px solid #f4c7c3; }
.risk-banner.risk-warn { background:#fff8e8; color:#b26a00; border:1px solid #f3deab; }
.risk-banner.risk-success { background:#eefbf2; color:#1f7a46; border:1px solid #bfe5cc; }
.execution-log-summary { padding:10px 12px; border-radius:10px; background:#fff4f4; color:#a93226; font-size:12px; line-height:1.6; border:1px solid #f5c6c6; }
.execution-log-summary :deep(mark), .execution-log-summary mark { background:#ffd4d4; color:#8e1b1b; padding:0 4px; border-radius:4px; font-weight:700; }
.inline-result-link { border:none; background:none; color:#1565c0; cursor:pointer; padding:0; font-weight:700; }
.inline-result-link:hover { text-decoration:underline; }
.execution-log-results { display:flex; flex-wrap:wrap; gap:8px; }
.execution-log-actions-row { display:flex; justify-content:flex-start; align-items:center; flex-wrap:wrap; gap:8px; }
.btn-danger-soft { background:#fff2f2; color:#c0392b; border:1px solid #f3c3c0; }
.btn-danger-soft:hover { background:#ffe4e1; }
.streak-chip { display:inline-flex; align-items:center; padding:4px 10px; border-radius:999px; background:#fff0f0; color:#b42318; font-size:12px; font-weight:700; }
.execution-log-history { border-top:1px dashed var(--border); padding-top:12px; }
.history-filter-bar { display:flex; align-items:center; gap:8px; flex-wrap:wrap; margin-bottom:10px; font-size:12px; color:var(--text-light); }
.mini-filter-btn { border:1px solid var(--border); background:#fff; color:var(--text-light); border-radius:999px; padding:4px 10px; font-size:12px; cursor:pointer; }
.mini-filter-btn.active { background:#edf4ff; color:#2458b8; border-color:#bfd2ff; font-weight:700; }
.execution-log-history-list { display:flex; flex-direction:column; gap:8px; }
.history-result-row { display:grid; grid-template-columns:90px 90px 90px 1fr; gap:12px; align-items:center; border:1px solid var(--border); background:#fff; border-radius:10px; padding:10px 12px; text-align:left; cursor:pointer; }
.history-result-row:hover { background:#f8fbff; border-color:#cdddf8; }
.history-result-id { font-weight:700; color:#2458b8; }
.history-time-block { display:flex; flex-direction:column; gap:2px; }
.history-time-block strong { font-size:12px; color:var(--text); font-weight:600; }
.history-time-block em { font-size:11px; color:var(--text-light); font-style:normal; }
.history-pagination-bar { display:flex; justify-content:space-between; align-items:center; gap:12px; padding-top:4px; color:var(--text-light); font-size:12px; }
.collapsed-log-summary { display:flex; flex-wrap:wrap; gap:10px 16px; color:var(--text-light); font-size:12px; }
.result-link-chip { border:1px solid #cfe0ff; background:#f5f9ff; color:#2458b8; border-radius:999px; padding:6px 10px; font-size:12px; cursor:pointer; }
.result-link-chip:hover { background:#e8f1ff; }
.execution-log-side { display:flex; align-items:center; }

.modal { position:fixed; inset:0; background:rgba(0,0,0,.5); display:flex; align-items:center; justify-content:center; z-index:1000; padding:20px; overflow-y:auto; }
.modal-content { background:white; border-radius:12px; padding:32px; width:90%; max-width:520px; animation:slideUp .3s ease; }
.modal-large { max-width:680px; }
.modal-content h3 { margin-bottom:20px; font-size:18px; font-weight:600; }
.modal-actions { display:flex; gap:12px; justify-content:flex-end; margin-top:20px; }
.run-pre-form { padding: 4px 0 8px; }
.run-pre-form .form-group { margin-bottom: 12px; }
.run-pre-form label { display:block; font-size:13px; color:#555; margin-bottom:6px; font-weight:500; }
.run-pre-form .form-select { width:100%; padding:8px 12px; border-radius:8px; border:1px solid var(--border,#ddd); font-size:13px; }
.ds-hint { margin-top:6px; font-size:12px; color:#1677ff; background:#e8f4ff; padding:4px 10px; border-radius:6px; }
.search-bar { margin-bottom:12px; }
.add-case-layout { display:flex; gap:12px; margin-bottom:10px; min-height:320px; }
.case-tree-panel { width:240px; border:1px solid var(--border); border-radius:8px; overflow:hidden; background:#fff; }
.case-tree-header { padding:8px 10px; font-size:12px; font-weight:600; color:var(--text-light); background:#f7f9fc; border-bottom:1px solid var(--border); }
.case-tree-body { max-height:280px; overflow:auto; }
.case-tree-row { line-height:30px; cursor:pointer; border-bottom:1px dashed #eef1f5; user-select:none; font-size:13px; }
.case-tree-row:last-child { border-bottom:none; }
.case-tree-row.active { background:#edf6ff; color:#0b5eb8; font-weight:600; }
.case-tree-toggle { display:inline-block; width:16px; }
.case-select-panel { flex:1; min-width:0; display:flex; flex-direction:column; }
.add-case-filters { display:flex; gap:10px; margin-bottom:12px; }
.filter-select-sm { border:1px solid var(--border); border-radius:6px; padding:7px 10px; font-size:13px; outline:none; min-width:140px; }
.search-input-sm { flex:1; border:1px solid var(--border); border-radius:6px; padding:7px 10px; font-size:13px; outline:none; }
.search-input-sm:focus, .filter-select-sm:focus { border-color:var(--accent); }
.available-cases { max-height:320px; overflow-y:auto; display:flex; flex-direction:column; gap:6px; }
.available-item { display:flex; align-items:center; gap:12px; padding:10px 14px; border:1px solid var(--border,#eee); border-radius:8px; cursor:pointer; transition:all .2s; }
.avail-info { display:flex; flex-direction:column; gap:4px; min-width:0; }
.avail-topline { display:flex; align-items:center; justify-content:space-between; gap:10px; }
.avail-name { font-weight:700; color:var(--text); }
.avail-type { display:inline-flex; padding:2px 8px; border-radius:999px; background:#eef3ff; color:#3556a8; font-size:11px; font-weight:700; }
.avail-endpoint { font-size:12px; color:var(--accent); }
.avail-meta { font-size:12px; color:var(--text-light); word-break:break-all; }
.available-item:hover { border-color:var(--accent); background:#f0f8ff; }
.available-item.selected { border-color:var(--accent); background:#e3f2fd; }
.avail-check { width:20px; height:20px; border-radius:50%; background:var(--accent); color:white; font-size:12px; display:flex; align-items:center; justify-content:center; flex-shrink:0; }
.selected-count { margin-top:10px; font-size:13px; color:var(--text-light); }
.loading-state,.success-state,.error-state { text-align:center; padding:24px; }
.spinner { width:40px; height:40px; border:4px solid var(--border); border-top-color:var(--accent); border-radius:50%; animation:spin 1s linear infinite; margin:0 auto 16px; }
.success-icon,.error-icon { width:52px; height:52px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:26px; margin:0 auto 12px; }
.success-icon { background:#27ae60; color:white; } .error-icon { background:#e74c3c; color:white; }
.empty-state { text-align:center; padding:32px; color:var(--text-light); }
@keyframes spin { to { transform:rotate(360deg); } }
@keyframes slideUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
</style>