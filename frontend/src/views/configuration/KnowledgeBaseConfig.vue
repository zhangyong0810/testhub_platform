<template>
  <div class="kb-config-container">
    <div class="page-header">
      <h1>AI 评测师 - 知识库配置</h1>
      <p>连接本地知识库 jt-kb，使用业务知识回答问题</p>
    </div>

    <div class="config-content">
      <el-card class="config-card">
        <template #header>
          <div class="card-header">
            <span>知识库连接配置</span>
            <el-tag v-if="currentConfig" type="success">已配置</el-tag>
            <el-tag v-else type="info">未配置</el-tag>
          </div>
        </template>

        <el-form :model="form" :rules="rules" ref="configForm" label-width="140px">
          <el-form-item label="知识库 URL" prop="kb_url">
            <el-input
              v-model="form.kb_url"
              placeholder="http://127.0.0.1:5050"
              clearable
            >
              <template #prepend>
                <el-icon><DataBoard /></el-icon>
              </template>
            </el-input>
            <div class="form-tip">本地知识库 (jt-kb) 的 API 地址，默认端口 5050</div>
          </el-form-item>

          <el-form-item label="启用状态" prop="is_active">
            <el-switch v-model="form.is_active" />
            <span class="switch-label">{{ form.is_active ? '已启用' : '已禁用' }}</span>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="testConnection" :loading="testing">
              <el-icon><Connection /></el-icon>
              测试连接
            </el-button>
            <el-button type="success" @click="saveConfig" :loading="saving">
              <el-icon><Check /></el-icon>
              保存
            </el-button>
            <el-button @click="resetForm">
              <el-icon><RefreshLeft /></el-icon>
              重置
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <el-card class="info-card" v-if="currentConfig">
        <template #header>
          <span>当前配置</span>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="知识库 URL">
            {{ currentConfig.kb_url }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="currentConfig.is_active ? 'success' : 'info'">
              {{ currentConfig.is_active ? '已启用' : '已禁用' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentConfig.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDate(currentConfig.updated_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { DataBoard, Connection, Check, RefreshLeft } from '@element-plus/icons-vue'
import api from '@/utils/api'

const configForm = ref(null)
const currentConfig = ref(null)
const testing = ref(false)
const saving = ref(false)

const form = ref({
  kb_url: 'http://127.0.0.1:5050',
  is_active: true
})

const rules = computed(() => ({
  kb_url: [
    { required: true, message: '知识库URL是必填项', trigger: 'blur' },
    { type: 'url', message: '请输入有效的URL地址', trigger: 'blur' }
  ]
}))

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

const loadConfig = async () => {
  try {
    const response = await api.get('/assistant/config/')
    currentConfig.value = response.data
    form.value = {
      kb_url: response.data.kb_url || 'http://127.0.0.1:5050',
      is_active: response.data.is_active
    }
  } catch (error) {
    if (error.response?.status !== 404) {
      console.error('加载配置失败', error)
    }
  }
}

const testConnection = async () => {
  if (!configForm.value) return
  await configForm.value.validate(async (valid) => {
    if (!valid) return
    testing.value = true
    try {
      const response = await api.post('/assistant/config/test_connection/', {
        kb_url: form.value.kb_url
      })
      if (response.data.success) {
        ElMessage.success(response.data.message || '连接成功！')
      } else {
        ElMessage.error(response.data.error || '连接失败')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '连接失败')
    } finally {
      testing.value = false
    }
  })
}

const saveConfig = async () => {
  if (!configForm.value) return
  await configForm.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const dataToSave = {
        kb_url: form.value.kb_url,
        is_active: form.value.is_active
      }
      if (currentConfig.value) {
        await api.patch(`/assistant/config/${currentConfig.value.id}/`, dataToSave)
        ElMessage.success('配置更新成功')
      } else {
        await api.post('/assistant/config/', dataToSave)
        ElMessage.success('配置保存成功')
      }
      await loadConfig()
    } catch (error) {
      ElMessage.error(error.response?.data?.error || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const resetForm = () => {
  if (configForm.value) configForm.value.resetFields()
  if (currentConfig.value) {
    form.value = {
      kb_url: currentConfig.value.kb_url || 'http://127.0.0.1:5050',
      is_active: currentConfig.value.is_active
    }
  }
}

onMounted(() => { loadConfig() })
</script>

<style scoped>
.kb-config-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}
.page-header {
  text-align: center;
  margin-bottom: 30px;
}
.page-header h1 {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 10px;
}
.page-header p {
  color: #666;
  font-size: 1rem;
}
.config-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
.switch-label {
  margin-left: 10px;
  color: #606266;
}
</style>
