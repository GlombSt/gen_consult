import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders welcome message', () => {
    render(<App />)
    const heading = screen.getByRole('heading', { name: /welcome to react/i })
    expect(heading).toBeInTheDocument()
  })

  it('renders the start editing message', () => {
    render(<App />)
    const message = screen.getByText(/start editing this file to see changes in real-time/i)
    expect(message).toBeInTheDocument()
  })
})
