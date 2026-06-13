import request from './request'

export const authApi = {
  login: (data) => request.post('/auth/login', data),
  me: () => request.get('/auth/me'),
  uploadAvatar: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request.post('/auth/avatar', form)
  },
  loginRecords: (params) => request.get('/auth/login-records', { params }),
}

export const dashboardApi = {
  overview: () => request.get('/dashboard'),
}

export const projectApi = {
  list: () => request.get('/projects'),
  detail: (id) => request.get(`/projects/${id}`),
  create: (data) => request.post('/projects', data),
  update: (id, data) => request.put(`/projects/${id}`, data),
  remove: (id) => request.delete(`/projects/${id}`),
  // modules
  createModule: (id, data) => request.post(`/projects/${id}/modules`, data),
  updateModule: (id, moduleId, data) =>
    request.put(`/projects/${id}/modules/${moduleId}`, data),
  removeModule: (id, moduleId) =>
    request.delete(`/projects/${id}/modules/${moduleId}`),
  // members
  members: (id) => request.get(`/projects/${id}/members`),
  addMember: (id, data) => request.post(`/projects/${id}/members`, data),
  removeMember: (id, memberId) =>
    request.delete(`/projects/${id}/members/${memberId}`),
}

export const caseApi = {
  // API cases
  apiCases: (keyword) => request.get('/api-cases', { params: { keyword } }),
  createApiCase: (data) => request.post('/api-cases', data),
  updateApiCase: (id, data) => request.put(`/api-cases/${id}`, data),
  removeApiCase: (id) => request.delete(`/api-cases/${id}`),
  runApiCase: (data) => request.post('/api-cases/run', data),
  renameApiModule: (oldName, newName) =>
    request.put('/api-cases/module/rename', null, {
      params: { old_name: oldName, new_name: newName },
    }),
  removeApiModule: (name) =>
    request.delete(`/api-cases/module/${encodeURIComponent(name)}`),
  // UI cases
  uiCases: (keyword) => request.get('/ui-cases', { params: { keyword } }),
  createUiCase: (data) => request.post('/ui-cases', data),
  updateUiCase: (id, data) => request.put(`/ui-cases/${id}`, data),
  removeUiCase: (id) => request.delete(`/ui-cases/${id}`),
  runUiCase: (id) => request.post(`/ui-cases/${id}/run`),
  renameUiModule: (oldName, newName) =>
    request.put('/ui-cases/module/rename', null, {
      params: { old_name: oldName, new_name: newName },
    }),
  removeUiModule: (name) =>
    request.delete(`/ui-cases/module/${encodeURIComponent(name)}`),
}

export const planApi = {
  list: () => request.get('/test-plans'),
  create: (data) => request.post('/test-plans', data),
  remove: (id) => request.delete(`/test-plans/${id}`),
}
