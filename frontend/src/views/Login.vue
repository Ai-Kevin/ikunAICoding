<template>
  <div class="login-page">
    <!-- Left hero panel -->
    <div class="login-hero">
      <div class="hero-logo brand-logo">
        <div class="logo-mark">A</div>
        <div class="logo-text">
          <div class="logo-title" style="color: #fff">
            AutoTest <span style="color: #6ea8ff">Pro</span>
          </div>
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
          <div class="infinity">
            <svg viewBox="0 0 200 100" width="260" height="130">
              <defs>
                <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stop-color="#3a7bff" />
                  <stop offset="100%" stop-color="#7db0ff" />
                </linearGradient>
              </defs>
              <path
                d="M50 50 C50 25 90 25 100 50 C110 75 150 75 150 50 C150 25 110 25 100 50 C90 75 50 75 50 50 Z"
                fill="none"
                stroke="url(#g1)"
                stroke-width="14"
                stroke-linecap="round"
              />
            </svg>
          </div>
        </div>

        <div class="hero-features">
          <div class="feature" v-for="f in features" :key="f.title">
            <el-icon :size="22"><component :is="f.icon" /></el-icon>
            <div class="f-title">{{ f.title }}</div>
            <div class="f-sub">{{ f.sub }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Right form panel -->
    <div class="login-form-wrap">
      <div class="login-card">
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
            <a class="link">忘记密码？</a>
          </div>

          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="onSubmit"
          >
            登录
          </el-button>
        </el-form>

        <div class="divider"><span>其他登录方式</span></div>

        <div class="social-login">
          <div class="social-btn">
            <el-icon color="#07c160"><ChatDotRound /></el-icon> 企业微信
          </div>
          <div class="social-btn">
            <el-icon color="#fc6d26"><Platform /></el-icon> GitLab
          </div>
          <div class="social-btn">
            <el-icon color="#00a4ef"><Grid /></el-icon> LDAP / AD
          </div>
        </div>

        <div class="register-tip">
          还没有账号？<a class="link">立即注册</a>
        </div>

        <div class="demo-tip">演示账号：admin / admin123</div>
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
}

.login-hero {
  flex: 1.15;
  position: relative;
  background: radial-gradient(
      circle at 70% 20%,
      #1b3a8c 0%,
      transparent 55%
    ),
    linear-gradient(135deg, #0a1d4a 0%, #0d265e 55%, #0a1c45 100%);
  color: #fff;
  padding: 48px 64px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.hero-logo {
  margin-bottom: 36px;
}

.hero-content {
  margin-top: 24px;
  h1 {
    font-size: 40px;
    line-height: 1.3;
    font-weight: 800;
    margin: 0 0 18px;
    .highlight {
      background: linear-gradient(90deg, #4f8bff, #8fb6ff);
      -webkit-background-clip: text;
      background-clip: text;
      color: transparent;
    }
  }
  .hero-desc {
    font-size: 16px;
    color: #aebfe0;
    margin: 0;
  }
}

.hero-illustration {
  margin: 30px 0 50px;
  display: flex;
  justify-content: center;
  .infinity {
    filter: drop-shadow(0 18px 40px rgba(58, 123, 255, 0.45));
  }
}

.hero-features {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 18px;
  margin-top: auto;
  .feature {
    .el-icon {
      color: #5d92ff;
      margin-bottom: 8px;
    }
    .f-title {
      font-size: 14px;
      font-weight: 700;
    }
    .f-sub {
      font-size: 12px;
      color: #93a4c8;
      margin-top: 2px;
    }
  }
}

.login-form-wrap {
  flex: 1;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
}

.login-card {
  width: 100%;
  max-width: 380px;
  h2 {
    font-size: 26px;
    font-weight: 800;
    margin: 0 0 8px;
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

.link {
  color: var(--brand-primary);
  cursor: pointer;
  font-size: 14px;
}

.login-btn {
  width: 100%;
  height: 46px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.divider {
  text-align: center;
  position: relative;
  margin: 26px 0 20px;
  color: var(--text-secondary);
  font-size: 13px;
  &::before,
  &::after {
    content: '';
    position: absolute;
    top: 50%;
    width: 32%;
    height: 1px;
    background: var(--border-light);
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
  gap: 12px;
  .social-btn {
    border: 1px solid var(--border-light);
    border-radius: 8px;
    height: 50px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 2px;
    font-size: 12px;
    color: var(--text-regular);
    cursor: pointer;
    transition: all 0.2s;
    &:hover {
      border-color: var(--brand-primary);
      color: var(--brand-primary);
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
  color: #b3b9c7;
  background: #f7f8fb;
  padding: 8px;
  border-radius: 6px;
}

.copyright {
  position: absolute;
  bottom: 24px;
  font-size: 12px;
  color: #b3b9c7;
}

@media (max-width: 900px) {
  .login-hero {
    display: none;
  }
}
</style>
