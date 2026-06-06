<template>
  <div class="kv-editor">
    <div class="kv-title">
      <span>{{ title }}</span>
      <span v-if="hiddenCount" class="kv-hidden">
        <el-icon><Hide /></el-icon> 已隐藏 {{ hiddenCount }} 个
      </span>
    </div>
    <div class="kv-table">
      <div class="kv-row kv-head">
        <span class="kv-cell kv-check"></span>
        <span class="kv-cell kv-key">参数名</span>
        <span class="kv-eq"></span>
        <span class="kv-cell kv-val">参数值</span>
        <span class="kv-cell kv-type">类型</span>
        <span class="kv-cell kv-desc">说明</span>
        <span class="kv-cell kv-op"></span>
      </div>
      <div class="kv-row" v-for="(row, i) in rows" :key="i">
        <span class="kv-cell kv-check"><el-checkbox v-model="row.enabled" /></span>
        <span class="kv-cell kv-key">
          <el-input v-model="row.key" placeholder="参数名" size="small" />
        </span>
        <span class="kv-eq">=</span>
        <span class="kv-cell kv-val">
          <el-input v-model="row.value" :placeholder="valuePlaceholder" size="small" />
        </span>
        <span class="kv-cell kv-type">
          <el-select v-model="row.type" size="small">
            <el-option v-for="t in types" :key="t" :label="t" :value="t" />
          </el-select>
        </span>
        <span class="kv-cell kv-desc">
          <el-input v-model="row.desc" placeholder="说明" size="small" />
        </span>
        <span class="kv-cell kv-op">
          <el-icon class="kv-del" @click="remove(i)"><Remove /></el-icon>
        </span>
      </div>
      <div class="kv-add" @click="add">
        <el-icon><Plus /></el-icon> {{ addLabel }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { Plus, Remove, Hide } from '@element-plus/icons-vue'

const rows = defineModel({ type: Array, default: () => [] })

defineProps({
  title: { type: String, default: '参数' },
  valuePlaceholder: { type: String, default: '参数值' },
  addLabel: { type: String, default: '添加参数' },
  hiddenCount: { type: Number, default: 0 },
})

const types = ['string', 'integer', 'number', 'boolean', 'array', 'object', 'file']

const add = () => {
  rows.value.push({ enabled: true, key: '', value: '', type: 'string', desc: '' })
}
const remove = (i) => rows.value.splice(i, 1)
</script>

<style scoped lang="scss">
.kv-editor {
  padding: 6px 2px;
  min-height: 220px;
}
.kv-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 10px;
  .kv-hidden {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-weight: 400;
    font-size: 12px;
    color: var(--text-secondary);
  }
}
.kv-table {
  border: 1px solid var(--border-light);
  border-radius: 8px;
  overflow: hidden;
}
.kv-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border-bottom: 1px solid var(--border-light);
  &:last-child {
    border-bottom: none;
  }
}
.kv-head {
  background: #f7f8fb;
  font-size: 12px;
  color: var(--text-secondary);
  padding-top: 9px;
  padding-bottom: 9px;
}
.kv-cell {
  display: flex;
  align-items: center;
}
.kv-check {
  width: 28px;
  justify-content: center;
}
.kv-key,
.kv-val,
.kv-desc {
  flex: 1;
}
.kv-eq {
  color: var(--text-secondary);
  width: 12px;
  text-align: center;
}
.kv-type {
  width: 110px;
}
.kv-op {
  width: 36px;
  justify-content: center;
}
.kv-del {
  cursor: pointer;
  color: var(--text-secondary);
  &:hover {
    color: var(--danger);
  }
}
.kv-add {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 9px 12px;
  font-size: 13px;
  color: var(--brand-primary);
  cursor: pointer;
  background: #fff;
  &:hover {
    background: #f7f9ff;
  }
}
</style>
