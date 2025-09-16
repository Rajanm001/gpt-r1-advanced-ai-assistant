import axios, { AxiosInstance, AxiosRequestConfig } from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: `${API_BASE_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          Cookies.remove('auth_token')
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async login(credentials: { username: string; password: string }) {
    const formData = new FormData()
    formData.append('username', credentials.username)
    formData.append('password', credentials.password)
    
    const response = await this.client.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  }

  async register(data: { username: string; email: string; password: string }) {
    const response = await this.client.post('/auth/register', data)
    return response.data
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me')
    return response.data
  }

  // Conversation endpoints
  async getConversations() {
    const response = await this.client.get('/conversations')
    return response.data
  }

  async getConversation(id: number) {
    const response = await this.client.get(`/conversations/${id}`)
    return response.data
  }

  async createConversation(title?: string) {
    const response = await this.client.post('/conversations', { title })
    return response.data
  }

  async updateConversationTitle(id: number, title: string) {
    const response = await this.client.put(`/conversations/${id}/title`, { title })
    return response.data
  }

  // Chat endpoints
  async sendMessage(data: {
    message: string
    conversation_id?: number
    use_rag?: boolean
  }) {
    const response = await this.client.post('/chat/simple', data)
    return response.data
  }

  // Streaming chat
  createChatStream(data: {
    message: string
    conversation_id?: number
    use_rag?: boolean
  }) {
    const token = Cookies.get('auth_token')
    const url = new URL(`${API_BASE_URL}/api/v1/chat`)
    
    return fetch(url.toString(), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify(data),
    })
  }
}

export const apiClient = new ApiClient()
export default apiClient