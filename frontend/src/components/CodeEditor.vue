<template>
  <div class="code-editor">
    <div class="ce-gutter" ref="gutterRef">
      <div v-for="n in lineCount" :key="n" class="ce-ln">{{ n }}</div>
    </div>
    <div class="ce-area">
      <pre class="ce-highlight" ref="preRef"><code v-html="highlighted"></code></pre>
      <textarea
        ref="taRef"
        v-model="content"
        class="ce-input"
        spellcheck="false"
        :placeholder="placeholder"
        @scroll="syncScroll"
        @keydown.tab.prevent="onTab"
      ></textarea>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const content = defineModel({ type: String, default: '' })

const props = defineProps({
  placeholder: { type: String, default: '' },
  language: { type: String, default: 'json' },
})

const taRef = ref()
const gutterRef = ref()
const preRef = ref()

const lineCount = computed(() => Math.max(1, content.value.split('\n').length))

const escapeHtml = (s) =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const highlightJson = (code) => {
  const tokenRe =
    /("(?:\\.|[^"\\])*")(\s*:)?|\b(true|false|null)\b|(-?\d+\.?\d*(?:[eE][+-]?\d+)?)/g
  let result = ''
  let lastIndex = 0
  let m
  while ((m = tokenRe.exec(code))) {
    result += escapeHtml(code.slice(lastIndex, m.index))
    if (m[1] !== undefined) {
      const isKey = !!m[2]
      result += `<span class="${isKey ? 'tok-key' : 'tok-str'}">${escapeHtml(m[1])}</span>`
      if (m[2]) result += `<span class="tok-punc">${escapeHtml(m[2])}</span>`
    } else if (m[3] !== undefined) {
      result += `<span class="tok-bool">${escapeHtml(m[3])}</span>`
    } else if (m[4] !== undefined) {
      result += `<span class="tok-num">${escapeHtml(m[4])}</span>`
    }
    lastIndex = tokenRe.lastIndex
  }
  result += escapeHtml(code.slice(lastIndex))
  return result
}

const highlighted = computed(() => {
  const code = content.value
  const html =
    props.language === 'json' ? highlightJson(code) : escapeHtml(code)
  // keep highlight layer height in sync with the textarea's trailing newline
  return code.endsWith('\n') ? html + '\n' : html
})

const syncScroll = () => {
  if (taRef.value) {
    if (gutterRef.value) gutterRef.value.scrollTop = taRef.value.scrollTop
    if (preRef.value) {
      preRef.value.scrollTop = taRef.value.scrollTop
      preRef.value.scrollLeft = taRef.value.scrollLeft
    }
  }
}

const onTab = (e) => {
  const el = e.target
  const start = el.selectionStart
  const end = el.selectionEnd
  content.value = content.value.slice(0, start) + '  ' + content.value.slice(end)
  requestAnimationFrame(() => {
    el.selectionStart = el.selectionEnd = start + 2
  })
}
</script>

<style scoped lang="scss">
.code-editor {
  display: flex;
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  overflow: hidden;
  height: 240px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
}
.ce-gutter {
  flex-shrink: 0;
  padding: 12px 8px 12px 12px;
  text-align: right;
  color: #b3b9c7;
  background: #f7f8fb;
  border-right: 1px solid var(--border-light);
  overflow: hidden;
  user-select: none;
  min-width: 44px;
}
.ce-ln {
  height: 1.6em;
}
.ce-area {
  position: relative;
  flex: 1;
  overflow: hidden;
}
.ce-highlight,
.ce-input {
  margin: 0;
  padding: 12px 14px;
  font-family: inherit;
  font-size: inherit;
  line-height: 1.6;
  white-space: pre;
  tab-size: 2;
  border: none;
}
.ce-highlight {
  position: absolute;
  inset: 0;
  overflow: auto;
  pointer-events: none;
  color: #24292e;
  code {
    font-family: inherit;
  }
}
.ce-input {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  resize: none;
  outline: none;
  background: transparent;
  color: transparent;
  caret-color: #24292e;
  overflow: auto;
  &::placeholder {
    color: #b3b9c7;
  }
}

// JSON syntax token colors
.ce-highlight :deep(.tok-key) {
  color: #24292e;
  font-weight: 600;
}
.ce-highlight :deep(.tok-str) {
  color: #16a34a;
}
.ce-highlight :deep(.tok-num) {
  color: #c2410c;
}
.ce-highlight :deep(.tok-bool) {
  color: #2f6bff;
}
.ce-highlight :deep(.tok-punc) {
  color: #6b7280;
}
</style>
