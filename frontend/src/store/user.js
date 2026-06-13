import { defineStore } from 'pinia'
import { authApi } from '@/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('user') || 'null'),
    avatarVersion: 0,
  }),
  getters: {
    isLoggedIn: (state) => !!state.token,
    avatarUrl: (state) => {
      const avatar = state.user?.avatar
      if (!avatar) return ''
      const joiner = avatar.includes('?') ? '&' : '?'
      return `${avatar}${joiner}v=${state.avatarVersion}`
    },
  },
  actions: {
    async login(payload) {
      const res = await authApi.login(payload)
      this.token = res.token
      this.user = res.user
      localStorage.setItem('token', res.token)
      localStorage.setItem('user', JSON.stringify(res.user))
      if (res.session_id) {
        localStorage.setItem('session_id', res.session_id)
      }
      return res
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('session_id')
    },
    setUser(user) {
      this.user = user
      this.avatarVersion += 1
      localStorage.setItem('user', JSON.stringify(user))
    },
  },
})
