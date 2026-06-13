<template>
  <div class="login-page">
    <!-- Left hero panel -->
    <div class="login-hero glass-panel">
      <div class="hero-logo brand-logo">
        <img src="/logo.png?v=2" alt="AutoTest Pro" class="logo-mark" />
        <div class="logo-text">
          <div class="logo-title">AutoTest <span class="pro">Pro</span></div>
          <div class="logo-sub">自动化测试平台</div>
        </div>
      </div>

      <div class="hero-content">
        <h1>
          一站式 API、UI、性能<br />
          <span class="highlight">自动化测试平台</span>
        </h1>
        <p class="hero-desc">从用例管理到持续集成，全流程质量保障</p>

        <div class="hero-illustration">
          <div class="infinity-ring">
            <svg viewBox="0 0 200 100" width="260" height="130">
              <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#007AFF" />
                  <stop offset="50%" stop-color="#5856D6" />
                  <stop offset="100%" stop-color="#AF52DE" />
                </linearGradient>
              </defs>
              <path
                d="M50 50 C50 25 90 25 100 50 C110 75 150 75 150 50 C150 25 110 25 100 50 C90 75 50 75 50 50 Z"
                fill="none"
                stroke="url(#g1)"
                stroke-width="12"
                stroke-linecap="round"
              />
            </svg>
          </div>
        </div>

        <div class="hero-features">
          <div class="feature glass-chip" v-for="f in features" :key="f.title">
            <el-icon :size="20"><component :is="f.icon" /></el-icon>
            <div class="f-title">{{ f.title }}</div>
            <div class="f-sub">{{ f.sub }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="login-form-wrap">
      <div class="login-card glass-panel-strong">
        <h2>欢迎登录</h2>
        <p class="card-sub">登录您的账号以继续使用 AutoTest Pro</p>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          @submit.prevent="onSubmit"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="用户名 / 邮箱"
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              show-password
              placeholder="密码"
              :prefix-icon="Lock"
              @keyup.enter="onSubmit"
            />
          </el-form-item>

          <div class="form-row">
            <el-checkbox v-model="form.remember">记住我</el-checkbox>
            <a class="link-primary">忘记密码？</a>
          </div>

          <el-button
            type="primary"
            round
            class="login-btn"
            :loading="loading"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form>

        <div class="divider"><span>其他登录方式</span></div>

        <div class="social-login">
          <div class="social-btn glass-chip" v-for="s in socials" :key="s.label">
            <el-icon :color="s.color"><component :is="s.icon" /></el-icon>
            <span>{{ s.label }}</span>
          </div>
        </div>

        <div class="register-tip">
          还没有账号？<a class="link-primary">立即注册</a>
        </div>

        <div class="demo-tip glass-chip">演示账号：admin / admin123</div>
      </div>

      <div class="copyright">
        © 2024 AutoTest Pro 自动化测试平台. All rights reserved.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  User,
  Lock,
  ChatDotRound,
  Platform,
  Grid,
  Aim,
  Promotion,
  DataAnalysis,
  Lock as LockIcon,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: 'admin',
  password: 'admin123',
  remember: true,
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const features = [
  { icon: Aim, title: '全面覆盖', sub: 'API / UI / 性能' },
  { icon: Promotion, title: '高效执行', sub: '并行分布式执行' },
  { icon: DataAnalysis, title: '智能分析', sub: '多维度数据统计' },
  { icon: LockIcon, title: '稳定可靠', sub: '企业级安全保障' },
]

const socials = [
  { icon: ChatDotRound, label: '企业微信', color: '#07c160' },
  { icon: Platform, label: 'GitLab', color: '#fc6d26' },
  { icon: Grid, label: 'LDAP / AD', color: '#007AFF' },
]

const onSubmit = async () => {
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await userStore.login({
        username: form.username,
        password: form.password,
      })
      ElMessage.success('登录成功')
      router.push('/dashboard')
    } catch (e) {
      // handled by interceptor
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped lang="scss">
.login-page {
  display: flex;
  height: 100vh;
  width: 100%;
  padding: 20px;
  gap: 20px;
  align-items: stretch;
}

.glass-panel,
.glass-panel-strong {
  position: relative;
  background: rgba(255, 255, 255, 0.55);
  backdrop-filter: blur(36px) saturate(200%);
  -webkit-backdrop-filter: blur(36px) saturate(200%);
  border: 1px solid rgba(255, 255, 255, 0.82);
  box-shadow: var(--glass-shadow-lg);

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    border-radius: inherit;
    padding: 1px;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.95) 0%,
      rgba(255, 255, 255, 0.3) 50%,
      rgba(255, 255, 255, 0.7) 100%
    );
    -webkit-mask:
      linear-gradient(#fff 0 0) content-box,
      linear-gradient(#fff 0 0);
    -webkit-mask-composite: xor;
    mask-composite: exclude;
    pointer-events: none;
  }
}

.glass-panel-strong {
  background: rgba(255, 255, 255, 0.62);
  backdrop-filter: blur(40px) saturate(200%);
  -webkit-backdrop-filter: blur(40px) saturate(200%);
}

.glass-chip {
  background: rgba(255, 255, 255, 0.35);
  backdrop-filter: blur(16px) saturate(160%);
  -webkit-backdrop-filter: blur(16px) saturate(160%);
  border: 1px solid rgba(255, 255, 255, 0.55);
  border-radius: var(--glass-radius-sm);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.login-hero {
  flex: 1.2;
  border-radius: var(--glass-radius-xl);
  color: var(--text-main);
  padding: 48px 56px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.hero-logo {
  margin-bottom: 36px;
}

.hero-content {
  margin-top: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;

  h1 {
    font-size: 38px;
    line-height: 1.25;
    font-weight: 700;
    margin: 0 0 16px;
    letter-spacing: -0.03em;

    .highlight {
      background: linear-gradient(90deg, #007aff, #5856d6, #af52de);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
  }

  .hero-desc {
    font-size: 15px;
    color: var(--text-secondary);
    margin: 0;
  }
}

.hero-illustration {
  margin: 36px 0 40px;
  display: flex;
  justify-content: center;

  .infinity-ring {
    filter: drop-shadow(0 12px 32px rgba(0, 122, 255, 0.25));
    animation: ring-pulse 4s ease-in-out infinite;
  }
}

@keyframes ring-pulse {
  0%,
  100% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.03);
    opacity: 0.9;
  }
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
  margin-top: auto;

  .feature {
    padding: 16px 14px;
    cursor: default;
    transition:
      background 0.28s ease,
      border-color 0.28s ease,
      box-shadow 0.28s ease,
      transform 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      backdrop-filter 0.28s ease;

    &:hover {
      background: rgba(255, 255, 255, 0.68);
      backdrop-filter: blur(24px) saturate(210%);
      -webkit-backdrop-filter: blur(24px) saturate(210%);
      border-color: rgba(255, 255, 255, 0.92);
      transform: translateY(-2px);
      box-shadow:
        0 8px 24px rgba(0, 122, 255, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }

    .el-icon {
      color: var(--brand-primary);
      margin-bottom: 8px;
    }
    .f-title {
      font-size: 13px;
      font-weight: 600;
      letter-spacing: -0.01em;
    }
    .f-sub {
      font-size: 11px;
      color: var(--text-secondary);
      margin-top: 3px;
    }
  }
}

.login-form-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.login-card {
  width: 100%;
  max-width: 400px;
  padding: 36px 32px;
  border-radius: var(--glass-radius-xl);

  h2 {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 8px;
    letter-spacing: -0.03em;
  }
  .card-sub {
    color: var(--text-secondary);
    font-size: 14px;
    margin: 0 0 28px;
  }
}

.form-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.divider {
  text-align: center;
  position: relative;
  margin: 26px 0 20px;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;

  &::before,
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 32%;
    height: 1px;
    background: rgba(255, 255, 255, 0.55);
  }
  &::before {
    left: 0;
  }
  &::after {
    right: 0;
  }
}

.social-login {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;

  .social-btn {
    position: relative;
    overflow: hidden;
    height: 64px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    font-size: 11px;
    color: var(--text-regular);
    cursor: pointer;
    border: 1px solid transparent;
    transition:
      background 0.28s ease,
      border-color 0.28s ease,
      box-shadow 0.28s ease,
      transform 0.28s cubic-bezier(0.25, 0.46, 0.45, 0.94),
      backdrop-filter 0.28s ease,
      color 0.28s ease;

    &::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: inherit;
      background: linear-gradient(
        135deg,
        rgba(255, 255, 255, 0.5) 0%,
        transparent 60%
      );
      opacity: 0;
      transition: opacity 0.28s ease;
      pointer-events: none;
    }

    &:hover {
      background: rgba(255, 255, 255, 0.78);
      backdrop-filter: blur(24px) saturate(220%);
      -webkit-backdrop-filter: blur(24px) saturate(220%);
      border-color: rgba(255, 255, 255, 0.92);
      color: var(--brand-primary);
      transform: translateY(-3px);
      box-shadow:
        0 10px 28px rgba(0, 122, 255, 0.14),
        inset 0 1px 0 rgba(255, 255, 255, 1);

      &::after {
        opacity: 1;
      }
    }

    &:active {
      transform: translateY(-1px);
    }
  }
}

.register-tip {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--text-secondary);
}

.demo-tip {
  text-align: center;
  margin-top: 14px;
  font-size: 12px;
  color: var(--text-secondary);
  padding: 10px 14px;
}

.copyright {
  position: absolute;
  bottom: 8px;
  font-size: 11px;
  color: var(--text-tertiary);
}

@media (max-width: 900px) {
  .login-hero {
    display: none;
  }
  .login-page {
    justify-content: center;
  }
}
</style>
