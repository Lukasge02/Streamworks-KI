import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import LoginPage from '../app/login/page'

// Mock useRouter
const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
    useRouter: () => ({
        push: mockPush,
    }),
}))

describe('LoginPage', () => {
    beforeEach(() => {
        mockPush.mockClear()
    })

    it('renders login form', () => {
        render(<LoginPage />)
        expect(screen.getByRole('heading', { name: /Willkommen zurück/i })).toBeInTheDocument()
        expect(screen.getByLabelText(/Email/i)).toBeInTheDocument()
        expect(screen.getByLabelText(/Passwort/i)).toBeInTheDocument()
        expect(screen.getByRole('button', { name: /Anmelden/i })).toBeInTheDocument()
    })

    it('allows user input and submits form', async () => {
        render(<LoginPage />)

        const emailInput = screen.getByLabelText(/Email/i)
        const passwordInput = screen.getByLabelText(/Passwort/i)
        const submitButton = screen.getByRole('button', { name: /Anmelden/i })

        // Simulate user typing
        fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
        fireEvent.change(passwordInput, { target: { value: 'password123' } })

        expect(emailInput).toHaveValue('test@example.com')
        expect(passwordInput).toHaveValue('password123')

        // Submit form
        fireEvent.click(submitButton)

        // Check loading state (optional, but good)
        // Check loading state (optional, but good)
        await waitFor(() => {
            expect(submitButton).toBeDisabled()
        })

        // Wait for redirect
        await waitFor(() => {
            expect(mockPush).toHaveBeenCalledWith('/testing')
        }, { timeout: 2000 })
    })
})
