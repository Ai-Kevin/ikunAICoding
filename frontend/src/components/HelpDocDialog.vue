<template>
  <el-dialog
    v-model="visible"
    title="帮助文档"
    width="860px"
    top="5vh"
    class="help-doc-dialog"
    destroy-on-close
    append-to-body
  >
    <div class="help-doc-body markdown-body" v-html="html" />
    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" @click="openSwagger">打开 API 文档</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import readmeRaw from '../../../README.md?raw'

const visible = defineModel({ type: Boolean, default: false })

marked.setOptions({
  gfm: true,
  breaks: true,
})

function prepareMarkdown(raw) {
  return raw
    .replace(/src="docs\//g, 'src="/docs/')
    .replace(/\]\(docs\//g, '](/docs/')
}

const html = computed(() => {
  const md = prepareMarkdown(readmeRaw)
  return marked.parse(md)
})

function openSwagger() {
  window.open('http://127.0.0.1:8010/docs', '_blank', 'noopener,noreferrer')
}
</script>

<style lang="scss">
.help-doc-dialog {
  .el-dialog__body {
    padding: 0 24px 8px;
    max-height: calc(90vh - 140px);
    overflow: hidden;
  }

  .help-doc-body {
    max-height: calc(90vh - 140px);
    overflow-y: auto;
    padding: 8px 4px 16px;
    scrollbar-width: thin;
  }
}

.markdown-body {
  color: var(--text-regular);
  font-size: 14px;
  line-height: 1.65;
  letter-spacing: -0.01em;

  > div[align='center'] {
    text-align: center;
    margin-bottom: 8px;
  }

  h1,
  h2,
  h3,
  h4 {
    color: var(--text-main);
    font-weight: 700;
    letter-spacing: -0.02em;
    margin: 1.4em 0 0.6em;
    line-height: 1.35;

    &:first-child {
      margin-top: 0;
    }
  }

  h1 {
    font-size: 1.65rem;
    background: linear-gradient(90deg, #007aff, #5856d6);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
  }

  h2 {
    font-size: 1.15rem;
    padding-bottom: 6px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.55);
  }

  h3 {
    font-size: 1rem;
  }

  p {
    margin: 0.65em 0;
  }

  strong {
    color: var(--text-main);
    font-weight: 600;
  }

  hr {
    border: none;
    height: 1px;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.65),
      transparent
    );
    margin: 1.5em 0;
  }

  a {
    color: var(--brand-primary);
    text-decoration: none;
    font-weight: 500;

    &:hover {
      text-decoration: underline;
    }
  }

  img {
    max-width: 100%;
    border-radius: var(--glass-radius);
    border: 1px solid rgba(255, 255, 255, 0.65);
    box-shadow: var(--glass-shadow);
    margin: 8px 0;
  }

  ul,
  ol {
    padding-left: 1.4em;
    margin: 0.6em 0;
  }

  li {
    margin: 0.35em 0;
  }

  li > p {
    margin: 0.2em 0;
  }

  blockquote {
    margin: 1em 0;
    padding: 10px 14px;
    border-left: 3px solid var(--brand-primary);
    background: rgba(0, 122, 255, 0.06);
    border-radius: 0 var(--glass-radius-sm) var(--glass-radius-sm) 0;
    color: var(--text-secondary);
  }

  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 1em 0;
    font-size: 13px;
    border-radius: var(--glass-radius-sm);
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.55);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.6);
  }

  thead th {
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(12px);
    font-weight: 600;
    color: var(--text-secondary);
    text-align: left;
    padding: 10px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.5);
  }

  tbody td {
    padding: 9px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.35);
    vertical-align: top;
  }

  tbody tr:last-child td {
    border-bottom: none;
  }

  tbody tr:hover td {
    background: rgba(255, 255, 255, 0.28);
  }

  code {
    font-family: 'Cascadia Code', 'Fira Code', Consolas, monospace;
    font-size: 0.88em;
    padding: 2px 6px;
    border-radius: 6px;
    background: rgba(255, 255, 255, 0.55);
    border: 1px solid rgba(255, 255, 255, 0.65);
    color: #c93400;
  }

  pre {
    margin: 1em 0;
    padding: 14px 16px;
    border-radius: var(--glass-radius-sm);
    background: rgba(15, 23, 42, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.1);
    overflow-x: auto;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);

    code {
      padding: 0;
      border: none;
      background: transparent;
      color: #e2e8f0;
      font-size: 12.5px;
      line-height: 1.6;
    }
  }

  img[src*='shields.io'],
  img[src*='badge'] {
    display: inline-block;
    vertical-align: middle;
    border: none;
    box-shadow: none;
    border-radius: 4px;
    margin: 2px 3px;
    max-height: 22px;
  }
}
</style>
