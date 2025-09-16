import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { AuthStore, LoginRequest, RegisterRequest, User } from '@/types'
import { apiClient } from '@/lib/api'
import Cookies from 'js-cookie'
import toast from 'react-hot-toast'

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user })
      },

      setToken: (token: string | null) => {
        set({ token, isAuthenticated: !!token })
        if (token) {
          Cookies.set('auth_token', token, { expires: 7 })
        } else {
          Cookies.remove('auth_token')
        }
      },

      login: async (credentials: LoginRequest) => {
        try {
          set({ isLoading: true })
          const response = await apiClient.login(credentials)
          
          const { access_token } = response
          get().setToken(access_token)
          
          // Get user info
          const user = await apiClient.getCurrentUser()
          get().setUser(user)
          
          toast.success('Successfully logged in!')
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Login failed'
          toast.error(message)
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      register: async (data: RegisterRequest) => {
        try {
          set({ isLoading: true })
          const user = await apiClient.register(data)
          
          // Auto login after registration
          await get().login({ username: data.username, password: data.password })
          
          toast.success('Account created successfully!')
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registration failed'
          toast.error(message)
          throw error
        } finally {
          set({ isLoading: false })
        }
      },

      logout: () => {
        set({ user: null, token: null, isAuthenticated: false })
        Cookies.remove('auth_token')
        toast.success('Successfully logged out!')
      },
    }),
    {
      name: 'auth-store',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)